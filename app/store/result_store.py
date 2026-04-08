import json
import os
import msvcrt
import time

RESULT_FILE = "data/results.json"

# Ensure file exists
if not os.path.exists(RESULT_FILE):
    with open(RESULT_FILE, "w") as f:
        json.dump({}, f)


def acquire_lock(file_handle):
    """Acquire exclusive lock on file (Windows)"""
    max_retries = 10
    retry_delay = 0.1
    
    for attempt in range(max_retries):
        try:
            msvcrt.locking(file_handle.fileno(), msvcrt.LK_NBLCK, 1)
            return True
        except IOError:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise
    return False


def release_lock(file_handle):
    """Release exclusive lock on file (Windows)"""
    try:
        msvcrt.locking(file_handle.fileno(), msvcrt.LK_UNLCK, 1)
    except IOError:
        pass


def save_result(task_id, result):
    """Save result with file locking to prevent race conditions"""
    with open(RESULT_FILE, "r+") as f:
        acquire_lock(f)
        try:
            f.seek(0)
            data = json.load(f)
            data[task_id] = result
            
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=2)
        finally:
            release_lock(f)


def get_result(task_id):
    """Get result with file locking"""
    with open(RESULT_FILE, "r") as f:
        acquire_lock(f)
        try:
            data = json.load(f)
            return data.get(task_id)
        finally:
            release_lock(f)