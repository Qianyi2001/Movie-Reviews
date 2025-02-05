from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def init_webdriver(
    chromedriver_path='chromedriver.exe',
    window_size="1200,1080",
    headless=False
):
    options = Options()
    options.add_argument(f"--window-size={window_size}")
    options.add_argument("--incognito")
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    if headless:
        options.add_argument("--headless")

    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver
