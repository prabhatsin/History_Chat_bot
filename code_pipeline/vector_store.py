import chromadb
import json
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config.config import OUTPUT_DIR, NUM_DAYS, CHROMA_PATH, COLLECTION_NAME

# NEW - initializes ChromaDB client and collection
def get_collection(chroma_path=CHROMA_PATH, collection_name=COLLECTION_NAME):
    # Using project root relative path so it works on any machine
    base_dir = os.path.join(os.path.dirname(__file__), "..")
    full_path = os.path.join(base_dir, chroma_path)
    client = chromadb.PersistentClient(path=full_path)
    collection = client.get_or_create_collection(collection_name)
    print(f"Collection '{collection_name}' ready, current count: {collection.count()}")
    return collection

def read_json(input_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"Loaded {len(data)} chunks from {input_path}")
    return data

# NEW - prepares data into the four lists ChromaDB expects
def prepare_chroma_data(data_list):
    ids = []
    embeddings = []
    documents = []
    metadatas = []
    for item in data_list:
        chunk_id = item['url'] + "__chunk_" + str(item['chunk_index'])
        ids.append(chunk_id)
        embeddings.append(item['vector'])
        documents.append(item['chunk_text'])
        metadatas.append({
            'url': item['url'],
            'title': item['title'],
            'timestamp': item['timestamp'],
            'chunk_index': item['chunk_index']
        })
    print(f"Prepared {len(ids)} chunks for upsert")
    return ids, embeddings, documents, metadatas

# NEW - upserts data into ChromaDB
def upsert_to_chroma(collection, ids, embeddings, documents, metadatas):
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )
    print(f"Upserted successfully. Collection count: {collection.count()}")


if __name__ == "__main__":
    input_path = os.path.join("data", f"Chunks_embedded_{NUM_DAYS}_days.json")
    data = read_json(input_path)
    collection = get_collection()
    ids, embeddings, documents, metadatas = prepare_chroma_data(data)
    upsert_to_chroma(collection, ids, embeddings, documents, metadatas)





# import chromadb
# import json
# chroma_client=chromadb.PersistentClient(path="./chroma")
# '''
# 1.Never  give path like this , it crashes as soon as machine changes 
# # path="F:\C drive data\Desktop\History_Chat_bot\chroma"

# 2.path="./chroma"

# This say wherever your script is → chroma folder

# '''
# #! TODO 
# #! This is more robus way to do it so explore it later 
# '''
# import os
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# path = os.path.join(BASE_DIR, "chroma")

# '''

# # collection=chroma_client.create_collection('mycollection')
# collection=chroma_client.get_or_create_collection('mycollection')

# # Its always better to use get_or_create_collection instead of create_collection
# # create_collection throws error when script runs more than once 

# with open('Chunks_embedded.json','r',encoding='utf-8') as file:
#     data_list=json.load(file)
# # print(len(data_list))

# ids        = []
# embeddings = []
# documents  = []
# metadatas  = []
# for items in data_list:
#     chunk_id=items['url']+"__chunk_"+str(items['chunk_index'])
#     ids.append(chunk_id)
#     embeddings.append(items['vector'])
#     documents.append(items['chunk_text'])
#     meta_entry={
#         'url':items['url'],
#           'title':items['title'],
#             'timestamp':items['timestamp'], 
#             'chunk_index':items['chunk_index']
#     }
#     metadatas.append(meta_entry)

# # print(len(ids),len(embeddings),len(documents),len(metadatas))

# #?-------------------------------------------------------------------------------------------
# #! TODO 
# #! The id generation step doesnot look very creative
# #! This step , items['url']+"__chunk_"+str(items['chunk_index'])
# #!, USE other ways later in phase 2

# #?-------------------------------------------------------------------------------------

# collection.upsert(
#     ids=ids,
#     embeddings=embeddings,
#     documents=documents,
#     metadatas=metadatas
# )

# print(collection.count())