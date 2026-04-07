
# NEW - adds project root to Python's search path so config/ can be found
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))



import os
from config.config import CHROME_PROFILE
# We are doing 'profile=CHROME_PROFILE' this inside the function as an argument so that
# it becomes the default value unless someone overwrites it inside the body of the function
def get_chrome_history_path(profile=CHROME_PROFILE):
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:   # Handles if None is returned from os.environ.get("LOCALAPPDATA")
        raise EnvironmentError("LOCALAPPDATA not found. Are you on Windows?")
    history_path= os.path.join(
        local_app_data,
        "Google",
        "Chrome",
        "User Data",
        profile,
        "History"
    )
    if os.path.exists(history_path):
        return history_path
    else:
         raise EnvironmentError("The path for chrome history not found !!")


import tempfile
import shutil
def copy_history_path(source_path):
    try:
         temp_dir = tempfile.gettempdir()
    except FileNotFoundError as e:
        print(f'Temp File location does not exist, error its showing is is {e}')
        raise
    destination = os.path.join(temp_dir, "chrome_history_copy.db")
    try:
        shutil.copy2(source_path, destination)# print('snapshot  created at ', destination)
    except PermissionError as e:
        print(f'History File is locked {e}')
        raise 
    except OSError as e:
        print(f"Disc full or other OS related Isuee. The error is {e}")
        raise 
    return destination

#!Note :# raise re-throws the caught error to the caller,
#!so the pipeline stops instead of silently continuing with bad data


#! Read the file through sqlite3 and 


from config.config import CHROME_PROFILE, NUM_DAYS ,OUTPUT_DIR # CHANGED - added NUM_DAYS
import sqlite3
days = NUM_DAYS
def database_connection_extraction(destination,days):
    if not isinstance(days, int):
        raise TypeError("days must be an integer")
    if days <= 0:
        raise ValueError("days must be positive")
    with sqlite3.connect(destination) as conn:
        cursor=conn.cursor()
        query = f"""
        SELECT urls.url, urls.title, visits.visit_time
        FROM visits
        JOIN urls ON visits.url = urls.id
        WHERE visits.visit_time >= 
            (strftime('%s','now','-{days} days') + 11644473600) * 1000000
        ORDER BY visits.visit_time DESC
    """
        cursor.execute(query)
        rows = cursor.fetchall()
        if rows == []:
            print(f"No history found for the last {days} days")
        return rows

#! Every SQLite database contains a special internal table: sqlite_master
#! TO Get all the tables of chrome history DB 

from datetime import datetime, timedelta
def chrome_time_to_datetime(chrome_time):
    # Chrome epoch starts at 1601-01-01
    epoch_start = datetime(1601, 1, 1)
    return epoch_start + timedelta(microseconds=chrome_time)


def process_rows(rows):
    history_data = []
    for url, title, visit_time in rows:
        readable_time = chrome_time_to_datetime(visit_time)
        history_data.append({
            "url": url,
            "title": title,
            "timestamp": readable_time.strftime("%Y-%m-%d %H:%M:%S")
        })
    return history_data
import json


def file_writing(history_data, days, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"history_last_{days}_days.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(history_data, f, indent=4, ensure_ascii=False)
    print("JSON file saved successfully")
    return filename


#!-------------------------------------------------------------------------
#! NEW - Test block to verify all functions work end to end
if __name__ == "__main__":
    
    # NEW - Test block to verify all functions work end to end
    print("--- Function 1 ---")
    path = get_chrome_history_path()
    print(f"Path: {path}")

    print("\n--- Function 2 ---")
    copied_path = copy_history_path(path)
    print(f"Copied to: {copied_path}")

    print("\n--- Function 3 ---")
    rows = database_connection_extraction(copied_path, days)
    print(f"Rows fetched: {len(rows)}")

    print("\n--- Function 5 ---")
    history_data = process_rows(rows)
    if history_data:
        print(f"First item: {history_data[0]}")

    print("\n--- Function 6 ---")
    filename = file_writing(history_data, days)
    print(f"Saved to: {filename}")
