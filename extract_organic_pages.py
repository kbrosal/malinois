from flask import Flask, request, jsonify
import serpapi
from dotenv import load_dotenv
import os
import tldextract

load_dotenv()

app = Flask(__name__)

# Domain names to exclude
EXCLUDED_DOMAINS = [
    "amazon.com", "ebay.com", "walmart.com", "tesla.com", "facebook.com", "instagram.com", 
    "x.com", "quora.com", "reddit.com", "google.com", "netflix.com", "microsoft.com", 
    "yelp.com", "crunchbase.com", "yellowpages.com", "healthline.com", "harvard.edu"
]

# TLDs to exclude
EXCLUDED_TLDS = [".edu", ".gov"]

def normalize_domain(url):
    """
    Extract the root domain using tldextract, which ignores subdomains like 'www.' and returns the base domain.
    """
    extract_result = tldextract.extract(url)
    return f"{extract_result.domain}.{extract_result.suffix}"

@app.route('/get-results', methods=['POST'])
def get_results():
    data = request.json
    keywords = data.get('keywords', [])
    location = data.get('location')

    api_key = os.getenv('API_KEY')
    if not api_key:
        return jsonify({"Error": "API key is missing!"}), 500
    
    client = serpapi.Client(api_key=api_key)

    all_results = {}

    for keyword in keywords:
        print(f"\nProcessing keyword: {keyword}")

        params = {
            "q": keyword,
            "location": location,
            "hl": "en",  # Language
            "gl": "us",  # Country/Region code
            "google_domain": "google.com",  # Google domain
            "engine": "google"
        }

        try:
            results = client.search(params)
            organic = results.get("organic_results", [])
            
            if not organic:
                print(f"No organic results found for keyword '{keyword}'")
                all_results[keyword] = []  # No results for this keyword
                continue
            
            filtered_results =  []
            seen_domains = set()  # To track domains we have already processed
            print(f"Results for keyword: {keyword}")

            for result in organic:
                url = result.get("link", '')
                normalized_domain = normalize_domain(url)  # Normalize the domain

                # Skip if the domain has already been seen or it's in excluded domains or TLDs
                if normalized_domain in seen_domains or normalized_domain in EXCLUDED_DOMAINS:
                    continue
                if any(normalized_domain.endswith(tld) for tld in EXCLUDED_TLDS):
                    continue

                filtered_results.append(url)
                seen_domains.add(normalized_domain)  # Mark the domain as seen

            all_results[keyword] = filtered_results[:3] # Store top 3 results for this keyword


        except Exception as e:
            print(f"An error occurred while processing keyword '{keyword}': {e}")
            all_results[keyword] = f"Error processing keyword: {e}"

    return jsonify(all_results)

if __name__ == '__main__':
    app.run(debug=True)  
