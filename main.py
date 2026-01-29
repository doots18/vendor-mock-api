from fastapi import FastAPI, Path, Body
from fastapi.responses import JSONResponse
from faker import Faker
from datetime import datetime

app = FastAPI(
    title="Vendor Mock API",
    version="1.0.0",
    description="Mock Vendor, Due Diligence & TPRM Assessment API"
)

fake = Faker()

# ---------------- In-memory stores ----------------
VENDORS_STORE = {}
DUE_DILIGENCE_STORE = {}
ASSESSMENTS_STORE = {}
ASSESSMENT_RESPONSES_STORE = {}

# ---------------- Helpers ----------------

def now_utc():
    return datetime.utcnow().isoformat() + "Z"

# ---------------- Vendor ----------------

def random_vendor(vendor_id: str):
    return {
        "id": vendor_id,
        "workflowId": fake.uuid4(),
        "legalName": fake.company(),
        "tradeName": fake.company_suffix(),
        "pan": fake.bothify("?????####?"),
        "panVerified": True,
        "gstin": fake.bothify("##?????####?#?#"),
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

@app.get("/")
def health():
    return {"status": "API is running"}

@app.get("/api/v1/vendors/{id}")
def get_vendor(id: str = Path(...)):
    return JSONResponse(content=get_or_create_vendor(id))

# ---------------- Due Diligence ----------------

def create_due_diligence(vendor):
    return {
        "id": fake.uuid4(),
        "vendorId": vendor["id"],
        "vendorName": vendor["legalName"],
        "overallStatus": "NOT_STARTED",
        "checks": [],
        "createdAt": now_utc(),
        "updatedAt": now_utc()
    }

@app.get("/api/v1/due-diligence/vendor/{vendorId}")
def get_due_diligence(vendorId: str):
    if vendorId not in DUE_DILIGENCE_STORE:
        vendor = get_or_create_vendor(vendorId)
        DUE_DILIGENCE_STORE[vendorId] = create_due_diligence(vendor)
    return JSONResponse(content=DUE_DILIGENCE_STORE[vendorId])

# ---------------- TPRM Assessment ----------------

def generate_assessment(payload: dict):
    now = now_utc()
    assessment_id = fake.uuid4()
    response_id = fake.uuid4()

    return {
        "id": assessment_id,
        "workflowId": fake.uuid4(),
        "type": "TPRM_A",
        "questionnaireId": fake.uuid4(),
        "questionnaireVersion": "1.0",
        "vendorId": payload.get("vendorId"),
        "vendorName": payload.get("vendorName"),
        "engagementId": payload.get("engagementId"),
        "engagementName": payload.get("engagementName"),
        "activityId": payload.get("activityId"),
        "activityName": payload.get("activityName"),
        "activityCategory": payload.get("activityCategory"),
        "assessmentPeriod": payload.get("assessmentPeriod"),
        "dueDate": payload.get("dueDate", now),
        "assessmentYear": datetime.utcnow().year,
        "businessUnitId": payload.get("businessUnitId"),
        "creatorId": fake.uuid4(),
        "creatorName": fake.name(),
        "assigneeId": fake.uuid4(),
        "assigneeName": fake.name(),
        "assigneeEmail": fake.email(),
        "reviewerId": fake.uuid4(),
        "reviewerName": fake.name(),
        "responseId": response_id,
        "score": None,
        "state": "DRAFT",
        "approvals": [],
        "findings": [],
        "actionItems": [],
        "documentIds": [],
        "createdAt": now,
        "updatedAt": now,
        "submittedAt": None,
        "reviewedAt": None,
        "completedAt": None,
        "annual": payload.get("isAnnual", True)
    }

@app.post("/api/v1/assessments/tprm-a", response_class=JSONResponse)
def create_tprm_assessment(payload: dict = Body(...)):
    assessment = generate_assessment(payload)
    ASSESSMENTS_STORE[assessment["id"]] = assessment
    return JSONResponse(content=assessment)

# ---------------- Assessment Response ----------------

@app.post(
    "/api/v1/assessments/{response_id}/response",
    response_class=JSONResponse
)
def create_assessment_response(
    response_id: str = Path(...),
    payload: dict = Body(...)
):
    now = now_utc()

    response_obj = {
        "id": response_id,
        "questionnaireId": payload.get("questionnaireId"),
        "questionnaireCode": payload.get("questionnaireCode", "TPRM_A"),
        "questionnaireVersion": payload.get("questionnaireVersion", "1.0"),
        "assessmentId": payload.get("assessmentId"),
        "assessmentType": payload.get("assessmentType", "TPRM_A"),
        "vendorId": payload.get("vendorId"),
        "engagementId": payload.get("engagementId"),
        "respondentId": payload.get("respondentId"),
        "respondentName": payload.get("respondentName"),
        "respondentRole": payload.get("respondentRole"),
        "respondentEmail": payload.get("respondentEmail"),
        "sectionResponses": payload.get("sectionResponses", []),
        "scored": payload.get("scored", True),
        "scoreResult": payload.get("scoreResult"),
        "state": payload.get("state", "DRAFT"),
        "reviewerId": payload.get("reviewerId"),
        "reviewerName": payload.get("reviewerName"),
        "reviewComments": payload.get("reviewComments"),
        "reviewedAt": payload.get("reviewedAt"),
        "createdAt": payload.get("createdAt", now),
        "updatedAt": now,
        "submittedAt": payload.get("submittedAt"),
        "completedAt": payload.get("completedAt")
    }

    ASSESSMENT_RESPONSES_STORE[response_id] = response_obj

    assessment_id = payload.get("assessmentId")
    if assessment_id in ASSESSMENTS_STORE:
        ASSESSMENTS_STORE[assessment_id]["state"] = "RESPONSE_SUBMITTED"
        ASSESSMENTS_STORE[assessment_id]["updatedAt"] = now

    return JSONResponse(content=response_obj)
