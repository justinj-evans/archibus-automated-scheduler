
# Debug helper
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

def debug_wait(driver, locator, timeout=20, label="debug"):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
    except TimeoutException:
        print(f"[DEBUG] Timeout while waiting for {locator}")
        print(f"[DEBUG] Current URL: {driver.current_url}")

        # Save screenshot
        screenshot_file = f"{label}_screenshot.png"
        driver.save_screenshot(screenshot_file)
        print(f"[DEBUG] Screenshot saved: {screenshot_file}")

        # Save DOM
        dom_file = f"{label}_page_source.html"
        with open(dom_file, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"[DEBUG] Page source saved: {dom_file}")

        # Print first 500 chars of DOM for quick log inspection
        print("[DEBUG] First 500 chars of DOM:")
        print(driver.page_source[:500])

        raise  # keep failing test