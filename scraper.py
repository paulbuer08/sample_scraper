from helper import initialize_driver, load_config, load_codes_state, wait_for_element, WaitCondition, log_message, LogLevel
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import requests, zipfile, io, pandas
import gc, base64



# ----get JSON contents----
config = load_config()
codes_state = load_codes_state()


# ----perform data extraction----
def scrape_claims(search_category):
    claims, logs = [], []
    screenshot_base64 = ''

    driver = initialize_driver(config)
    try:
        # homepage
        driver.get(config['website']['url'])
        btn_navigate = wait_for_element(driver, By.XPATH, "//button[./span[text()='Sign In']]", WaitCondition.CLICKABLE)
        btn_navigate.click()
        log_message(logs, "Clicked the \"Sign In\" button.", LogLevel.INFO)

        # login with email
        btn_login_with_email = wait_for_element(driver, By.XPATH, "//button[./span[text()='Sign in with Email']]", WaitCondition.CLICKABLE)
        btn_login_with_email.click()
        log_message(logs, "Clicked the \"Sign in with Email\" button.", LogLevel.INFO)

        # login
        txt_username = wait_for_element(driver, By.XPATH, "//input[@name='email']", WaitCondition.PRESENT)
        txt_password = wait_for_element(driver, By.XPATH, "//input[@name='password']", WaitCondition.PRESENT)
        btn_login = wait_for_element(driver, By.XPATH, "//button[./span[text()='Sign In']]", WaitCondition.CLICKABLE)

        txt_username.send_keys(config['credentials']['username'])
        txt_password.send_keys(config['credentials']['password'])
        btn_login.click()
        log_message(logs, "Performed login successfully.", LogLevel.INFO)

        # check claim_id if already loaded in the view (trigger)
        header_claim_id = wait_for_element(driver, By.XPATH, "//div[./span[text()='CLM_ID']]", WaitCondition.PRESENT, is_scrollintoview=True, is_scrollhassticky=True)
        insured_codes_state = get_insured_address(logs)

        if header_claim_id and insured_codes_state:
            # targets the ancestor element 3 levels up, then its following-sibling 2 levels down
            # get top 5 records
            claim_elements = driver.find_elements(By.XPATH, "//div[./span[text()='CLM_ID']]/ancestor::div[3]/following-sibling::div[2]/span")[:5]

            for claim in claim_elements:
                desynpuf_id = claim.find_element(By.XPATH, "./div/div[1]").text
                claim_id = claim.find_element(By.XPATH, "./div/div[2]").text
                claim_type = "Inpatient claim"
                date_claim_from = claim.find_element(By.XPATH, "./div/div[4]").text
                date_claim_thru = claim.find_element(By.XPATH, "./div/div[5]").text
                claim_amount = claim.find_element(By.XPATH, "./div/div[7]").text
                insured_address = codes_state[str(insured_codes_state[str(desynpuf_id)])] if str(desynpuf_id) in insured_codes_state else ''

                claims.append({
                    "Claim ID": claim_id,
                    "Claim Type": claim_type,
                    "Date Claim From": date_claim_from,
                    "Date Claim Thru": date_claim_thru,
                    "Insured Address": insured_address,
                    "Claim Amount": claim_amount
                })
            logs.append("Extracted claim details")

            # capture screenshot
            screenshot = driver.get_screenshot_as_png()
            screenshot_base64 = base64.b64encode(screenshot).decode('utf-8')
            logs.append("Screenshot captured and encoded to base64.")

        return {
            "claims": claims,
            "screenshot_base64": screenshot_base64,
            "logs": logs
        }
    except Exception as e:
        logs.append(f"Error occurred: {str(e)}")
        return {
            "error": str(e),
            "logs": logs
        }
    finally:
        driver.quit()
        logs.append("WebDriver closed")



def get_insured_address(logs):
    insured_codes_state = {}
    response = requests.get(config['website']['bene'], stream=True)  # GET request to download the file as a stream

    if response.status_code == 200:
        # read the content of the response into an in-memory bytes buffer
        zip_stream = io.BytesIO(response.content)

        # open the zip file, extract the csv, then read it into a pandas DataFrame
        with zipfile.ZipFile(zip_stream, 'r') as zip_file:
            with zip_file.open('bene_file.csv') as file:
                # read only specific columns
                df = pandas.read_csv(file, usecols=['DESYNPUF_ID', 'SP_STATE_CODE'])

                for index, row in df.iterrows():
                    key = row['DESYNPUF_ID']
                    value = row['SP_STATE_CODE']
                    if key not in insured_codes_state:  # check for duplicate keys
                        insured_codes_state[key] = value

        # explicitly delete DataFrame and other large objects
        del df
        del zip_stream
        del response

        # force garbage collection to free up memory
        gc.collect()
    else:
        log_message(logs, f"Failed to download in memory [{response.status_code}]: {config['website']['bene']}", LogLevel.INFO)

    return insured_codes_state
