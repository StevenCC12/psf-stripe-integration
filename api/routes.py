from fastapi import APIRouter, Request, HTTPException, Header
from core.redis import get_redis
from services.stripe_service import create_checkout_session, verify_webhook_signature

router = APIRouter()

@router.post("/create-embedded-checkout")
async def handle_create_checkout():
    # In a real scenario, you'd accept a Pydantic model with product details here
    session_data = create_checkout_session()
    return session_data

@router.post("/stripe-webhook-listener")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe signature")

    # 1. Read raw body for cryptographic validation
    payload = await request.body()

    # 2. Verify Signature
    try:
        event = verify_webhook_signature(payload, stripe_signature)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    event_id = event["id"]
    event_type = event["type"]
    print(f"INFO: Received Webhook Event: {event_type} (ID: {event_id})")

    # 3. Idempotency Check using Redis
    redis_client = get_redis()
    # nx=True means "Set ONLY IF it does not exist". ex=86400 expires it in 24h.
    is_new_event = await redis_client.set(f"stripe_event:{event_id}", "processing", nx=True, ex=86400)
    
    if not is_new_event:
        print(f"INFO: Idempotency catch. Event {event_id} already processed. Ignoring.")
        return {"status": "success", "message": "Duplicate event ignored"}

    # 4. Handle the specific event
    if event_type == "invoice.paid":
        invoice_obj = event["data"]["object"]
        customer_email = invoice_obj.get("customer_email")
        hosted_invoice_url = invoice_obj.get("hosted_invoice_url")
        
        print(f"ACTION: Dispatch email to {customer_email} with link {hosted_invoice_url}")
        print(f"ACTION: Sync purchase tag to HighLevel for {customer_email}")
        
        # TODO: Await email dispatch
        # TODO: Await GHL sync

    # Return 200 OK to Stripe quickly so it stops retrying
    return {"status": "success"}