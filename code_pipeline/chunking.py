import json
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config.config import OUTPUT_DIR, NUM_DAYS

from config.config import CHUNK_SIZE, CHUNK_STEP, CHUNK_MIN_LENGTH

def read_json(input_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"Loaded {len(data)} items from {input_path}")
    return data

# Splits each item's content into overlapping chunks
def chunk_content(data):
    chunk_list = []
    for item in data:
        content = item["content"]
        chunk_index = 0
        for i in range(0, len(content), CHUNK_STEP):
            chunk_text = content[i:i + CHUNK_SIZE]
            chunk = {
                'url': item['url'],
                'title': item['title'],
                'chunk_text': chunk_text,
                'timestamp': item['timestamp'],
                'chunk_index': chunk_index
            }
            chunk_list.append(chunk)
            chunk_index += 1
    print(f"Total chunks created: {len(chunk_list)}")
    return chunk_list



# Removes chunks shorter than CHUNK_MIN_LENGTH
def filter_chunks(chunk_list):
    filtered = [item for item in chunk_list if len(item['chunk_text']) > CHUNK_MIN_LENGTH]
    print(f"Before filter: {len(chunk_list)}, After filter: {len(filtered)}, Removed: {len(chunk_list) - len(filtered)}")
    return filtered

def save_chunks(chunk_list, days, output_dir=OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"Chunks_filtered_{days}_days.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(chunk_list, f, indent=4, ensure_ascii=False)
    print(f"Chunks saved to {filepath}")
    return filepath


if __name__ == "__main__":
    input_path = os.path.join("data", f"merged_content_{NUM_DAYS}_days.json")
    data = read_json(input_path)
    chunks = chunk_content(data)
    filtered = filter_chunks(chunks)
    save_chunks(filtered, NUM_DAYS)















# import json
# with open('merged_content.json', 'r', encoding='utf-8') as file:
#     data=json.load(file)

# chunk_list=[]
# for item in data:
#     Content=item["content"]
#     # print(type(Content))
#     # print(Content)
    
#     chunk_index=0
#     for i in range(0, len(Content),400):
#         chunk_text=Content[i:i+500]
#         chunk={'url':item['url'],
#               'title':item['title'],
#               'chunk_text':chunk_text,
#               'timestamp':item['timestamp'],
#               'chunk_index':chunk_index
#         }
#         chunk_index+=1
#         chunk_list.append(chunk)
#         # print(dict)
#         # print(chunk_list)

# with open ('Chunks.json','w',encoding='utf-8') as f:
#     json.dump(chunk_list,f,indent=4)


