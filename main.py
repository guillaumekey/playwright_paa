from fastapi import FastAPI
from playwright.async_api import async_playwright
from urllib.parse import quote_plus

app = FastAPI()

@app.get("/paa")
async def get_paa(q: str):
    print(f"[PAA] New request: q={q}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        print("[PAA] Browser opened")
        page = await browser.new_page()
        url = f"https://www.google.com/search?q={quote_plus(q)}&hl=fr"
        print(f"[PAA] Navigating to {url}")
        await page.goto(url, wait_until="domcontentloaded")
        print("[PAA] Page loaded")

        # Handle Google cookie consent dialog if present (reject all)
        try:
            reject_btn = page.locator('button', has_text='Tout refuser')
            await reject_btn.click(timeout=3000)
            print("[PAA] Cookie consent dismissed (Tout refuser)")
        except Exception:
            print("[PAA] No cookie consent dialog found, skipping")

        try:
            await page.wait_for_selector(
                'div.related-question-pair',
                timeout=5000
            )
            print("[PAA] PAA section found in DOM")
        except Exception:
            print(f"[PAA] No PAA found for query: {q}")
            await browser.close()
            print("[PAA] Browser closed")
            return {"query": q, "paa": []}

        results = await page.eval_on_selector_all(
            'div.related-question-pair',
            'elements => elements.map(el => el.getAttribute("data-q")).filter(q => q)'
        )
        print(f"[PAA] Extracted {len(results)} questions: {results}")

        await browser.close()
        print("[PAA] Browser closed")
        return {"query": q, "paa": list(set(results))}
