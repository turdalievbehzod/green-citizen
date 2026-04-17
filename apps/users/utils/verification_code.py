def generate_verification_code(length=6):
    """Generate a random verification code consisting of digits."""
    import random
    import string

    characters = string.digits
    verification_code = ''.join(random.choice(characters) for _ in range(length))
    return verification_code


def send_verification_code(user, code):
    """Send the verification code to the user's phone number or email."""
    # This is a placeholder function. You would implement the actual sending logic here,
    # such as using an SMS gateway for phone numbers or an email service for email addresses.
    if user.phone_number:
        print(f"Sending verification code {code} to phone number {user.phone_number}")
        # Implement SMS sending logic here
    elif user.email:
        print(f"Sending verification code {code} to email {user.email}")
        # Implement email sending logic here
    else:
        print("No contact information available to send the verification code.")