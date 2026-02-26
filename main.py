from fastapi import FastAPI
from urllib.parse import quote_plus
import nodriver as nd
import undetected_chromedriver as uc
import asyncio
import random
import time

app = FastAPI()

# ──────────────────────────────────────────────
# Methode 1 : nodriver (async, CDP direct)
# ──────────────────────────────────────────────

async def scrape_with_nodriver(q: str) -> list:
    print(f"[PAA][nodriver] Trying nodriver for q={q}")
    browser = None
    try:
        browser = await nd.start(
            headless=False,
            browser_args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--window-size=1280,800",
            ],
            lang="fr-FR",
        )
        print("[PAA][nodriver] Browser started")

        tab = await browser.get("about:blank")

        # Cookie SOCS pour bypass consent Google
        await tab.send(nd.cdp.network.set_cookie(
            name="SOCS",
            value="CAESEwgDEg9yZW1vdGVfY29uc2VudBgB",
            domain=".google.com",
            path="/",
        ))
        print("[PAA][nodriver] SOCS cookie set via CDP")

        url = f"https://www.google.com/search?q={quote_plus(q)}&hl=fr"
        print(f"[PAA][nodriver] Navigating to {url}")
        tab = await browser.get(url)
        await tab.sleep(random.uniform(1.5, 4.0))

        title = tab.target.title if tab.target else "N/A"
        print(f"[PAA][nodriver] Page title: {title}")

        # Extraction PAA via JavaScript (3 strategies en une)
        results = await tab.evaluate("""
            (() => {
                // Strategy 1: related-question-pair with data-q attribute
                let r = Array.from(document.querySelectorAll('div.related-question-pair'))
                    .map(el => el.getAttribute('data-q')).filter(q => q);
                if (r.length) return r;
                // Strategy 2: data-sgrd container with role="button"
                r = Array.from(document.querySelectorAll('div[data-sgrd="true"] div[role="button"]'))
                    .map(el => el.innerText.trim()).filter(t => t.includes('?'));
                if (r.length) return r;
                // Strategy 3: any div[role="button"] containing "?"
                return Array.from(document.querySelectorAll('div[role="button"]'))
                    .map(el => el.innerText.trim())
                    .filter(t => t.includes('?') && t.length > 10 && t.length < 200);
            })()
        """)

        results = results if isinstance(results, list) else []
        print(f"[PAA][nodriver] Got {len(results)} results")
        return results

    except Exception as e:
        print(f"[PAA][nodriver] Failed: {e}")
        return []
    finally:
        if browser:
            try:
                browser.stop()
            except Exception:
                pass


# ──────────────────────────────────────────────
# Methode 2 : undetected-chromedriver (fallback)
# ──────────────────────────────────────────────

def scrape_with_uc(q: str) -> list:
    print(f"[PAA][uc] Fallback to undetected-chromedriver for q={q}")
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,800")
    options.add_argument("--lang=fr-FR")

    driver = uc.Chrome(options=options, headless=True, use_subprocess=True)
    print("[PAA][uc] Browser started")

    try:
        # Cookie SOCS via CDP
        driver.execute_cdp_cmd('Network.setCookie', {
            'name': 'SOCS',
            'value': 'CAESEwgDEg9yZW1vdGVfY29uc2VudBgB',
            'domain': '.google.com',
            'path': '/'
        })
        print("[PAA][uc] SOCS cookie set via CDP")

        url = f"https://www.google.com/search?q={quote_plus(q)}&hl=fr"
        print(f"[PAA][uc] Navigating to {url}")
        driver.get(url)
        time.sleep(random.uniform(1.5, 4.0))

        title = driver.title
        print(f"[PAA][uc] Page title: {title}")

        # Meme 3 strategies via execute_script
        results = driver.execute_script("""
            // Strategy 1: related-question-pair with data-q attribute
            let r = Array.from(document.querySelectorAll('div.related-question-pair'))
                .map(el => el.getAttribute('data-q')).filter(q => q);
            if (r.length) return r;
            // Strategy 2: data-sgrd container with role="button"
            r = Array.from(document.querySelectorAll('div[data-sgrd="true"] div[role="button"]'))
                .map(el => el.innerText.trim()).filter(t => t.includes('?'));
            if (r.length) return r;
            // Strategy 3: any div[role="button"] containing "?"
            return Array.from(document.querySelectorAll('div[role="button"]'))
                .map(el => el.innerText.trim())
                .filter(t => t.includes('?') && t.length > 10 && t.length < 200);
        """)

        results = results if isinstance(results, list) else []
        print(f"[PAA][uc] Got {len(results)} results")

        if not results:
            snippet = driver.page_source[:500]
            print(f"[PAA][uc] HTML snippet: {snippet}")

        return results

    except Exception as e:
        print(f"[PAA][uc] Failed: {e}")
        return []
    finally:
        driver.quit()


# ──────────────────────────────────────────────
# Endpoint
# ──────────────────────────────────────────────

@app.get("/paa")
async def get_paa(q: str):
    print(f"[PAA] New request: q={q}")

    # 1. Essayer nodriver (async, CDP direct)
    results = await scrape_with_nodriver(q)

    # 2. Fallback: undetected-chromedriver (Selenium)
    if not results:
        print("[PAA] nodriver returned nothing, falling back to uc")
        results = await asyncio.to_thread(scrape_with_uc, q)

    print(f"[PAA] Done. Returning {len(results)} questions")
    return {"query": q, "paa": list(set(results))}
