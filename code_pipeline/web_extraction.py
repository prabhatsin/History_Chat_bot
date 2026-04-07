import trafilatura
import json
import logging
import sys ,os



sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config.config import OUTPUT_DIR, MIN_CONTENT_LENGTH, LOG_FILE
#! -----------------------------------------------------------------------------------------
logger=logging.getLogger(__name__)
logging.basicConfig(filename=LOG_FILE,encoding='utf-8',level=logging.INFO)



# Return True for youtube links
# def is_youtube(url):
#     if "youtube.com" in url or "youtu.be" in url:
#         return True
#     else:
#         return False
    
from code_pipeline.youtube_transcript import extract_video_id

from code_pipeline.youtube_transcript import extract_video_id

def is_youtube_video(url):
    if "youtube.com" not in url and "youtu.be" not in url:
        return False 
    video_id = extract_video_id(url)
    
    if video_id is not None:
        return True
    else:
        return False

# Scrapes a Single url
def scrape_url(url):
    try:
        html = trafilatura.fetch_url(url)
        if html is None:
            return None
        result = trafilatura.extract(html)
        return result
    except Exception as e:
        logger.warning(f"[ERROR] Failed to scrape {url}: {e}")
        return None


# NEW - separates YT links from web URLs and scrapes web content
def process_urls(history):
    yt_list = []
    extracted_content = []
    count_failed = 0

    for item in history:
        link = item['url']

        if is_youtube_video(link):
            yt_list.append(item)
            continue  # FIXED - skip to next item after adding to YT list

        result = scrape_url(link)

        if result is None or len(result) < MIN_CONTENT_LENGTH:
            logger.warning(f"[FAILED] {link} content too short or None")
            count_failed += 1
            continue

        entry = {
            'url': item['url'],
            'title': item['title'],
            'timestamp': item['timestamp'],
            'content': result
        }
        extracted_content.append(entry)

    print(f"Extracted: {len(extracted_content)}, YouTube: {len(yt_list)}, Failed: {count_failed}")
    return extracted_content, yt_list



# NEW - saves both outputs to files
def save_extracted(extracted_content, yt_list,days, output_dir=OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)

    web_path = os.path.join(output_dir, f"Web_Extracted_Content_{days}_days.json")
    with open(web_path, "w", encoding="utf-8") as f:
        json.dump(extracted_content, f, indent=4, ensure_ascii=False)

    yt_path = os.path.join(output_dir, f"Youtube_Extracted_links_{days}_days.json")
    with open(yt_path, "w", encoding="utf-8") as f:
        json.dump(yt_list, f, indent=4, ensure_ascii=False)

    print(f"Web content saved to {web_path}")
    print(f"YouTube links saved to {yt_path}")
    return web_path, yt_path


# NEW - read input file
def read_cleaned_history(input_path):
    with open(input_path, "r", encoding="utf-8") as f:
        history = json.load(f)
    print(f"Total input URLs: {len(history)}")
    return history
        


if __name__ == "__main__":
    from config.config import NUM_DAYS
    input_path = os.path.join("data", f"history_last_{NUM_DAYS}_days_clean.json")
    history = read_cleaned_history(input_path)
    extracted_content, yt_list = process_urls(history)
    save_extracted(extracted_content, yt_list,NUM_DAYS)


