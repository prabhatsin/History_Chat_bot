import json
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config.config import OUTPUT_DIR, NUM_DAYS

def read_json(input_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"Loaded {len(data)} items from {input_path}")
    return data

def merge_content(web_content, yt_content):
    merged = web_content + yt_content
    print(f"Merged: {len(web_content)} web + {len(yt_content)} youtube = {len(merged)} total")
    return merged

def save_merged(merged, days, output_dir=OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"merged_content_{days}_days.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=4, ensure_ascii=False)
    print(f"Merged content saved to {filepath}")
    return filepath


if __name__ == "__main__":
    web_path = os.path.join("data", f"Web_Extracted_Content_{NUM_DAYS}_days.json")
    yt_path = os.path.join("data", f"Youtube_translated_script_{NUM_DAYS}_days.json")
    web_content = read_json(web_path)
    yt_content = read_json(yt_path)
    merged = merge_content(web_content, yt_content)
    save_merged(merged, NUM_DAYS)


#! Whats this f here ???? "with open() as f"
#! f is an object. Specifically, it is a file object (often called a "file handle" or "stream").

'''
When you run with open(...) as f:, Python reaches out to your computer's
perating system and asks for access to the file Youtube_translated_script.json.
The operating system gives Python a "handle" to that file,
which Python then wraps into an object and assigns to the name f
'''


'''
3. What can you do with f?
Since f is an object, it has methods (actions) you can perform. Inside that with block, you’ll usually see things like:
data = f.read(): Slurps the whole file into a string.
data = json.load(f): Passes the file object to the JSON library to turn it into a Python dictionary.
for line in f:: Loops through the file one line at a time.
'''