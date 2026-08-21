import os
from datetime import datetime

import allure


def attach_failure_screenshot(driver, test_name):
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

        print(f"Screenshot saved: {file_path}")

    except Exception as exc:
        print(f"Failed to capture screenshot: {exc}")