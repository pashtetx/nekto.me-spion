import hashlib
import time
import random

def generate_webagent(token: str, user_id: int, create_time: int) -> str:
    payload = token + "1AXYINmuWLLQk1iX" + "NAd0NHvxy" + str(user_id) + str(create_time)
    return hashlib.sha256(payload.encode())\
        .hexdigest()

def generate_random_id() -> str:
    return str(time.time() * 1000) + str(random.random())