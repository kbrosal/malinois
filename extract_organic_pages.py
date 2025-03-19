from flask import Flask, request, jsonify
import serpapi
from dotenv import load_dotenv
import os
import tldextract
import logging

load_dotenv()

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

# Homepage route
@app.route("/", methods=["GET"])
def home():
    return "Welcome to Malinois! Use POST /get-results to fetch results.", 200

# Domain names to exclude
EXCLUDED_DOMAINS = [
    "amazon.com", "ebay.com", "walmart.com", "tesla.com", "facebook.com", "instagram.com", 
    "x.com", "quora.com", "reddit.com", "google.com", "netflix.com", "microsoft.com", 
    "yelp.com", "crunchbase.com", "yellowpages.com", "healthline.com", "harvard.edu", "stackoverflow.com", "wikipedia.org", "youtube.com", "whatsapp.com",
    "chatgpt.com", "yahoo.com", "linkedin.com", "bing.com", "pinterest.com"
]

# TLDs to exclude
EXCLUDED_TLDS = [".edu", ".gov"]

def normalize_domain(url):
    """
    Extract the root domain using tldextract, which ignores subdomains like 'www.' and returns the base domain.
    """
    extract_result = tldextract.extract(url)
    return f"{extract_result.domain}.{extract_result.suffix}"

def perform_search(keyword, location, client, excluded_domains, gl):
    """
    Perform the actual search for a given keyword and location, applying domain filters.
    """
    params = {
            "q": keyword,
            "location": location,
            "hl": "en",  # Language
            "gl": gl,  # Country/Region code
            "google_domain": "google.com",  # Google domain
            "engine": "google"
        }
    try:
        results = client.search(params)
        organic = results.get("organic_results", [])

        if not organic:
            logging.info(f"No organic results found for keyword '{keyword}'")
            return []

        filtered_results = []
        seen_domains = set()

        for result in organic:
            url = result.get("link", '')
            normalized_domain = normalize_domain(url)

            # Skip if domain is excluded or has already been seen
            if normalized_domain in seen_domains or normalized_domain in excluded_domains:
                continue
            if any(normalized_domain.endswith(tld) for tld in EXCLUDED_TLDS):
                continue

            filtered_results.append(url)
            seen_domains.add(normalized_domain)

        logging.info(f"Found {len(filtered_results[:3])} results for keyword: {keyword}")
        return filtered_results[:3]
    
    except Exception as e:
        logging.error(f"Error processing keyword '{keyword}: {e}")
        return []



@app.route('/get-results', methods=['POST'])
def get_results():
    data = request.json
    keywords = data.get('keywords', [])
    location = data.get('location')
    client_website = data.get('client_website')
    gl = data.get('gl', 'us')
    
    excluded_domains = EXCLUDED_DOMAINS.copy()

    if client_website:
        excluded_domains.append(client_website)

    api_key = os.getenv('API_KEY')
    if not api_key:
        return jsonify({"Error": "API key is missing!"}), 400
    
    client = serpapi.Client(api_key=api_key)
    all_results = {}

    for keyword in keywords:
        try:
            logging.info(f"Processing keyword: {keyword}")
            filtered_results = perform_search(keyword, location, client, excluded_domains, gl)
            all_results[keyword] = filtered_results

        except Exception as e:
            logging.error(f"An error occurred while processing keyword '{keyword}': {e}")
            all_results[keyword] = f"Error processing keyword: {e}"

    return jsonify(all_results)

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))  # Railway's Port
    app.run(host="0.0.0.0", port=port, debug=True)
