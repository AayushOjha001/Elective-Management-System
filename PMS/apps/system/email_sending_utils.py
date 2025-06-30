from django.conf import settings
from django.core.mail import EmailMessage


email_body_template = 'Hello %s, we have created your account at Elective Priority Management System ' \
                      'with username: %s and password: %s. Logon to %s and enter your priority before the deadline.'


def send_account_creation_email(user_data, password):
    first_name = user_data.get('first_name')
    last_name = user_data.get('last_name')
    username = user_data.get('username')
    user_email = user_data.get('email')
    stream = user_data.get('stream')
    # user_email = 'theabhinavdev@gmail.com'
    title = 'Account created at Elective Priority Management System'
    email_body = email_body_template % (first_name, username, password, settings.WEBSITE_LINK)
    email = EmailMessage(title, email_body, to=[user_email, ])
    print(email_body)
    # email.send()
