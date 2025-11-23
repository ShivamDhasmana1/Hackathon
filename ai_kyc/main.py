import uuid
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ocr import analyze_image_file
from face_match import verify_faces
from security import hash_kyc_fields

logger = logging.getLogger("kyc_service")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="AI KYC Service")

# ---------- CORS (so Lovable frontend can call this) ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can later restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Health / Root endpoints for verification ----------
@app.get("/")
async def root():
    return {"status": "ok", "message": "AI KYC backend is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# ---------- Your existing analyze_kyc route ----------
def make_decision(ocr_result: dict, face_result: dict) -> dict:
    ocr_conf = float(ocr_result.get("ocr_confidence_avg") or 0.0)
    face_verified = bool(face_result.get("face_verified"))
    face_score = float(face_result.get("face_score") or 0.0)
    liveness_passed = bool(face_result.get("liveness_passed", False))

    reasons = []
    risk_level = "low"
    status = "approved"

    if ocr_conf < 60:
        status = "manual_review"
        risk_level = "medium"
        reasons.append("Low OCR confidence")

    if not face_verified or face_score < 0.6:
        status = "manual_review"
        risk_level = "medium"
        reasons.append("Weak face verification")

    if not liveness_passed:
        status = "manual_review"
        risk_level = "high"
        reasons.append("Liveness check not passed")

    if not reasons and status == "approved":
        reasons = ["All basic checks passed"]

    summary = {
        "approved": "KYC auto-approved (low risk)",
        "manual_review": "KYC requires manual review",
        "rejected": "KYC rejected",
    }[status]

    return {
        "status": status,
        "auto_approve": status == "approved",
        "risk_level": risk_level,
        "summary": summary,
        "reasons": reasons,
        "internal_scores": {
            "ocr_conf": ocr_conf,
            "face_verified": face_verified,
            "face_score": face_score,
            "liveness_passed": liveness_passed,
        },
    }


@app.post("/analyze_kyc")
async def analyze_kyc(id_document: UploadFile = File(...),
                      selfie: UploadFile = File(...)):

    request_id = str(uuid.uuid4())
    logger.info(f"[{request_id}] /analyze_kyc started | id={id_document.filename}, selfie={selfie.filename}")

    try:
        id_bytes = await id_document.read()
        selfie_bytes = await selfie.read()

        if not id_bytes:
            raise HTTPException(status_code=400, detail="Empty ID document file")
        if not selfie_bytes:
            raise HTTPException(status_code=400, detail="Empty selfie file")

        try:
            ocr_result = analyze_image_file(id_bytes)
        except Exception:
            logger.exception(f"[{request_id}] OCR failed")
            raise HTTPException(status_code=500, detail="Failed to read document")

        try:
            face_result = verify_faces(id_bytes, selfie_bytes)
        except Exception:
            logger.exception(f"[{request_id}] Face verification failed")
            face_result = {
                "face_verified": False,
                "face_score": 0.0,
                "liveness_passed": False
            }

        fields = (ocr_result.get("fields") or {})
        name = fields.get("name")
        dob = fields.get("dob")
        id_number = fields.get("id_number")
        address = fields.get("address_snippet")

        try:
            hashed = hash_kyc_fields(
                name=name,
                dob=dob,
                id_number=id_number,
                address=address,
            )
            logger.info(f"[{request_id}] Hashing completed")
            # here you also append to your internal JSON log if you want
        except Exception:
            logger.exception(f"[{request_id}] Hashing failed")
            hashed = None

        decision = make_decision(ocr_result, face_result)

        logger.info(
            f"[{request_id}] decision={decision['status']} | "
            f"risk={decision['risk_level']} | "
            f"ocr_conf={decision['internal_scores']['ocr_conf']:.2f} | "
            f"face_score={decision['internal_scores']['face_score']:.3f} | "
            f"liveness={decision['internal_scores']['liveness_passed']}"
        )

        return JSONResponse(
            content={
                "request_id": request_id,
                "decision": {
                    "status": decision["status"],
                    "auto_approve": decision["auto_approve"],
                    "risk_level": decision["risk_level"],
                    "summary": decision["summary"],
                    "reasons": decision["reasons"],
                },
            }
        )

    except HTTPException as http_exc:
        logger.warning(f"[{request_id}] HTTP error: {http_exc.detail}")
        raise http_exc

    except Exception:
        logger.exception(f"[{request_id}] Unexpected error in /analyze_kyc")
        raise HTTPException(status_code=500, detail="Internal error while analyzing KYC")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)