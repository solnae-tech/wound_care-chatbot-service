import json
import os

RESULT_FILE = "data/results.json"

# Ensure file exists
if not os.path.exists(RESULT_FILE):
    with open(RESULT_FILE, "w") as f:
        json.dump({}, f)


def save_result(task_id, result):
    with open(RESULT_FILE, "r") as f:
        data = json.load(f)

    data[task_id] = result

    with open(RESULT_FILE, "w") as f:
        json.dump(data, f)


def get_result(task_id):
    with open(RESULT_FILE, "r") as f:
        data = json.load(f)

    return data.get(task_id)