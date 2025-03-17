from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InputData(BaseModel):
    keyword: str
    domain: str

class OutputData(BaseModel):
    exact_match: str
    topic_anchors: List[str]
    brand: List[str]

# 🧠 Smart brand splitting function
def smart_split_brand(domain_base: str) -> List[str]:
    variants = [domain_base]

    # Split camelCase / PascalCase (e.g., DataCamp -> Data Camp)
    camel_case_split = re.sub(r'([a-z])([A-Z])', r'\1 \2', domain_base)
    if camel_case_split != domain_base:
        variants.append(camel_case_split.lower())

    # Light compound heuristics (can be extended later)
    common_compounds = ["medspa", "datacamp", "healthcare", "webdesign"]
    for term in common_compounds:
        if term in domain_base:
            variants.append(domain_base.replace(term, f"{term[:-3]} {term[-3:]}"))

    # Generic fallback (split between long lowercase blocks)
    generic_split = re.sub(r'([a-z]{3,})([a-z]{3,})', r'\1 \2', domain_base)
    if generic_split != domain_base:
        variants.append(generic_split.lower())

    return list(set(variants))


@app.post("/process", response_model=OutputData)
def process_data(data: InputData):
    keyword = data.keyword.strip().lower()
    domain = data.domain.strip().lower().replace('www.', '').replace('https://', '').replace('http://', '')
    domain_base = domain.split('.')[0]

    words = keyword.split()
    
    # Global dynamic geo logic
    if len(words) >= 5:
        service_words = words[:-3]
        location_words = words[-3:]
    elif len(words) >= 4:
        service_words = words[:-2]
        location_words = words[-2:]
    else:
        service_words = words
        location_words = []

    service = " ".join(service_words)
    location = " ".join(location_words)

    # Create anchors based on keyword structure
    if location:
        topic_anchors = [
            keyword,                       # Exact keyword
            f"{location} {service}",       # Location first
            f"{service} {location}",       # Service first
            service                        # Service-only (partial)
        ]
    else:
        topic_anchors = [
            keyword,
            " ".join(words),
            " ".join(words[1:]),
            " ".join(words[0:2])
        ]

    # 🔄 Dynamic brand splitting
    brand_variants = smart_split_brand(domain_base)

    return OutputData(
        exact_match=keyword,
        topic_anchors=list(dict.fromkeys(topic_anchors)),
        brand=brand_variants
    )

@app.get("/")
def root():
    return {"message": "🚀 FastAPI with global keyword + smart brand splitter is running!"}
