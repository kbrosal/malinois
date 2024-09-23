
import serpapi
from dotenv import load_dotenv
import os
import tldextract

load_dotenv()

# Domain names to exclude
EXCLUDED_DOMAINS = [
    "amazon.com", "ebay.com", "walmart.com", "tesla.com", "facebook.com", "instagram.com", 
    "x.com", "quora.com", "reddit.com", "google.com", "netflix.com", "microsoft.com", 
    "yelp.com", "crunchbase.com", "yellowpages.com", "healthline.com", "harvard.edu", "stackoverflow.com"
]

# TLDs to exclude
EXCLUDED_TLDS = [".edu", ".gov"]

def normalize_domain(url):
    """
    Extract the root domain using tldextract, which ignores subdomains like 'www.' and returns the base domain.
    """
    extract_result = tldextract.extract(url)
    return f"{extract_result.domain}.{extract_result.suffix}"

def get_top_organic_results(keywords, location, client_website):
    EXCLUDED_DOMAINS.append(client_website)
    client = serpapi.Client(api_key=os.getenv('API_KEY'))

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
            
            if len(organic) == 0:
                print(f"No organic results found for keyword '{keyword}'")
            
            count = 0
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

                print(url)
                count += 1
                seen_domains.add(normalized_domain)  # Mark the domain as seen

                if count == 3:  # Limit to top 3 results
                    break

                
        except Exception as e:
            print(f"An error occurred for keyword '{keyword}': {e}")

if __name__ == '__main__':
    keywords = keywords = [
    "airflow alternatives",
    "python etl",
    "sql server etl",
]
    location = "United States",
    client_website = "hevodata.com"
    
    get_top_organic_results(keywords, location, client_website)  


