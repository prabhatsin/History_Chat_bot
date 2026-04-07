
import json 
import sys,os
from dotenv import load_dotenv
from google import genai
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))#! THIS must be before config import

from config.config import OUTPUT_DIR, NUM_DAYS
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def translate_text(text):
    try:
        prompt = f"If the following text is in Hindi, translate it to English. If it is already in English, return it unchanged. Return only the text, nothing else:\n\n{text}"
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return response.text
    except Exception as e:
        print(f"Translation failed: {e}")
        return text 

def translate_all(transcript_list):
    translated_script = []
    for item in transcript_list:
        translated_text = translate_text(item['content'])
        entry = {
            'url': item['url'],
            'title': item['title'],
            'timestamp': item['timestamp'],
            'content': translated_text
        }
        translated_script.append(entry)
    print(f"Translated {len(translated_script)} transcripts")
    return translated_script


def read_yt_content(input_path):
    with open(input_path, "r", encoding="utf-8") as f:
        transcript = json.load(f)
    print(f"Total transcripts to translate: {len(transcript)}")
    return transcript

def save_translated(translated_script, days, output_dir=OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"Youtube_translated_script_{days}_days.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(translated_script, f, indent=4, ensure_ascii=False)
    print(f"Translated content saved to {filepath}")
    return filepath

if __name__ == "__main__":
    input_path = os.path.join("data", f"Youtube_Extracted_content_{NUM_DAYS}_days.json")
    transcript = read_yt_content(input_path)
    translated = translate_all(transcript)
    save_translated(translated, NUM_DAYS)