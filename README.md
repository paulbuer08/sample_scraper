**Sample_Scraper** 

This python project is a web scraping tool with a REST API interface, detailed logging, configurable settings, and automated data extraction. 
It utilizes a Flask API (app.py) to handle HTTP requests, Selenium (scraper.py) for web scraping, and helper functions (helper.py) for configuration management and logging. 

**Files Overview**
1. config.json:  Contains configuration settings for Selenium and the target website URL. Credentials are not given so you need to create a Kaggle account first and use. 
2. codes_state.json:  Provides a mapping of state FIPS codes to state names. 
3. app.py:  The main entry point of the application. It sets up a Flask API to receive requests and trigger the scraping process. 
4. scraper.py:  Contains the core scraping logic using Selenium, including login automation and data extraction. 
5. helper.py:  Provides utility functions for initializing the web driver, handling configurations, logging, and waiting for elements.
6. requirements.txt:  List of dependencies/libraries used. 
