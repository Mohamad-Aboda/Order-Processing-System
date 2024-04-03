import requests
import json

from .models import OrderItem


def send_order_confirmation_email(sender_email: str, receiver_email: str, brevo_api_key: str, order):
    url = "https://api.brevo.com/v3/smtp/email"
    order_items = OrderItem.objects.filter(order=order)
    items_list = [f"{item.quantity}x {item.product.name}" for item in order_items]
    total_amount = order.total_amount

    payload = json.dumps(
        {
            "sender": {"name": "appgain", "email": sender_email},
            "to": [{"email": f"{receiver_email}"}],
            "subject": f'Order Confirmation - #{order.id}',
            "textContent": f"""
                            Hi {order.user.first_name},This email confirms your successful payment for Order #{order.id}.
                            Order details:
                            - Items:
                                {', '.join(items_list)}
                            - Total Amount: {total_amount} EGP

                            Thank you for your order!

                            Sincerely,

                            Mohamed Abdelhamid Store Team""",
        }
    )
    headers = {
        "accept": "application/json",
        "api-key": brevo_api_key,
        "content-type": "application/json",
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
