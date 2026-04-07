import json
import os, sys
import logging
import warnings
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config.config import OUTPUT_DIR, NUM_DAYS, EMBEDDING_MODEL_NAME
from sentence_transformers import SentenceTransformer

# Suppresses unnecessary warnings from transformers
os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN", "")
os.environ["TOKENIZERS_PARALLELISM"] = "false"
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

def read_json(input_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"Loaded {len(data)} chunks from {input_path}")
    return data

def load_model(model_name=EMBEDDING_MODEL_NAME):
    print(f"Loading model: {model_name}")
    model = SentenceTransformer(model_name)
    return model

# Embeds all chunk texts and adds vectors to each chunk dict
def embed_chunks(chunks, model):
    chunk_texts = [item['chunk_text'] for item in chunks]
    embeddings = model.encode(chunk_texts)
    # .tolist() deep converts numpy arrays to python lists for JSON serialization
    for item, embedding in zip(chunks, embeddings):
        item['vector'] = embedding.tolist()
    print(f"Embedded {len(chunks)} chunks")
    return chunks

def save_embedded(chunks, days, output_dir=OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"Chunks_embedded_{days}_days.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=4, ensure_ascii=False)
    print(f"Embedded chunks saved to {filepath}")
    return filepath


if __name__ == "__main__":
    input_path = os.path.join("data", f"Chunks_filtered_{NUM_DAYS}_days.json")
    chunks = read_json(input_path)
    model = load_model()
    embedded = embed_chunks(chunks, model)
    save_embedded(embedded, NUM_DAYS)





# from sentence_transformers import SentenceTransformer
# import json



# #! This step tries to supress the warning , explore later 
# # --------------------------------------------------------------------------
# import os
# import logging
# import warnings

# os.environ["HF_TOKEN"] = "your_token_here"
# os.environ["TOKENIZERS_PARALLELISM"] = "false"  # bonus: suppresses another common warning

# logging.getLogger("transformers").setLevel(logging.ERROR)
# logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
# warnings.filterwarnings("ignore")



# # ----------------------------------------------------------------------








# model=SentenceTransformer("all-MiniLM-L6-v2")

# #---------------------------------------------------------
# with open('Chunks_filtered.json','r',encoding='utf-8') as f:
#     chunks=json.load(f)
# # print(type(chunks))
# chunk_texts=[items['chunk_text'] for items in chunks]
# # print(len(chunk_texts))
# embeddings=model.encode(chunk_texts)  # This function takes a list 
# # print(embeddings)  #!expected 484*384
# # print(embeddings.shape)
# # print(chunk_texts)
# embeddings_list=list(embeddings)
# # print(type(embeddings_list))
# # for  embedding in embeddings_list:
# #     print(type(list(embedding)))
# #     break
# for item , embedding in zip(chunks,embeddings_list):
#     item['vector']=embedding.tolist()

# with open('Chunks_embedded.json','w',encoding='utf-8') as file:
#     json.dump(chunks,file,indent=4)

# print(f"Saved {len(chunks)} with chunk embeddings")

# #! Learnings from this script
# '''
# Serialization 

# Serialization means converting a Python object into a format that can
# be written to a file or sent over a network. JSON is just text — it only
# understands a limited set of types: strings, numbers, lists, dictionaries, booleans, and null.

# 1.When we dump anything inside a .json file only limited number of datatypes
# are accepted there , like the vector from model.encode is a numpy array
# we cant dump that in the file so convert it into a list 
# 2. Also  -->item['vector']=embedding.tolist()<-- this .tolist is a better approch in this case
# bcz -->list(embedding)<-- only converts the outer shell into a list while .tolist()
# goes inside each element and converts it into a python types 

# list(array)-->Shallow: Only converts the top level.
# array.tolist()-->Deep: Recursively converts all nested levels.

# '''