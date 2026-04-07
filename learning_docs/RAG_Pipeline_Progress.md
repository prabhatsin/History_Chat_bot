# Chrome History RAG Chatbot — Progress Log

## Project Goal
Build a RAG (Retrieval Augmented Generation) chatbot that answers questions based on your Chrome browsing history. Phase 1 is a pure Python pipeline. Phase 2 will wrap it in a Chrome extension.

---

## Architecture Overview

```
Chrome History (SQLite)
        ↓
Step 1: Extract URLs + timestamps
        ↓
Step 2: Deduplicate + Clean URLs
        ↓
Step 3: Fetch page content (trafilatura)
        ↓
Step 4: Chunk content
        ↓
Step 5: Embed chunks (sentence-transformers)
        ↓
Step 6: Store in ChromaDB  ← NEXT
        ↓
Step 7: RAG Query Interface
```

---

## Completed Steps

### ✅ Step 1 — Chrome History Extraction
**File:** `history_extractor.py`  
**Output:** `history_last_{days}_days.json`

- Chrome stores history in SQLite at `%LOCALAPPDATA%\Google\Chrome\User Data\Profile 2\History`
- File must be copied before reading (Chrome locks it) → copy to `%TEMP%\chrome_history_copy.db`
- Chrome timestamp = microseconds since 1601-01-01
- SQL joins `visits` and `urls` tables, filters by `visit_time`
- CLI argument `days` passed via `argparse` → `python script.py 2`

---

### ✅ Step 2 — URL Deduplication & Cleaning
**File:** `process.py`  
**Output:** `history_last_{days}_days_clean.json`

Three-level deduplication:
1. Exact duplicate URLs
2. Fragment stripping (`#section`) via `urlunparse`
3. Query param cleaning — keep only `["v", "list", "t"]`, strip tracking params

URL filtering — skip domains: `mail.google.com`, `claude.ai`, `chatgpt.com`, `google.com`, `x.com`, etc.  
Skip patterns: `/logout`, `/login`, `/i/flow/`, `chrome-extension://`

**Result:** 33 clean URLs from 1 day of history

---

### ✅ Step 3 — Content Fetching
**File:** `Web_Extraction.py`  
**Output:** `Extracted_content.json`, `Future_actions.log`

- Library: `trafilatura` — `fetch_url()` + `extract()`
- YouTube URLs → logged as `[SKIPPED-youtube]` INFO, skipped (needs transcript API later)
- Failed/short content → logged as `[FAILED]` WARNING, skipped
- Minimum content length: 200 characters

**Pipeline counters:**
```
Total input:     33 URLs
YouTube skipped:  7
Failed/short:    12
Successfully extracted: 14
```

**Logging setup:**
```python
logging.basicConfig(filename='Future_actions.log', encoding='utf-8', level=logging.INFO)
logger = logging.getLogger(__name__)
```

---

### ✅ Step 4 — Chunking
**File:** `chunking.py`  
**Output:** `Chunks_filtered.json`

- Strategy: Fixed-size chunking with overlap
- Chunk size: 500 characters
- Overlap: 100 characters (step = 400)
- Minimum chunk length: 30 characters (short tail chunks filtered out)

Each chunk stored as:
```json
{
  "url": "...",
  "title": "...",
  "timestamp": "...",
  "chunk_index": 0,
  "chunk_text": "..."
}
```

**Result:** 484 clean chunks from 14 documents

---

### ✅ Step 5 — Embeddings
**File:** `Embeddings.py`  
**Output:** `Chunks_embedded.json`

- Library: `sentence-transformers`
- Model: `all-MiniLM-L6-v2` (local, no API key, 384 dimensions)
- All 484 chunks encoded in one batch call via `model.encode(chunk_texts)`
- Embedding stored as `vector` field using `.tolist()` for JSON serialization

Each embedded chunk:
```json
{
  "url": "...",
  "title": "...",
  "timestamp": "...",
  "chunk_index": 0,
  "chunk_text": "...",
  "vector": [0.019, -0.047, ...]
}
```

**Embedding shape:** `(484, 384)` — 484 chunks × 384 dimensions

---

## File Inventory

| File | Description |
|------|-------------|
| `history_last_1_days.json` | Raw extracted Chrome history |
| `history_last_1_days_clean.json` | Deduplicated, filtered URLs (33) |
| `Extracted_content.json` | Fetched page content (14 docs) |
| `Future_actions.log` | YouTube skips (INFO) + fetch failures (WARNING) |
| `Chunks_filtered.json` | 484 chunks with metadata |
| `Chunks_embedded.json` | 484 chunks with 384-dim vectors |

---

## Key Technical Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Language | Python | Richer NLP ecosystem |
| Content fetcher | trafilatura | Simple, no JS rendering needed for most pages |
| Chunking strategy | Fixed-size + overlap | Simple, effective for technical docs |
| Embedding model | all-MiniLM-L6-v2 | Local, fast, 384 dims, good quality |
| Vector store (next) | ChromaDB | Persists to disk, no server needed |

---

## Known Limitations

- **JS-rendered pages** (e.g. pinecone.io, 100xschool.in) return None — need Playwright in Phase 2
- **Auth-gated pages** (e.g. vizuara.ai course lessons) cannot be fetched — Phase 2 Chrome extension runs inside logged-in browser
- **Amazon** blocks with 503 errors — anti-scraping, expected
- **YouTube** content skipped — will use `youtube-transcript-api` later

---

## Next Steps

- [ ] **Step 6** — Store embeddings in ChromaDB (vector store)
- [ ] **Step 7** — RAG query interface (semantic search + LLM answer)
- [ ] **Phase 2** — Chrome extension wrapping the pipeline

---

## Lessons Learned

- Never modify a list while iterating over it — use list comprehension instead
- `json.dump` cannot serialize numpy `ndarray` — use `.tolist()` not `list()`
- `basicConfig(level=logging.INFO)` captures both INFO and WARNING; setting WARNING drops INFO messages
- `continue` placement inside loops is critical — must be inside the correct `if` block
- Always verify math — input count should equal sum of all outcomes
