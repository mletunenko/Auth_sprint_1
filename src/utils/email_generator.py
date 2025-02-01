import random
import string


def generate_email():
    random_string = "".join(random.choices(string.ascii_lowercase, k=10))
    return random_string + "@mail.com"
