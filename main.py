from fastapi import FastAPI
from playwright.async_api import async_playwright

app = FastAPI()

@app.get("/paa")
async def get_paa(q: str):
    async with async_playwright() as p:
        # Remplace ta ligne browser = ... par celle-ci :
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        page = await browser.new_page()
        await page.goto(f"https://www.google.com/search?q={q}&hl=fr")
        
        # On récupère les questions (version rapide sans clics pour le test)
        questions = await page.query_selector_all('div[role="button"]:has-text("?")')
        results = [await q.inner_text() for q in questions]
        
        await browser.close()
        return {"query": q, "paa": list(set(results))}