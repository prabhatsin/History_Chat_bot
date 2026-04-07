import os
import sys
import io
import logging
import warnings
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

os.environ["TOKENIZERS_PARALLELISM"] = "false"
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

import chromadb
from google import genai
from config.config import EMBEDDING_MODEL_NAME, CHROMA_PATH, COLLECTION_NAME,QUERY_N_RESULTS

def load_model():
    old_stderr = sys.stderr
    sys.stderr = io.StringIO()
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)  # CHANGED - from config
    sys.stderr = old_stderr
    return model

def load_collection():
    base_dir = os.path.join(os.path.dirname(__file__), "..")
    client = chromadb.PersistentClient(path=os.path.join(base_dir, CHROMA_PATH))  # CHANGED - from config
    return client.get_collection(COLLECTION_NAME)  # CHANGED - from config

def load_gemini():
    return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# CHANGED - distance threshold from config
from config.config import QUERY_DISTANCE_THRESHOLD

def get_rag_response(user_query, model, collection, gemini_client):
    query_embedding = model.encode(user_query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=10,
        include=["documents", "metadatas", "distances"]
    )

    filtered = [
        (doc, meta, dist)
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        )
        if dist < QUERY_DISTANCE_THRESHOLD  # CHANGED - from config instead of hardcoded 1.0
    ]

    if not filtered:
        yield "I couldn't find relevant information in your browsing history for this query."
        return

    context = ""
    for doc, meta, dist in filtered:
        context += f"Source: {meta['title']}\nURL: {meta['url']}\n{doc}\n\n"

    prompt = f"""You are a helpful assistant that helps users recall and understand content from their browsing history.
Based on the following content from pages the user has visited, provide a detailed and elaborate answer.
Include specific concepts, examples, and explanations found in the content.
Do not repeat information. Be concise and avoid redundancy.

Context:
{context}

Question: {user_query}

Answer:"""

    try:

        response = gemini_client.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=prompt
        )
        for chunk in response:
            yield chunk.text
    except Exception as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            yield "Rate limit hit. Please wait a few seconds and try again."
        else:
            yield f"Error generating response: {e}"
 


# NEW - prints retrieved chunks for debugging
def print_retrieved_results(user_query, model, collection):
    query_embedding = model.encode(user_query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=QUERY_N_RESULTS,
        include=["documents", "metadatas", "distances"]
    )
    print("\n===== Retrieved Chunks =====")
    for i, (doc, meta, dist) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    )):
        print(f"\n--- Chunk {i+1} (distance: {dist:.4f}) ---")
        print(f"Title: {meta['title']}")
        print(f"URL: {meta['url']}")
        print(f"Text: {doc[:100]}...")  # first 100 chars only
    print("\n============================")


#!yield = a waiter who brings each dish as soon as it's ready. Appetizer first, then soup, then
#  main course — you start eating immediately without waiting for everything.
# A function with yield is called a generator
if __name__ == "__main__":
    model      = load_model()
    collection = load_collection()
    gemini     = load_gemini()

    user_query = input("Ask a question about your browsing history: ")
    print_retrieved_results(user_query, model, collection)
    print("\n===== Answer =====")
    for chunk in get_rag_response(user_query, model, collection, gemini):
        print(chunk, end="", flush=True)