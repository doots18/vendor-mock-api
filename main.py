from fastapi import FastAPI, Path, Body
from fastapi.responses import JSONResponse
from faker import Faker
from datetime import datetime

app = FastAPI(
    title="Vendor API",
    version="1.0.0",
    description="Mock Vendor Service for FlutterFlow"
)

fake = Faker()

# Function to generate a random vendor
def random_vendor(vendor_id: str):
    now = datetime.utcnow().isoformat() + "Z"
    return {
        "id": vendor_id,
        "workflowId": fake.uuid4(),
        "legalName": fake.company(),
        "tradeName": fake.company_suffix(),
        "pan": fake.bothify(text="?????####?"),
        "panVerified": True,
        "gstin": fake.bothify(text="##?????####?#?#"),
        "gstinVerified": True,
        "entityType": "PROPRIETORSHIP",
        "contactPersonName": fake.name(),
        "contactEmail": fake.email(),
        "contactPhone": fake.msisdn(),
        "registeredAddress": {
            "addressLine1": fake.street_address(),
            "city": fake.city(),
            "state": fake.state(),
            "pincode": fake.postcode(),
            "country": "India"
        },
        "category": "FOS",
        "dueDiligenceStatus": "NOT_STARTED",
        "state": "DRAFT",
        "createdAt": now,
        "updatedAt": now,
        "material": True
    }

# ---------------- GET ENDPOINTS ----------------

@app.get("/", response_class=JSONResponse)
def health():
    return {"status": "API is running"}

@app.get(
    "/api/v1/vendors/{id}",
    response_class=JSONResponse
)
def get_vendor_by_id(id: str = Path(..., description="Vendor ID")):
    return JSONResponse(
        content=random_vendor(id),
        headers={"Content-Type": "application/json"}
    )

@app.get(
    "/api/v1/vendors/state/{state}",
    response_class=JSONResponse
)
def get_vendors_by_state(state: str):
    vendors = [random_vendor(fake.uuid4()) for _ in range(3)]
    # Override the state
    for v in vendors:
        v["state"] = state
    return JSONResponse(
        content=vendors,
        headers={"Content-Type": "application/json"}
    )

# ---------------- POST ENDPOINT ----------------

@app.post(
    "/api/v1/vendors/{id}/state",
    response_class=JSONResponse
)
def update_vendor_state(
    id: str = Path(..., description="Vendor ID"),
    payload: dict = Body(..., description="State update payload")
):
    """
    Updates only the `state` of a vendor.
    Payload should be like: {"state": "SUBMITTED"}
    Returns the full vendor JSON.
    """
    vendor = random_vendor(id)
    
    # Update state if provided
    new_state = payload.get("state")
    if new_state:
        vendor["state"] = new_state
        vendor["updatedAt"] = datetime.utcnow().isoformat() + "Z"

    return JSONResponse(
        content=vendor,
        headers={"Content-Type": "application/json"}
    )

