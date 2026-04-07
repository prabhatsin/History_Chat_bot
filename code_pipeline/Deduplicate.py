
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import json
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
#! This function Removes the #fragment from a URL (e.g. #comments, #section2) since fragments point to the same page
#!So you're rebuilding the URL with everything intact except the fragment is now empty.
def strip_fragment(url):
    parsed = urlparse(url)
    cleaned = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        parsed.query,
        ""              #? This parf shows the empty fragment
    ))
    return cleaned

from config.config import MEANINGFUL_PARAMS

#!Restructuring the querry with only MEANINGFUL_PARAMS
def clean_query_params(url):
    parsed = urlparse(url)
    all_params = parse_qs(parsed.query) #turns that query string into a dictionary: {"v": ["abc"],
    filtered = {k: v for k, v in all_params.items() if k in MEANINGFUL_PARAMS}
    new_query = urlencode(filtered, doseq=True) #doseq=True handles the fact that values are lists.
    cleaned = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        ""
    ))
    return cleaned
# TODO: MEANINGFUL_PARAMS currently only covers YouTube (v, list, t). 
# Consider switching to a blacklist approach — remove known tracking params 
# (utm_source, utm_medium, fbclid, gclid, ref, si, feature) instead of 
# whitelisting meaningful ones. Safer for non-YouTube URLs.

#!Standardizes URL to 'https' and removes www. so that variations of the same site are treated as identical
def normalize_url(url):
    parsed = urlparse(url)
    scheme = "https"
    netloc = parsed.netloc.replace("www.", "")
    return urlunparse((scheme, netloc, parsed.path, parsed.params, parsed.query, ""))
from config.config import MEANINGFUL_PARAMS, OUTPUT_DIR ,SKIP_DOMAINS,SKIP_PATTERNS # CHANGED - added OUTPUT_DIR

def should_skip(url):
    parsed = urlparse(url)
    for domain in SKIP_DOMAINS:
        if domain in parsed.netloc:
            return True
    for pattern in SKIP_PATTERNS:
        if pattern in url:
            return True
    return False


def deduplicate(history):
    seen = {}
    for item in history:
        if should_skip(item["url"]): # If True Skip this complete url 
            continue
        cleaned_url = normalize_url(clean_query_params(strip_fragment(item["url"])))
        if cleaned_url not in seen:
            seen[cleaned_url] = item
        else:
            if item["timestamp"] > seen[cleaned_url]["timestamp"]:
                seen[cleaned_url] = item
          
    cleaned_history = list(seen.values())  # CHANGED - more readable name
    return cleaned_history
#So you're returning a deduplicated list of history items


# NEW - function to read input file
def read_history(input_path):
    with open(input_path, "r", encoding="utf-8") as f:
        history = json.load(f)
    print(f"Before deduplication: {len(history)}")
    return history

# NEW - function to save deduplicated data
def save_deduplicated(cleaned_history, days, output_dir=OUTPUT_DIR ):
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"history_last_{days}_days_clean.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(cleaned_history, f, indent=4, ensure_ascii=False)
    print(f"After deduplication: {len(cleaned_history)}")
    print(f"Saved to {filename}")
    return filename


if __name__ == "__main__":

    from config.config import NUM_DAYS
    input_path = os.path.join("data", f"history_last_{NUM_DAYS}_days.json")
    history = read_history(input_path)
    cleaned = deduplicate(history)
    print(f"Filtered out: {len(history) - len(cleaned)} duplicates")  # NEW
    save_deduplicated(cleaned, NUM_DAYS)