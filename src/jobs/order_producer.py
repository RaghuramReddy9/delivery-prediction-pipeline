import json
import time
import random
from datetime import datetime
from config.settings import STREAM_FILE
from src.utils.logger import log

warehouses = ["SAN_JOSE", "LOS_ANGELES", "DALLAS", "MIAMI", "NEW_YORK"] 
carriers = ["UPS", "FEDEX", "DHL", "USPS"]

def generate_order_event():
    return {
        "order_id": f"O{random.randint(1000, 9999)}",
        "warehouse": random.choice(warehouses),
        "customer_zip": str(random.randint(90000, 99999)),
        "weight_kg": round(random.uniform(0.5, 10.0), 2),
        "carrier": random.choice(carriers),
        "event_time": datetime.utcnow().isoformat()
    }


def run_producer():
    while True:
        event = generate_order_event()

        with open(STREAM_FILE, "a") as f:
            f.write(json.dumps(event) + "\n")

        log(f"Produced event: {event}")

        time.sleep(1)  # One event per second


if __name__ == "__main__":
    run_producer()