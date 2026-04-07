
#! Learnings----------------------------------------------------------
'''
Now, for Python to treat `config/` (which currently is just a folder) 
as a package you can import from, you need one thing inside that folder
 — an empty file called `__init__.py`. Without it, Python doesn't 
recognize the folder as importable.

So your config folder looks like:

config/
    __init__.py
    config.py
'''
#! Learnings---------------------------------------------------------------

'''
Therse is  a Python convention called constants.When a variable is in 
ALL_CAPS, it signals to every  developer reading the code: "this value is
set once and should never change during runtime.
'''

CHROME_PROFILE = "Profile 2"

# NUM_DAYS = 15

MEANINGFUL_PARAMS = ["v", "list", "t"]
# OUTPUT_DIR = "data"
'''
v — the video ID. In youtube.com/watch?v=abc123, abc123 identifies which video. Remove this and you lose the page entirely.
list — the playlist ID. In youtube.com/watch?v=abc123&list=PLxyz, PLxyz identifies which playlist the video is part of.
t — the timestamp. In youtube.com/watch?v=abc123&t=120, t=120 means "start at 2 minutes." This matters because if you bookmarked a specific moment, you want to keep that.

'''

SKIP_DOMAINS = [
    "mail.google.com",
    "claude.ai",
    "chatgpt.com",
    "gemini.google.com",
    "t.co",
    "google.com",
    "amazon",          # CHANGED - catches all Amazon domains
    "scaler.com",
    "notion.so",
    "x.com",
    "apps.apple.com",
    "grok.com",
]

SKIP_PATTERNS = [
    "/logout",
    "/login",
    "/i/flow/",
    "/aclk?",
    "chrome-extension://",
    "file://",          # local files
    "localhost",        # local dev servers
    "192.168.",         # local network
    "127.0.0.1",        # localhost IP
    "/robots.txt",      # robot files
    "accounts.google",  # login pages
]

MIN_CONTENT_LENGTH = 200


import os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(PROJECT_ROOT, "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "ERROR.log")
YT_LOG_FILE = os.path.join(LOG_DIR, "youtube_transcript.log")

YT_SLEEP_TIME = 10

CHUNK_SIZE = 500
CHUNK_STEP = 400
CHUNK_MIN_LENGTH = 30
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# CHROMA_PATH = "chroma"
COLLECTION_NAME = "mycollection"

QUERY_DISTANCE_THRESHOLD = 1.0
QUERY_N_RESULTS = 10\

#! Testing ------------------------------------------------------**----------------------
NUM_DAYS = 11       # CHANGED - small test instead of 15
OUTPUT_DIR = "data_test"  # CHANGED - separate folder so real data is untouched

CHROMA_PATH = "chroma_test"