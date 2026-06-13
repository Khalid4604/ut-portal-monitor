import os
import asyncio
import logging
import requests
from playwright.async_api import async_playwright

# --- Configuration & Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Credentials and Notification Settings from Environment Variables
UT_USERNAME = os.getenv('UT_USERNAME')
UT_PASSWORD = os.getenv('UT_PASSWORD')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

PORTAL_URL = "https://myut.ut.edu.sa/ut/ui/guest/common/index.faces"

def send_telegram_notification(message):
    """
    Sends a message to the user via Telegram Bot API.
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram configuration missing. Skipping notification.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logger.info("Telegram notification sent successfully.")
    except Exception as e:
        logger.error(f"Failed to send Telegram notification: {str(e)}")

async def monitor_tabuk_portal():
    if not UT_USERNAME or not UT_PASSWORD:
        logger.error("Missing UT credentials. Please set UT_USERNAME and UT_PASSWORD env vars.")
        return

    async with async_playwright() as p:
        logger.info("Starting University of Tabuk portal monitor...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        try:
            # 1. Login Phase
            logger.info("Navigating to login page...")
            await page.goto(PORTAL_URL)
            
            await page.fill('input[id*="username"]', UT_USERNAME)
            await page.fill('input[id*="password"]', UT_PASSWORD)
            
            # Wait for navigation after clicking login
            await asyncio.gather(
                page.wait_for_load_state("networkidle"),
                page.click('button[id*="login"], input[type="submit"]')
            )
            
            # Check for login errors
            if "index.faces" in page.url and await page.query_selector(".error"):
                error_msg = "❌ <b>Tabuk Portal Login Failed:</b> Invalid credentials or server error."
                logger.error(error_msg)
                send_telegram_notification(error_msg)
                return
            
            logger.info("Login successful.")

            # 2. Check 'Drop and Add' (الحذف والاضافة)
            logger.info("Checking Drop/Add (الحذف والاضافة) section...")
            drop_add_link = page.get_by_text("الحذف والاضافة", exact=False)
            
            if await drop_add_link.count() > 0:
                await asyncio.gather(
                    page.wait_for_load_state("networkidle"),
                    drop_add_link.click()
                )
                
                content = await page.content()
                # Check if registration is open based on common success keywords
                if "متاح" in content or "اختيار المقرر" in content:
                    status_msg = "🚀 <b>University of Tabuk Alert:</b> Drop/Add (الحذف والاضافة) is now <b>OPEN</b>!"
                    logger.info(status_msg)
                    send_telegram_notification(status_msg)
                else:
                    logger.info("Drop/Add is currently closed.")
            else:
                logger.warning("Drop/Add link not found in the portal menu.")

            # 3. Check Final Grades / Transcript
            logger.info("Checking Final Grades (النتائج الدراسية) section...")
            grades_link = page.get_by_text("النتائج الدراسية", exact=False)
            
            if await grades_link.count() > 0:
                await asyncio.gather(
                    page.wait_for_load_state("networkidle"),
                    grades_link.click()
                )
                
                # Look for grade tables
                grades_table = await page.query_selector("table")
                if grades_table:
                    # In a production version, you would hash this table to detect changes.
                    # For now, we log that the data was successfully accessed.
                    logger.info("Successfully accessed grades table.")
                else:
                    logger.warning("Grades table container not found.")
            else:
                logger.warning("Grades/Transcript link not found in the portal menu.")

        except Exception as e:
            error_trace = f"⚠️ <b>Automation Error:</b> {str(e)}"
            logger.error(error_trace)
            send_telegram_notification(error_trace)
        finally:
            await browser.close()
            logger.info("Portal monitor task completed.")

if __name__ == "__main__":
    asyncio.run(monitor_tabuk_portal())
