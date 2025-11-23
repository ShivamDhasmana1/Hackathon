import uuid
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from ocr import analyze_image_file
from face_match import verify_faces
from security import hash_kyc_fields
from audit import append_hash_log, append_decision_log  # <-- NEW

# ---------- Logging setup ----------
logger = logging.getLogger("kyc_service")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="AI KYC Service")


# ---------- Decision logic ----------
def make_decision(ocr_result: dict, face_result: dict) -> dict:
    ocr_conf = float(ocr_result.get("ocr_confidence_avg") or 0.0)

    face_verified = bool(face_result.get("face_verified"))
    face_score = float(face_result.get("face_score") or 0.0)
    liveness_passed = bool(face_result.get("liveness_passed", False))

    reasons = []
    status = "approved"
    risk = "low"

    # Thresholds (tune later)
    if ocr_conf < 60:
        status = "manual_review"
        risk = "medium"
        reasons.append("Low OCR confidence")

    if not face_verified or face_score < 0.6:
        status = "manual_review"
        risk = "medium"
        reasons.append("Weak face verification")

    if not liveness_passed:
        status = "manual_review"
        risk = "medium"
        reasons.append("Liveness check not passed")

    if face_score < 0.3:
        status = "rejected"
        risk = "high"
        reasons.append("Very low face similarity")

    if not reasons and status == "approved":
        reasons = ["All basic checks passed"]

    # Short summary for UI
    if status == "approved":
        summary = "KYC auto-approved (low risk)"
    elif status == "manual_review":
        summary = "KYC requires manual review"
    else:
        summary = "KYC rejected due to high risk"

    return {
        "status": status,
        "auto_approve": status == "approved",
        "risk_level": risk,
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
async def analyze_kyc(
    id_document: UploadFile = File(...),
    selfie: UploadFile = File(...),
):
    request_id = str(uuid.uuid4())
    logger.info(
        f"[{request_id}] /analyze_kyc started | "
        f"id={id_document.filename} selfie={selfie.filename}"
    )

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

        fields = ocr_result.get("fields", {}) or {}
        name = fields.get("name")
        dob = fields.get("dob")
        id_number = fields.get("id_number")
        address = fields.get("address_snippet")

        try:
            face_result = verify_faces(id_bytes, selfie_bytes)
        except Exception:
            logger.exception(f"[{request_id}] Face verification failed")
            # Fail safe: treat as not verified, no liveness
            face_result = {
                "face_verified": False,
                "face_score": 0.0,
                "liveness_passed": False,
            }

        try:
            hashed = hash_kyc_fields(
                name=name,
                dob=dob,
                id_number=id_number,
                address=address,
            )
            logger.info(f"[{request_id}] Hashing completed")

            append_hash_log(
                request_id=request_id,
                hashed_fields=hashed,
                raw_meta={
                    "has_name": name is not None,
                    "has_dob": dob is not None,
                    "has_id_number": id_number is not None,
                    "has_address": address is not None,
                },
            )

        except Exception:
            logger.exception(f"[{request_id}] Hashing failed")
            hashed = None  

        decision = make_decision(ocr_result, face_result)
        append_decision_log(
            request_id=request_id,
            decision=decision,
            fields=fields,
        )

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
                    "status": decision["status"],          # "approved" | "manual_review" | "rejected"
                    "auto_approve": decision["auto_approve"],
                    "risk_level": decision["risk_level"],  # "low" | "medium" | "high"
                    "summary": decision["summary"],        # One-line message
                    "reasons": decision["reasons"],        # List of reasons
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

    uvicorn.run(app, host="0.0.0.0", port=8000)