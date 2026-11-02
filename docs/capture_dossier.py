import time
from pathlib import Path
from playwright.sync_api import sync_playwright

output_dir = Path(r"C:\Users\heyder\Desktop\dev\zine\docs\screenshots")
output_dir.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        headless=True,
    )
    context = browser.new_context(viewport={"width": 1440, "height": 1100})
    page = context.new_page()

    print("Navigating to Streamlit on localhost:8501...")
    page.goto("http://localhost:8501", wait_until="networkidle", timeout=30000)
    time.sleep(3)

    # Click on the Preset scenario selectbox or click the Run button
    buttons = page.query_selector_all("button")
    run_btn = None
    for b in buttons:
        txt = b.inner_text().strip()
        if "تنفيذ التحليل" in txt:
            run_btn = b
            break
    
    if run_btn:
        print("Clicking Run Analysis button...")
        run_btn.click()
        time.sleep(3)

    # Capture Tab 1 with Dossier visible
    dossier_shot = output_dir / "01_live_testing_model_duel.png"
    page.screenshot(path=str(dossier_shot), full_page=False)
    print(f"Captured fresh Tab 1 dossier: {dossier_shot} ({dossier_shot.stat().st_size} bytes)")

    browser.close()
print("Done!")
