import spacy

nlp = spacy.load("en_core_web_sm")

def human_sounding_filter(phrase):
    doc = nlp(phrase)
    
    if len(doc) < 2:
        return False

    # New filter: favor patterns that start with ADJ/NOUN and end with NOUN
    if doc[0].pos_ in ["ADJ", "NOUN"] and doc[-1].pos_ == "NOUN":
        return True
    
    return False


def keyword_breakdown(keyword):
    doc = nlp(keyword)
    normalized_input = " ".join([token.text for token in doc if not token.is_stop and token.is_alpha])
    tokens = [token.text for token in doc if not token.is_stop and token.is_alpha]

    # Extract only n-grams (bigrams to len(tokens))
    ngrams = []
    for n in range(2, len(tokens) + 1):
        for i in range(len(tokens) - n + 1):
            ngram = tokens[i:i + n]
            phrase = " ".join(ngram)
            ngrams.append(phrase)

    # Filter using human sounding rules
    final_results = []
    for phrase in ngrams:
        if human_sounding_filter(phrase) and phrase != normalized_input:
            final_results.append(phrase)

    # Sort by length desc
    sorted_results = sorted(final_results, key=lambda x: -len(x.split()))

    return sorted_results


# Example input
input_kw = "med spa tampa florida"
results = keyword_breakdown(input_kw)

for r in results:
    print(r)
