import shutil
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

output_dir = Path(r"C:\Users\heyder\Desktop\dev\zine\docs\screenshots")
output_dir.mkdir(parents=True, exist_ok=True)
artifact_dir = Path(r"C:\Users\heyder\.t3\userdata\providers\antigravity\ac0a3dfd6dddb20962cecff6ee5fe65e19d3923be20e52c5ab52ff877f7e4c32\antigravity-acp\brain\f3f6b061-8672-4831-8afc-bad0318bda45")

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        headless=True,
    )
    context = browser.new_context(viewport={"width": 1440, "height": 950})
    page = context.new_page()

    print("Navigating to http://127.0.0.1:8502...")
    page.goto("http://127.0.0.1:8502", timeout=30000)
    time.sleep(5)  # Allow Streamlit to initialize

    # In Tab 1, click Run button to generate the full dossier
    buttons = page.query_selector_all("button")
    for b in buttons:
        txt = b.inner_text()
        if "فحص" in txt or "run" in txt.lower():
            print("Found and clicking inspection button...")
            b.click()
            time.sleep(4)
            break

    # 1. Capture Tab 1
    t1_path = output_dir / "01_live_testing_model_duel.png"
    page.screenshot(path=str(t1_path), full_page=False)
    print(f"Captured Tab 1 -> {t1_path.name}")

    # Tabs navigation
    tabs = page.query_selector_all('[role="tab"]')
    print(f"Found {len(tabs)} tabs.")

    tab_files = [
        "01_live_testing_model_duel.png",
        "02_review_queue.png",
        "03_ai_observability_evidence.png",
        "04_outage_intelligence.png",
        "05_active_learning_discrepancy.png",
    ]

    for idx, filename in enumerate(tab_files):
        if idx == 0:
            continue
        if idx < len(tabs):
            print(f"Clicking Tab {idx+1}...")
            tabs[idx].click()
            time.sleep(2)
            shot_path = output_dir / filename
            page.screenshot(path=str(shot_path), full_page=False)
            print(f"Captured Tab {idx+1} -> {filename}")

    browser.close()

# Copy to artifacts directory
for f in tab_files:
    src_f = output_dir / f
    if src_f.exists():
        dst_f = artifact_dir / f
        shutil.copy2(src_f, dst_f)
        print(f"Copied {f} to artifact directory ({dst_f.stat().st_size} bytes)")

print("All redesigned screenshots captured and synced successfully!")
