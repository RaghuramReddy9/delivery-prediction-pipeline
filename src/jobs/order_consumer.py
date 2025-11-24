import json
import os 
import time
from config.settings import STREAM_FILE, RAW_OUTPUT_PATH
from src.utils.logger import log


offset = 0

def run_consumer():
    global offset

    while True:
        if os.path.exists(STREAM_FILE):
            with open(STREAM_FILE, "r") as f:
                f.seek(offset)
                new_lines = f.readlines()
                offset = f.tell()

                for line in new_lines:
                    event = json.loads(line.strip())
                    log(f"Consumed event: {event}")

                    with open(RAW_OUTPUT_PATH, "a") as rawf:
                        rawf.write(json.dumps(event) + "\n")

        time.sleep(1)


if __name__ == "__main__":
    run_consumer()
