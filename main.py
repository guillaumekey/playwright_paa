from fastapi import FastAPI
from playwright.async_api import async_playwright
from urllib.parse import quote_plus

app = FastAPI()

@app.get("/paa")
async def get_paa(q: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        page = await browser.new_page()
        await page.goto(
            f"https://www.google.com/search?q={quote_plus(q)}&hl=fr",
            wait_until="domcontentloaded"
        )

        # Handle Google cookie consent dialog if present (reject all)
        try:
            reject_btn = page.locator('button', has_text='Tout refuser')
            await reject_btn.click(timeout=3000)
        except Exception:
            pass

        try:
            await page.wait_for_selector(
                'div.related-question-pair',
                timeout=5000
            )
        except Exception:
            await browser.close()
            return {"query": q, "paa": []}

        results = await page.eval_on_selector_all(
            'div.related-question-pair',
            'elements => elements.map(el => el.getAttribute("data-q")).filter(q => q)'
        )

        await browser.close()
        return {"query": q, "paa": list(set(results))}
