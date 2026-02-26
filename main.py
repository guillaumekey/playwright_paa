from fastapi import FastAPI
from patchright.async_api import async_playwright
from urllib.parse import quote_plus
import random

app = FastAPI()

@app.get("/paa")
async def get_paa(q: str):
    print(f"[PAA] New request: q={q}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            channel="chrome",
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ]
        )
        print("[PAA] Browser opened (Patchright + Chrome)")

        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="fr-FR",
        )
        await context.add_cookies([{
            'name': 'SOCS',
            'value': 'CAESEwgDEg9yZW1vdGVfY29uc2VudBgB',
            'domain': '.google.com',
            'path': '/'
        }])
        print("[PAA] SOCS cookie set")

        page = await context.new_page()
        url = f"https://www.google.com/search?q={quote_plus(q)}&hl=fr"
        print(f"[PAA] Navigating to {url}")
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(random.randint(1500, 4000))

        title = await page.title()
        print(f"[PAA] Page title: {title}")

        results = []

        # Strategy 1: related-question-pair with data-q attribute
        try:
            await page.wait_for_selector('div.related-question-pair', timeout=5000)
            results = await page.eval_on_selector_all(
                'div.related-question-pair',
                'elements => elements.map(el => el.getAttribute("data-q")).filter(q => q)'
            )
            print(f"[PAA] Strategy 1 (related-question-pair): {len(results)} results")
        except Exception:
            print("[PAA] Strategy 1 (related-question-pair): not found")

        # Strategy 2: data-sgrd container with role="button"
        if not results:
            try:
                await page.wait_for_selector('div[data-sgrd="true"]', timeout=3000)
                results = await page.eval_on_selector_all(
                    'div[data-sgrd="true"] div[role="button"]',
                    'elements => elements.map(el => el.innerText.trim()).filter(t => t.includes("?"))'
                )
                print(f"[PAA] Strategy 2 (data-sgrd): {len(results)} results")
            except Exception:
                print("[PAA] Strategy 2 (data-sgrd): not found")

        # Strategy 3: any div[role="button"] containing "?"
        if not results:
            try:
                results = await page.eval_on_selector_all(
                    'div[role="button"]',
                    'elements => elements.map(el => el.innerText.trim()).filter(t => t.includes("?") && t.length > 10 && t.length < 200)'
                )
                print(f"[PAA] Strategy 3 (role=button fallback): {len(results)} results")
            except Exception:
                print("[PAA] Strategy 3 (role=button fallback): failed")

        # If all strategies failed, dump diagnostic info
        if not results:
            snippet = await page.content()
            print(f"[PAA] ALL STRATEGIES FAILED. HTML snippet: {snippet[:500]}")

        await context.close()
        await browser.close()
        print(f"[PAA] Done. Returning {len(results)} questions")
        return {"query": q, "paa": list(set(results))}
