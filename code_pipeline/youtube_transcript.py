
#? This part of the code proides us the 'vedio id' of YT url ---------------------------
from urllib.parse import urlsplit, parse_qs
import os , sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
# Extracts video ID from both full youtube.com URLs and short youtu.be URLs
def extract_video_id(url):
    video_id = None 
    # Always Initialise the vriable to be returned like this 
    # So that if neither of conditions match , It still returns None   
    parser=urlsplit(url)
    #! Here it can be two cases  , full YT url or the short form 
    if "youtube.com" in url:
        query_dict=parse_qs(parser.query)
        video_id_list=query_dict.get('v')
        if video_id_list is not None:
            video_id=video_id_list[0]
        else:
            video_id=None
    elif 'youtu.be' in url:
        video_id = parser.path.lstrip("/")
    return video_id

#? This part of code Extracts the transcript from the given url ---------------------------
import logging
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import ( TranscriptsDisabled,NoTranscriptFound,VideoUnplayable,
    AgeRestricted,TranslationLanguageNotAvailable
)
from config.config import OUTPUT_DIR, YT_LOG_FILE, YT_SLEEP_TIME,NUM_DAYS

logger=logging.getLogger(__name__)
logging.basicConfig(filename=YT_LOG_FILE,encoding='utf-8',level=logging.INFO)

# Fetches transcript, tries English first then Hindi
def get_youtube_transcript(video_id,url):
    yt_api = YouTubeTranscriptApi()
    script = None
    try:
        script = yt_api.fetch(video_id, languages=['en'])
    except NoTranscriptFound:
        try:
            script = yt_api.fetch(video_id, languages=['hi'])
        except Exception as e:
            logger.info(f'No transcript found for {url}: {e}')
            return None
    except TranslationLanguageNotAvailable:
        logger.info(f'This vedio {url} does not have English Transcript')
        return None

    except TranscriptsDisabled:
        logger.info(f'This vedio {url} has transcript disabled')
        return None

    except AgeRestricted:
        logger.info(f'This vedio {url} is age restricted')
        return None

    except VideoUnplayable:
        logger.info(f'The vedio {url} is unplayable')
        return None

    except Exception as e:
        logger.info(f'Unexpected error for {url}: {e}')
        return None
    if script is not None: 
        full_text=" ".join([snippet.text for snippet in script])
        return full_text
    else:
        print("No transcript available")
        return None


import json
import time

# NEW - processes all YT links, extracts transcripts, skips playlists
def process_youtube_links(yt_list):
    content_list = []
    count_failed = 0
    for item in yt_list:
        link = item['url']
        if "youtube.com/playlist" in link:
            logger.info(f'[SKIPPED-playlist] {link}')
            continue
        video_id = extract_video_id(link)
        if video_id is None:
            logger.info(f'[SKIPPED-no-id] {link}')
            count_failed += 1
            continue
        result = get_youtube_transcript(video_id, link)
        time.sleep(YT_SLEEP_TIME)  # CHANGED - from config instead of hardcoded 10
        if result is None:
            count_failed += 1
            continue
        entry = {
            'url': item['url'],
            'title': item['title'],
            'timestamp': item['timestamp'],
            'content': result
        }
        content_list.append(entry)

    print(f"YouTube transcripts extracted: {len(content_list)}, Failed: {count_failed}")
    return content_list

def read_yt_links(input_path):
    with open(input_path, "r", encoding="utf-8") as f:
        yt_list = json.load(f)
    print(f"Total YouTube URLs: {len(yt_list)}")
    return yt_list


def save_yt_content(content_list,days, output_dir=OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"Youtube_Extracted_content_{days}_days.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(content_list, f, indent=4, ensure_ascii=False)
    print(f"YouTube content saved to {filepath}")
    return filepath




if __name__ == "__main__":
    from config.config import NUM_DAYS
    input_path = os.path.join("data", f"Youtube_Extracted_links_{NUM_DAYS}_days.json")
    yt_list = read_yt_links(input_path)
    content_list = process_youtube_links(yt_list)
    save_yt_content(content_list, NUM_DAYS)