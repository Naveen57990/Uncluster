#!/usr/bin/env python3
"""
Playwright Automated Demo Video Recorder for Uncluster.
Records 1920x1080 30fps screen video of the Cyberdeck Web Console with in-DOM subtitle badges.
"""

import os
import sys
import json
import asyncio
from playwright.async_api import async_playwright

DEMO_DIR = os.path.dirname(__file__)
RAW_VIDEO_DIR = os.path.join(DEMO_DIR, "raw_video")
WEB_DIR = os.path.abspath(os.path.join(DEMO_DIR, "..", "web"))
SCRIPT_FILE = os.path.join(DEMO_DIR, "voiceover_script.json")

# Clean existing webm files in raw_video
os.makedirs(RAW_VIDEO_DIR, exist_ok=True)
for f in os.listdir(RAW_VIDEO_DIR):
    if f.endswith(".webm"):
        try:
            os.remove(os.path.join(RAW_VIDEO_DIR, f))
        except Exception:
            pass

with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
    SEGMENTS = json.load(f)

# Scene durations corresponding to each audio segment
DURATIONS = {
    1: 17.74,
    2: 13.82,
    3: 17.33,
    4: 15.70,
    5: 13.10,
    6: 19.22,
    7: 12.77,
    8: 9.14
}

async def record():
    html_url = f"file://{os.path.join(WEB_DIR, 'index.html')}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-web-security",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2,
            record_video_dir=RAW_VIDEO_DIR,
            record_video_size={"width": 1920, "height": 1080}
        )

        page = await context.new_page()
        await page.goto(html_url, wait_until="networkidle")

        # Inject cyberdeck subtitle badge into DOM
        await page.evaluate("""() => {
            const badge = document.createElement('div');
            badge.id = 'demoSubtitleBadge';
            badge.style.cssText = `
                position: fixed;
                bottom: 34px;
                left: 50%;
                transform: translateX(-50%);
                background: rgba(10, 14, 20, 0.94);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid rgba(245, 166, 35, 0.45);
                border-radius: 9999px;
                padding: 12px 36px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 20px;
                font-weight: 700;
                color: #FFFFFF;
                box-shadow: 0 12px 36px rgba(0, 0, 0, 0.8), 0 0 24px rgba(245, 166, 35, 0.25);
                z-index: 10000;
                transition: opacity 200ms ease, transform 200ms ease;
                pointer-events: none;
                text-align: center;
                max-width: 85%;
                white-space: nowrap;
                letter-spacing: 0.5px;
            `;
            document.body.appendChild(badge);
        }""")

        async def set_subtitle(text):
            await page.evaluate(f"""(txt) => {{
                const el = document.getElementById('demoSubtitleBadge');
                if (el) {{
                    el.style.opacity = '0';
                    el.style.transform = 'translateX(-50%) translateY(8px)';
                    setTimeout(() => {{
                        el.textContent = txt;
                        el.style.opacity = '1';
                        el.style.transform = 'translateX(-50%) translateY(0)';
                    }}, 150);
                }}
            }}""", text)

        # =========================================================================
        # SCENE 1: The Threat: UTXO Cluster Deanonymization (17.74s)
        # =========================================================================
        print("🎬 Scene 1: The Threat (17.74s)")
        await set_subtitle(SEGMENTS[0]["subtitle"])
        await asyncio.sleep(2.0)

        # Smooth scan down
        for _ in range(3):
            await page.mouse.wheel(0, 100)
            await asyncio.sleep(0.5)

        await page.mouse.move(960, 420)
        await asyncio.sleep(4.0)

        # Hover over mempool ticker and system chips
        await page.hover("#mempool-tip")
        await asyncio.sleep(3.0)

        # Smooth return to top
        await page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
        await asyncio.sleep(6.74)

        # =========================================================================
        # SCENE 2: Introducing Uncluster (13.82s)
        # =========================================================================
        print("🎬 Scene 2: Introducing Uncluster (13.82s)")
        await set_subtitle(SEGMENTS[1]["subtitle"])
        await asyncio.sleep(2.0)

        # Highlight pre-flight test vector buttons
        await page.hover('[data-scenario="cioh_leak"]')
        await asyncio.sleep(2.0)

        # Click scenario 1 to ensure loaded
        await page.click('[data-scenario="cioh_leak"]')
        await asyncio.sleep(3.0)

        # Scroll down to reveal inputs / outputs
        await page.mouse.wheel(0, 180)
        await asyncio.sleep(3.0)
        await asyncio.sleep(3.82)

        # =========================================================================
        # SCENE 3: Live Pre-Flight Audit & CIOH Detection (17.33s)
        # =========================================================================
        print("🎬 Scene 3: Live Pre-Flight Audit & CIOH (17.33s)")
        await set_subtitle(SEGMENTS[2]["subtitle"])
        await asyncio.sleep(2.0)

        # Hover over the ASCII topology diagram showing contaminated clusters
        await page.hover("#ascii-topology-diagram")
        await asyncio.sleep(3.5)

        # Hover over the CIOH violation check item
        await page.hover("#chk-cioh")
        await asyncio.sleep(3.5)

        # Hover over the Score Grade Badge
        await page.hover("#score-grade-badge")
        await asyncio.sleep(4.0)
        await asyncio.sleep(4.33)

        # =========================================================================
        # SCENE 4: Toxic Change & BIP-69 Fingerprint Audit (15.70s)
        # =========================================================================
        print("🎬 Scene 4: Toxic Change & BIP-69 (15.70s)")
        await set_subtitle(SEGMENTS[3]["subtitle"])
        await asyncio.sleep(2.0)

        # Click Scenario 2: Toxic Change Mismatch
        await page.click('[data-scenario="script_mismatch"]')
        await asyncio.sleep(3.0)

        # Hover over script mismatch check item
        await page.hover("#chk-script")
        await asyncio.sleep(3.5)

        # Hover over remediation recommendations
        await page.hover("#remediation-list")
        await asyncio.sleep(4.0)
        await asyncio.sleep(3.20)

        # =========================================================================
        # SCENE 5: Autonomous Coin Selection Sanitization (13.10s)
        # =========================================================================
        print("🎬 Scene 5: Autonomous Coin Selection Sanitization (13.10s)")
        await set_subtitle(SEGMENTS[4]["subtitle"])
        await asyncio.sleep(2.0)

        # Click SANITIZE COIN SELECTION button to open modal
        await page.click("#btn-sanitize-now")
        await asyncio.sleep(2.5)

        # Click recalculate unclustered pool
        await page.click("#btn-calc-sanitize")
        await asyncio.sleep(3.5)

        # Close sanitize modal
        await page.click("#btn-close-sanitize-btn")
        await asyncio.sleep(2.0)
        await asyncio.sleep(3.10)

        # =========================================================================
        # SCENE 6: Nostr Agent Shield & Relay Leak Auditing (19.22s)
        # =========================================================================
        print("🎬 Scene 6: Nostr Agent Shield (19.22s)")
        await set_subtitle(SEGMENTS[5]["subtitle"])
        await asyncio.sleep(2.0)

        # Click Scenario 4: Nostr Agent Gossip Shield
        await page.click('[data-scenario="nostr_zap"]')
        await asyncio.sleep(3.5)

        # Hover over Nostr event details
        await page.hover("#ascii-topology-diagram")
        await asyncio.sleep(4.5)

        # Scroll to remediation and status
        await page.hover("#gauge-verdict")
        await asyncio.sleep(4.0)
        await asyncio.sleep(5.22)

        # =========================================================================
        # SCENE 7: Terminal CLI & Open-Source Engine (12.77s)
        # =========================================================================
        print("🎬 Scene 7: Terminal CLI & Architecture (12.77s)")
        await set_subtitle(SEGMENTS[6]["subtitle"])
        await asyncio.sleep(2.0)

        # Click Scenario 3: Sovereign Clean Payment
        await page.click('[data-scenario="sovereign_clean"]')
        await asyncio.sleep(3.0)

        # Hover over the perfect 100/100 score
        await page.hover("#score-number")
        await asyncio.sleep(3.5)
        await asyncio.sleep(4.27)

        # =========================================================================
        # SCENE 8: Conclusion: Never Broadcast Blind (9.14s)
        # =========================================================================
        print("🎬 Scene 8: Conclusion (9.14s)")
        await set_subtitle(SEGMENTS[7]["subtitle"])

        # Scroll back to top
        await page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
        await asyncio.sleep(4.0)
        await page.mouse.move(960, 200)
        await asyncio.sleep(5.14)

        print("Recording finished, closing browser...")
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(record())
