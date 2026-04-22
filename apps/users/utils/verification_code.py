from time import sleep

from celery import shared_task


@shared_task
def send_verification_code(user_id):
    from apps.users.models.users import User

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        print(f"User with id {user_id} not found.")
        return

    code = user.generate_verification_code()
    sleep(3)  # Simulate delay for sending code
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


@shared_task
def hello():
    print("Hello, this is a test task to verify Celery is working!")