import random
import string


def generate_password(length: int = 12) -> str:
    """Generate a random password containing uppercase, lowercase, digits, and special characters."""
    if length < 4:
        length = 4

    password = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice(string.punctuation),
    ]

    remaining = length - len(password)
    all_characters = string.ascii_letters + string.digits + string.punctuation
    password.extend(random.choices(all_characters, k=remaining))

    random.shuffle(password)
    return "".join(password)
