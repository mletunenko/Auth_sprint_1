import random
import string


def gen_random_email():
    return f"{''.join(random.choices(string.ascii_letters,k=10))}@example.com"

def gen_random_password():
    return "".join(random.choices(string.ascii_letters,k=6))