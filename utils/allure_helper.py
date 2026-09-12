import os
import logging
from datetime import datetime

import allure

logger = logging.getLogger(__name__)


def attach_failure_screenshot(driver, test_name):
    # --- Screenshot capture and Allure attachment ---
    try:
        screenshot_dir = "screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{test_name}_{timestamp}.png"
        file_path = os.path.join(screenshot_dir, file_name)

        screenshot = driver.get_screenshot_as_png()

        # Save locally
        with open(file_path, "wb") as file:
            file.write(screenshot)

        # Attach to Allure
        allure.attach(
            screenshot,
            name="Screenshot on Failure",
            attachment_type=allure.attachment_type.PNG,
        )

        logger.info("Screenshot saved: %s", file_path)

    except Exception as exc:
        logger.exception("Failed to capture screenshot: %s", exc)