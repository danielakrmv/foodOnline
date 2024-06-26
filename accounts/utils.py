from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.conf import settings


def detectUser(user):
    """
    Detects the type of user based on their role and returns the corresponding redirect URL.

    Args:
        user: The user object whose role needs to be detected.

    Returns:
        str: A URL string to redirect the user to the appropriate dashboard.
    """
    if user.role == 1:
        redirectUrl = 'vendorDashboard'
        return redirectUrl
    elif user.role == 2:
        redirectUrl = 'custDashboard'
        return redirectUrl
    elif user.role == None and user.is_superadmin:
        redirectUrl = '/admin'
        return redirectUrl

def send_verification_email(request, user, mail_subject, email_template):
    """
    Sends a verification email to the specified user.

    Args:
        request: The HTTP request object.
        user: The user object to whom the verification email is to be sent.
        mail_subject: The subject of the email.
        email_template: The path to the email template to be used.

    Returns:
        None
    """
    from_email = settings.DEFAULT_FROM_EMAIL
    # Retrieve the current site from the request to include in the email.
    current_site = get_current_site(request)

    # Create the email message:
    # user.pk - The user's primary key. This is a unique identifier that Django automatically generates for each user.
    # force_bytes(user.pk): Convert the primary key into bytes.
    # urlsafe_base64_encode(...): Encodes the bytes into base64 format, which is safe for use in URLs.
    # `default_token_generator.make_token(user): Generates a temporary verification token based on the state of the user.
    message = render_to_string(email_template, {
        'user': user, # the user object.
        'domain': current_site, # The domain of the current site.
        'uid': urlsafe_base64_encode(force_bytes(user.pk)), # A unique base64-encoded identifier of the user.
        'token': default_token_generator.make_token(user), # Verification token generated by default_token_generator.
    })
    to_email = user.email
    # Create the email object with a specified subject, message, sender, and recipient.
    mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
    # Set the email content type as HTML.
    mail.content_subtype = "html"
    mail.send()


def send_notification(mail_subject, mail_template, context):
    """
    Sends a notification email using the specified template and context.

    Args:
        mail_subject: The subject of the email.
        mail_template: The path to the email template to be used.
        context: A dictionary containing context variables for rendering the email template.

    Returns:
        None
    """
    from_email = settings.DEFAULT_FROM_EMAIL
    message = render_to_string(mail_template, context)
    # to_email = context['user'].email
    if(isinstance(context['to_email'], str)):
        to_email = []
        to_email.append(context['to_email'])
    else:
        to_email = context['to_email']
    mail = EmailMessage(mail_subject, message, from_email, to=to_email)
    mail.content_subtype = "html"
    mail.send()
