from fastapi import FastAPI, Path, Body
from fastapi.responses import JSONResponse
from faker import Faker
from datetime import datetime

app = FastAPI(
    title="Vendor API",
    version="1.0.0",
    description="Mock Vendor, Due Diligence & TPRM Assessment Service for FlutterFlow"
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


@app.get("/", response_class=JSONResponse)
def health():
    return {"status": "API is running"}


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


# ---------------- Due Diligence ----------------

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


@app.get("/api/v1/due-diligence/vendor/{vendorId}", response_class=JSONResponse)
def get_due_diligence(vendorId: str = Path(...)):
    due_diligence = get_or_create_due_diligence(vendorId)
    return JSONResponse(content=due_diligence)


# ---------------- TPRM Assessments ----------------

def generate_assessment(input_data: dict):
    now = now_utc()
    assessment_id = fake.uuid4()
    return {
        "id": assessment_id,
        "workflowId": fake.uuid4(),
        "type": "TPRM_A",
        "questionnaireId": fake.uuid4(),
        "questionnaireVersion": "1.0",
        "vendorId": input_data.get("vendorId"),
        "vendorName": input_data.get("vendorName"),
        "engagementId": input_data.get("engagementId"),
        "engagementName": input_data.get("engagementName"),
        "activityId": input_data.get("activityId"),
        "activityName": input_data.get("activityName"),
        "activityCategory": input_data.get("activityCategory"),
        "assessmentPeriod": input_data.get("assessmentPeriod"),
        "dueDate": input_data.get("dueDate", now),
        "assessmentYear": datetime.utcnow().year,
        "businessUnitId": input_data.get("businessUnitId"),
        "creatorId": fake.uuid4(),
        "creatorName": fake.name(),
        "assigneeId": fake.uuid4(),
        "assigneeName": fake.name(),
        "assigneeEmail": fake.email(),
        "reviewerId": fake.uuid4(),
        "reviewerName": fake.name(),
        "responseId": fake.uuid4(),
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
        "annual": input_data.get("isAnnual", True)
    }


@app.post("/api/v1/assessments/tprm-a", response_class=JSONResponse)
def create_tprm_assessment(payload: dict = Body(...)):
    assessment = generate_assessment(payload)
    ASSESSMENTS_STORE[assessment["id"]] = assessment
    return JSONResponse(content=assessment)


# ---------------- Assessment Response ----------------

@app.post("/api/v1/assessments/{assessment_id}/response", response_class=JSONResponse)
def create_assessment_response(
    assessment_id: str = Path(...),
    payload: dict = Body(...)
):
    """
    Create a response for a given assessment.
    """
    assessment = ASSESSMENTS_STORE.get(assessment_id)
    if not assessment:
        return JSONResponse(content={"error": "Assessment not found"}, status_code=404)

    now = now_utc()
    response_id = payload.get("id", assessment.get("responseId", fake.uuid4()))

    response_obj = {
        "id": response_id,
        "questionnaireId": assessment.get("questionnaireId"),
        "questionnaireCode": "TPRM_A_CODE",
        "questionnaireVersion": assessment.get("questionnaireVersion", "1.0"),
        "assessmentId": assessment_id,
        "assessmentType": assessment.get("type"),
        "vendorId": assessment.get("vendorId"),
        "engagementId": assessment.get("engagementId"),
        "respondentId": fake.uuid4(),
        "respondentName": fake.name(),
        "respondentRole": "Vendor Representative",
        "respondentEmail": fake.email(),
        "sectionResponses": [
            {
                "sectionId": fake.uuid4(),
                "sectionName": "Default Section",
                "answers": [
                    {
                        "questionId": fake.uuid4(),
                        "questionText": "Sample Question?",
                        "textValue": "Sample Answer",
                        "selectedOptions": ["Option1"],
                        "numericValue": 0,
                        "dateValue": now,
                        "booleanValue": True,
                        "fileIds": [fake.uuid4()],
                        "score": 0,
                        "maxScore": 5,
                        "rating": "LOW",
                        "remarks": "No remarks",
                        "evidenceDocumentIds": [fake.uuid4()],
                        "reviewerComment": "Reviewed",
                        "flagged": True,
                        "overarching": True
                    }
                ],
                "sectionScore": 0,
                "sectionMaxScore": 5
            }
        ],
        "scored": True,
        "scoreResult": {
            "totalScore": 0,
            "maxPossibleScore": 5,
            "percentage": 0,
            "rating": "LOW",
            "ratingColor": "GREEN",
            "riskRating": "LOW",
            "riskCategory": "LOW",
            "calculatedRating": "LOW",
            "overarchingOverride": True,
            "overarchingQuestionIds": [fake.uuid4()],
            "sectionScores": {
                "additionalProp1": 0,
                "additionalProp2": 0,
                "additionalProp3": 0
            },
            "sectionRatings": {
                "additionalProp1": "LOW",
                "additionalProp2": "LOW",
                "additionalProp3": "LOW"
            },
            "calculatedAt": now
        },
        "state": "DRAFT",
        "reviewerId": fake.uuid4(),
        "reviewerName": fake.name(),
        "reviewComments": "All good",
        "reviewedAt": now,
        "createdAt": now,
        "updatedAt": now,
        "submittedAt": now,
        "completedAt": None
    }

    ASSESSMENT_RESPONSES_STORE[response_id] = response_obj

    assessment["state"] = "RESPONSE_SUBMITTED"
    assessment["updatedAt"] = now

    return JSONResponse(content=response_obj)
