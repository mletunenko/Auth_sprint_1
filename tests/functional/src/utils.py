import random
import string


def gen_random_email() -> str:
    return f"{''.join(random.choices(string.ascii_letters,k=10))}@example.com"

def gen_random_password() -> str:
    return "".join(random.choices(string.ascii_letters,k=6))