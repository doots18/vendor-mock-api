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

# ---------------- In-memory store ----------------
VENDORS_STORE = {}

# ---------------- Helper ----------------
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

def get_or_create_vendor(vendor_id: str):
    """Return vendor from store or create a new one"""
    if vendor_id not in VENDORS_STORE:
        VENDORS_STORE[vendor_id] = random_vendor(vendor_id)
    return VENDORS_STORE[vendor_id]

# ---------------- GET ENDPOINTS ----------------
@app.get("/", response_class=JSONResponse)
def health():
    return {"status": "API is running"}

@app.get("/api/v1/vendors/{id}", response_class=JSONResponse)
def get_vendor_by_id(id: str = Path(..., description="Vendor ID")):
    vendor = get_or_create_vendor(id)
    return JSONResponse(content=vendor, headers={"Content-Type": "application/json"})

@app.get("/api/v1/vendors/state/{state}", response_class=JSONResponse)
def get_vendors_by_state(state: str):
    vendors = []
    for _ in range(3):
        vendor_id = fake.uuid4()
        vendor = get_or_create_vendor(vendor_id)
        vendor["state"] = state  # override state
        vendors.append(vendor)
    return JSONResponse(content=vendors, headers={"Content-Type": "application/json"})

# ---------------- POST ENDPOINT ----------------
@app.post("/api/v1/vendors/{id}/state", response_class=JSONResponse)
def update_vendor_state(
    id: str = Path(..., description="Vendor ID"),
    payload: dict = Body(..., description="State update payload")
):
    """
    Updates only the `state` of a vendor.
    Payload should be like: {"state": "SUBMITTED"}
    Returns the full vendor JSON.
    """
    vendor = get_or_create_vendor(id)
    new_state = payload.get("state")
    if new_state:
        vendor["state"] = new_state
        vendor["updatedAt"] = datetime.utcnow().isoformat() + "Z"
    return JSONResponse(content=vendor, headers={"Content-Type": "application/json"})
