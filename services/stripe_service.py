import stripe
from core.config import settings

# Initialize Stripe with the backend restricted key
stripe.api_key = settings.STRIPE_RESTRICTED_KEY

def create_checkout_session():
    """
    Creates an embedded checkout session forcing invoice creation.
    """
    try:
        session = stripe.checkout.Session.create(
            ui_mode="embedded",
            # We must enable invoice creation for the PDF receipt
            invoice_creation={"enabled": True},
            payment_method_types=["card", "klarna"],
            # Localize the invoice to Swedish
            customer_email="test@example.com", # In reality, pass this from frontend if available
            locale="sv", 
            line_items=[
                {
                    "price_data": {
                        "currency": "sek",
                        "product_data": {"name": "Course Access"},
                        "unit_amount": 500000, # 5000.00 SEK
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            return_url="https://your-domain.com/success?session_id={CHECKOUT_SESSION_ID}",
        )
        return {"client_secret": session.client_secret}
    except Exception as e:
        print(f"ERROR: Failed to create Stripe session: {e}")
        raise

def verify_webhook_signature(payload: bytes, sig_header: str):
    """
    Cryptographically verifies the webhook came from Stripe.
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        return event
    except ValueError:
        raise ValueError("Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise ValueError("Invalid signature")