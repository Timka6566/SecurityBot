import string
import random


def generate_easy() -> str:
    length = 8
    chars = string.ascii_letters
    return ''.join(random.choice(chars) for _ in range(length))


def generate_medium() -> str:
    length = 12
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def generate_strong() -> str:
    length = 16
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))
