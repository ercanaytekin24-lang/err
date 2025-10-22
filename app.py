# app.py
from flask import Flask, render_template, request
import asyncio
from playwright.async_api import async_playwright

app = Flask(__name__)

API_BASE = "https://arielservices.ct.ws/puan.php?lista="

async def fetch_card_playwright(card):
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(API_BASE + card, wait_until="networkidle", timeout=30000)
            content = await page.evaluate("() => document.body.innerText")
            content = content.strip() if content else ""
            # parse
            if "✅Approved" in content:
                parts = content.split("|")
                # puan genelde parts[6] veya parts[5]
                puan_raw = parts[6] if len(parts) >= 7 else (parts[5] if len(parts) >=6 else "0")
                # normalize -> "20.,75" -> "20.75"
                puan_fixed = puan_raw.replace("TL","").replace(" ","").replace("..",".").replace(".", "").replace(",", ".")
                # above removes thousands dots; now restore decimal
                try:
                    puan = float(puan_fixed) if puan_fixed else 0.0
                except:
                    # fallback: try extracting digits and comma/dot pattern
                    import re
                    m = re.search(r'(\d+[.,]?\d*)', puan_raw)
                    puan = float(m.group(1).replace(",", ".")) if m else 0.0
                status = "LIVE" if puan >= 1 else "DEC"
                return {"card": card, "status": status, "puan": puan}
            else:
                return {"card": card, "status": "DEC", "puan": 0.0}
        except Exception as e:
            print("Playwright error for", card, ":", e)
            return {"card": card, "status": "DEC", "puan": 0.0}
        finally:
            await browser.close()

def run_async(tasks):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(asyncio.gather(*tasks))

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    if request.method == "POST":
        raw = request.form.get("kartlar", "").strip()
        if raw:
            # kullanıcının her satıra kart koyacağı varsayılıyor
            cards = [c.strip() for c in raw.splitlines() if c.strip()]
            tasks = [fetch_card_playwright(c) for c in cards]
            results = run_async(tasks)
    return render_template("index.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)
