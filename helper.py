from enum import Enum, auto
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
import logging
import sys

# ----initialize logging----
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# ----enum for log levels
class LogLevel(Enum):
    INFO = auto()
    ERROR = auto()
    WARNING = auto()
    DEBUG = auto()
    CRITICAL = auto()


# ----enum for wait conditions----
class WaitCondition(Enum):
    CLICKABLE = auto()
    VISIBLE = auto()
    PRESENT = auto()



# ----load configurations from config.json----
def load_config():
    try:
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)

        # verify that necessary keys are present in the config
        required_keys = ['selenium', 'website', 'credentials']
        for key in required_keys:
            if key not in config:
                raise KeyError(f"Missing required key '{key}' in config.json")

        logging.info("Configuration loaded successfully from config.json")
        return config

    except FileNotFoundError:
        logging.error("config.json file not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        logging.error("Failed to parse config.json. Please check the file format.")
        sys.exit(1)
    except KeyError as e:
        logging.error(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred while loading the configuration: {e}")
        sys.exit(1)



# ----load state-level FIPS code with their corresponding state name----
def load_codes_state():
    try:
        with open('codes_state.json', 'r') as codes_state_file:
            codes_state = json.load(codes_state_file)

        logging.info("State codes loaded successfully from codes_state.json")
        return codes_state

    except FileNotFoundError:
        logging.error("codes_state.json file not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        logging.error("Failed to parse codes_state.json. Please check the file format.")
        sys.exit(1)
    except KeyError as e:
        logging.error(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred while loading the file: {e}")
        sys.exit(1)



# ----initialize WebDriver with options from config.json----
def initialize_driver(config):
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # run as headless?
    if config['selenium'].get('headless', False):
        options.add_argument('--headless')

    # run in incognito?
    if config['selenium'].get('incognito', False):
        options.add_argument('--incognito')

    # initialize the driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    logging.info("WebDriver initialized successfully.")
    return driver



# ----helper method for waiting for an element using the WaitCondition enum----
def wait_for_element(driver, by, value, condition: WaitCondition, timeout=15, is_scrollintoview=False, is_scrollhassticky=False):
    """
        Wait for a specific condition of an element to be met using WaitCondition enum.

        :param driver: Selenium WebDriver instance
        :param by: Locator strategy (By.XPATH, By.ID, etc.)
        :param value: The locator value (e.g., XPath string)
        :param condition: The condition to wait for (WaitCondition enum)
        :param timeout: Maximum time to wait for the condition (default is 15 seconds)
        :param is_scrollintoview: Either to scroll the found element into view or not
        :param is_scrollhassticky: Either to account for sticky headers/footers or not
        :return: WebElement if the condition is met
    """
    try:
        if condition == WaitCondition.CLICKABLE:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
        elif condition == WaitCondition.VISIBLE:
            element = WebDriverWait(driver, timeout).until(
                EC.visibility_of_element_located((by, value))
            )
        elif condition == WaitCondition.PRESENT:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        else:
            raise ValueError(f"Unknown condition: {condition}")

        # using Javascript, scroll the element into view?
        if is_scrollintoview:
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)

            # adjust scroll position to account for sticky headers/footers
            if is_scrollhassticky:
                driver.execute_script("window.scrollBy(0, -150);")  # adjust the offset as needed
            logging.info(f"Scrolled to the element located by {by}='{value}' successfully.")

        logging.info(f"Element located by {by}='{value}' is now {condition.name} and interactable.")
        return element

    except Exception as e:
        logging.error(f"Error while waiting for element: {e}")
        return None



# ----call this to put a log-entry to both:----
#  -> [1] logging.basicConfig(...) - for persistent and system-wide logging
#  -> [2] logs=[] - for API-specific logging
def log_message(logs, message, level=LogLevel.INFO):
    """
        Logs a message and appends it to the provided logs list.

        :param logs: List to append log messages for the API response
        :param message: The message to log and append
        :param level: LogLevel enum value indicating the logging level
    """
    if level == LogLevel.INFO:
        logging.info(message)
    elif level == LogLevel.ERROR:
        logging.error(message)
    elif level == LogLevel.WARNING:
        logging.warning(message)
    elif level == LogLevel.DEBUG:
        logging.debug(message)
    elif level == LogLevel.CRITICAL:
        logging.critical(message)
    else:
        logging.info(message)  # default to info if level is unknown

    # append the message to the logs list for API response
    logs.append(message)
