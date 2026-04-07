# orchestrator.py — runs the full RAG pipeline end to end
import sys
import os
sys.path.append(os.path.dirname(__file__))

from config.config import NUM_DAYS, OUTPUT_DIR

def run_pipeline():
    print("=" * 50)
    print(f"Running pipeline for {NUM_DAYS} days of history")
    print("=" * 50)

    # Step 1: Chrome History Extraction
    print("\n--- Step 1: Chrome History Extraction ---")
    from code_pipeline.chrome_history_extraction import (
        get_chrome_history_path, copy_history_path,
        database_connection_extraction, process_rows, file_writing
    )
    path = get_chrome_history_path()
    copied_path = copy_history_path(path)
    rows = database_connection_extraction(copied_path, NUM_DAYS)
    history_data = process_rows(rows)
    history_file = file_writing(history_data, NUM_DAYS,OUTPUT_DIR)
    print(f"Extracted {len(history_data)} entries → {history_file}")

    # Step 2: Deduplicate & Filter domains
    print("\n--- Step 2: Deduplicate & Filter ---")
    from code_pipeline.Deduplicate import read_history, deduplicate, save_deduplicated
    history = read_history(history_file)
    cleaned = deduplicate(history)
    cleaned_file = save_deduplicated(cleaned, NUM_DAYS)
    print(f"Deduplicated: {len(history)} → {len(cleaned)} → {cleaned_file}")

    # Step 3: Web Content Extraction
    print("\n--- Step 3: Web Content Extraction ---")
    from code_pipeline.web_extraction import read_cleaned_history, process_urls, save_extracted
    history = read_cleaned_history(cleaned_file)
    extracted_content, yt_list = process_urls(history)
    web_file, yt_links_file = save_extracted(extracted_content, yt_list, NUM_DAYS)
    print(f"Web: {len(extracted_content)}, YouTube links: {len(yt_list)}")

    # Step 4: YouTube Transcript Extraction
    print("\n--- Step 4: YouTube Transcript Extraction ---")
    from code_pipeline.youtube_transcript import read_yt_links, process_youtube_links, save_yt_content
    yt_list = read_yt_links(yt_links_file)
    yt_content = process_youtube_links(yt_list)
    yt_content_file = save_yt_content(yt_content, NUM_DAYS)
    print(f"Transcripts extracted: {len(yt_content)}")

    # Step 5: Translate Hindi transcripts
    print("\n--- Step 5: Translate ---")
    from code_pipeline.youtube_translate_script import (
        read_yt_content as read_translate, translate_all, save_translated
    )
    transcript = read_translate(yt_content_file)
    translated = translate_all(transcript)
    translated_file = save_translated(translated, NUM_DAYS)
    print(f"Translated: {len(translated)}")

    # Step 6: Merge Web + YouTube content
    print("\n--- Step 6: Merge ---")
    from code_pipeline.merge_content import read_json as read_merge, merge_content, save_merged
    web_content = read_merge(web_file)
    merged = merge_content(web_content, translated)
    merged_file = save_merged(merged, NUM_DAYS)
    print(f"Merged total: {len(merged)}")

    # Step 7: Chunking + Filtering
    print("\n--- Step 7: Chunking ---")
    from code_pipeline.chunking import read_json as read_chunks, chunk_content, filter_chunks, save_chunks
    data = read_chunks(merged_file)
    chunks = chunk_content(data)
    filtered = filter_chunks(chunks)
    chunks_file = save_chunks(filtered, NUM_DAYS)
    print(f"Chunks: {len(chunks)} → Filtered: {len(filtered)}")

    # Step 8: Embedding
    print("\n--- Step 8: Embedding ---")
    from code_pipeline.embeddings import read_json as read_embed, load_model, embed_chunks, save_embedded
    chunks_data = read_embed(chunks_file)
    model = load_model()
    embedded = embed_chunks(chunks_data, model)
    embedded_file = save_embedded(embedded, NUM_DAYS)
    print(f"Embedded {len(embedded)} chunks")

    # Step 9: Store in ChromaDB
    print("\n--- Step 9: Vector Store ---")
    from code_pipeline.vector_store import read_json as read_vectors, get_collection, prepare_chroma_data, upsert_to_chroma
    data = read_vectors(embedded_file)
    collection = get_collection()
    ids, embeddings, documents, metadatas = prepare_chroma_data(data)
    upsert_to_chroma(collection, ids, embeddings, documents, metadatas)

    print("\n" + "=" * 50)
    print("Pipeline complete! Run 'streamlit run code_pipeline/app.py' to query.")
    print("=" * 50)


if __name__ == "__main__":
    run_pipeline()