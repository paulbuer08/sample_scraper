from flask import Flask, request, jsonify
from scraper import scrape_claims
import logging


# ----initialize logging----
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


app = Flask(__name__)

# ----API endpoint -> triggers the scraping process----
@app.route('/scrape_claims', methods=['POST'])
def scrape_claims_api():
    try:
        data = request.get_json()
        search_category = data.get('claim_category', 'Default Category')
        logging.info(f"Received request to scrape claims with category: {search_category}")

        # call the scraping function
        result = scrape_claims(search_category)

        # return JSON response with collected logs
        logging.info("Scraping process completed. Returning JSON response.")
        return jsonify(result)

    except Exception as e:
        logging.error(f"Error in API endpoint /scrape_claims: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
