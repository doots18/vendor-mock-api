from fastapi import FastAPI, Path, Body
from fastapi.responses import JSONResponse
from faker import Faker
from datetime import datetime

app = FastAPI(
    title="Vendor API",
    version="1.0.0",
    description="Mock Vendor & Due Diligence Service for FlutterFlow"
)

fake = Faker()

# ---------------- In-memory stores ----------------
VENDORS_STORE = {}
DUE_DILIGENCE_STORE = {}

# ---------------- Helpers ----------------

def now_utc():
    return datetime.utcnow().isoformat() + "Z"


def random_vendor(vendor_id: str):
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
        "createdAt": now_utc(),
        "updatedAt": now_utc(),
        "material": True
    }


def get_or_create_vendor(vendor_id: str):
    if vendor_id not in VENDORS_STORE:
        VENDORS_STORE[vendor_id] = random_vendor(vendor_id)
    return VENDORS_STORE[vendor_id]


def generate_checks():
    return [
        {
            "checkType": "NAME_SCREENING",
            "status": "NOT_STARTED",
            "inputValue": "string",
            "passed": True,
            "resultCode": "NO_MATCH",
            "resultMessage": "No adverse records found",
            "rawResponse": {},
            "matchedName": "string",
            "matchScore": 95,
            "cibilScore": 0,
            "riskCategory": "LOW",
            "initiatedAt": now_utc(),
            "completedAt": now_utc(),
            "attemptCount": 1,
            "lastError": None
        }
    ]


def create_due_diligence(vendor: dict):
    return {
        "id": fake.uuid4(),
        "vendorId": vendor["id"],
        "vendorName": vendor["legalName"],
        "vendorPan": vendor["pan"],
        "subcontractorId": fake.uuid4(),
        "executiveId": fake.uuid4(),
        "overallStatus": "NOT_STARTED",
        "passed": True,
        "overallRemarks": "Due diligence initiated",
        "checks": generate_checks(),
        "exceptionRequested": False,
        "exceptionReason": None,
        "exceptionApprovedBy": None,
        "exceptionApprovedAt": None,
        "exceptionApproved": False,
        "initiatedBy": "SYSTEM",
        "createdAt": now_utc(),
        "updatedAt": now_utc(),
        "completedAt": None
    }


def get_or_create_due_diligence(vendor_id: str):
    if vendor_id not in DUE_DILIGENCE_STORE:
        vendor = get_or_create_vendor(vendor_id)
        DUE_DILIGENCE_STORE[vendor_id] = create_due_diligence(vendor)
    return DUE_DILIGENCE_STORE[vendor_id]

# ---------------- Health ----------------

@app.get("/", response_class=JSONResponse)
def health():
    return {"status": "API is running"}

# ---------------- Vendor APIs ----------------

@app.get("/api/v1/vendors/{id}", response_class=JSONResponse)
def get_vendor_by_id(id: str = Path(...)):
    vendor = get_or_create_vendor(id)
    return JSONResponse(content=vendor)


@app.get("/api/v1/vendors/state/{state}", response_class=JSONResponse)
def get_vendors_by_state(state: str):
    vendors = []
    for _ in range(3):
        vendor_id = fake.uuid4()
        vendor = get_or_create_vendor(vendor_id)
        vendor["state"] = state
        vendors.append(vendor)
    return JSONResponse(content=vendors)


@app.post("/api/v1/vendors/{id}/state", response_class=JSONResponse)
def update_vendor_state(
    id: str = Path(...),
    payload: dict = Body(...)
):
    vendor = get_or_create_vendor(id)
    if "state" in payload:
        vendor["state"] = payload["state"]
        vendor["updatedAt"] = now_utc()
    return JSONResponse(content=vendor)

# ---------------- Due Diligence APIs ----------------

@app.get(
    "/api/v1/due-diligence/vendor/{vendorId}",
    response_class=JSONResponse
)
def get_due_diligence(vendorId: str = Path(...)):
    due_diligence = get_or_create_due_diligence(vendorId)
    return JSONResponse(content=due_diligence)
