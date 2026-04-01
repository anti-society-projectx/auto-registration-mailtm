import string
import random
from pathlib import Path


def random_string(length=10):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

def save_result(
        email: str,
        password: str,
        path: Path = "emails_output.txt"
):
    with open(path, "a") as f:
        f.write(f"{email}:{password}\n")
