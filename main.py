from fastapi import FastAPI, Path
from fastapi.responses import JSONResponse
from faker import Faker
import random
from datetime import datetime

app = FastAPI(
    title="Vendor API",
    version="1.0.0",
    description="Mock Vendor Service"
)

fake = Faker()

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

@app.get(
    "/",
    response_class=JSONResponse,
    status_code=200
)
def health():
    return {"status": "API is running"}

@app.get(
    "/api/v1/vendors/{id}",
    response_class=JSONResponse,
    status_code=200,
    responses={
        200: {
            "content": {
                "application/json": {}
            }
        }
    }
)
def get_vendor_by_id(
    id: str = Path(..., description="Vendor ID")
):
    return JSONResponse(
        content=random_vendor(id),
        headers={
            "Content-Type": "application/json"
        }
    )

@app.get(
    "/api/v1/vendors/state/{state}",
    response_class=JSONResponse,
    status_code=200
)
def get_vendors_by_state(state: str):
    vendors = [random_vendor(fake.uuid4()) for _ in range(3)]
    return JSONResponse(
        content=vendors,
        headers={
            "Content-Type": "application/json"
        }
    )
