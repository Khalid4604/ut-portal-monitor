# University of Tabuk Portal Monitor

This project monitors the University of Tabuk (UT) student portal for specific events like the opening of the Drop/Add (الحذف والاضافة) period and updates to final grades.

## Prerequisites

- Python 3.8+
- Playwright
- Telegram Bot Token and Chat ID (for notifications)

## Environment Variables

To run the monitor, you need to set the following environment variables:

- `UT_USERNAME`: Your University of Tabuk student ID or username.
- `UT_PASSWORD`: Your University of Tabuk portal password.
- `TELEGRAM_TOKEN`: Your Telegram Bot API token (get it from @BotFather).
- `TELEGRAM_CHAT_ID`: Your Telegram Chat ID (get it from @userinfobot).

## Setup

1. Install dependencies:
   ```bash
   pip install playwright requests
   playwright install chromium
   ```

2. Run the monitor:
   ```bash
   export UT_USERNAME='your_username'
   export UT_PASSWORD='your_password'
   export TELEGRAM_TOKEN='your_bot_token'
   export TELEGRAM_CHAT_ID='your_chat_id'
   python ut_monitor.py
   ```

## Files

- `ut_monitor.py`: The main Python script using Playwright to check the portal.
- `ut_poke_automation.ts`: A Poke automation script for handling notifications within the Poke ecosystem.
