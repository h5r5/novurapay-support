from pathlib import Path
import time
from playwright.sync_api import sync_playwright

output_dir = Path(r"C:\Users\heyder\Desktop\dev\zine\docs\screenshots")
output_dir.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        headless=True,
    )
    context = browser.new_context(viewport={"width": 1440, "height": 950})
    page = context.new_page()

    print("Navigating to http://localhost:8501...")
    page.goto("http://localhost:8501", wait_until="networkidle", timeout=25000)
    time.sleep(3)  # Allow Streamlit components to mount and render

    # Find tabs
    tabs = page.query_selector_all('[role="tab"]')
    print(f"Found {len(tabs)} tabs.")

    tab_names = [
        "01_live_testing_model_duel.png",
        "02_review_queue.png",
        "03_ai_observability_evidence.png",
        "04_outage_intelligence.png",
        "05_active_learning_discrepancy.png",
    ]

    for idx, (tab, filename) in enumerate(zip(tabs, tab_names)):
        print(f"Capturing Tab {idx + 1} -> {filename}")
        tab.click()
        time.sleep(2)  # Wait for tab transition and re-render
        screenshot_path = output_dir / filename
        page.screenshot(path=str(screenshot_path), full_page=False)
        print(f"Saved: {screenshot_path} ({screenshot_path.stat().st_size} bytes)")

    browser.close()
print("All screenshots successfully captured!")
