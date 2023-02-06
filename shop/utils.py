from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator as token_generator


# counting user discount in loyalty program
def discount(money_amount: float) -> int:
    if money_amount <= 500:
        return 5
    elif 500 <= money_amount <= 1000:
        return 6
    elif 1000 <= money_amount <= 2000:
        return 7
    else:
        return 10


def send_email_verify(request, user):
    current_site = get_current_site(request)
    context = {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.id)),
        'token': token_generator.make_token(user),
        "protocol": "http"
    }
    message = render_to_string(
        'shop/email_verify.html',
        context=context
        )
    email = EmailMessage(
        'Verify email',
        message,
        to=[user.email]
    )
    email.send()


def send_email_confirm_order(request, customer, order, admin):
    current_site = get_current_site(request)
    order_id = customer['order_id']
    context = {
        'first_name': customer['first_name'],
        'last_name': customer['last_name'],
        'address': customer['address'],
        'phone_number': customer['phone_number'],
        'email': customer['email'],
        'total': customer['total'],
        'order_id': order_id,
        'domain': current_site.domain,
        'order': order,
        'uid': urlsafe_base64_encode(force_bytes(order_id)),
        'token': token_generator.make_token(admin),
        "protocol": "http"
    }
    message = render_to_string(
        'shop/email_confirm_order.html',
        context=context
        )
    email = EmailMessage(
        'Confirmation of an order',
        message,
        to=[admin.email]
    )
    email.send()
