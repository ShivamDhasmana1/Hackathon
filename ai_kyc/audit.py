import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HASH_LOG_PATH = os.path.join(BASE_DIR, "hash_log.jsonl")
DECISION_LOG_PATH = os.path.join(BASE_DIR, "decision_log.jsonl")


def _append_json_line(path: str, payload: Dict[str, Any]) -> None:
    """Append one JSON object as a single line in a .jsonl file."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def append_hash_log(
    request_id: str,
    hashed_fields: Optional[Dict[str, Any]],
    raw_meta: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Save hashed KYC fields (no raw PII) to local file for future DB import.
    """
    if not hashed_fields:
        return

    payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "request_id": request_id,
        "hashed_fields": hashed_fields,   # name/dob/id_number/address hashes
        "meta": raw_meta or {},          # e.g. which fields were present / null
    }
    _append_json_line(HASH_LOG_PATH, payload)


def append_decision_log(
    request_id: str,
    decision: Dict[str, Any],
    fields: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Save decision details (no raw hashes) for internal review.
    `fields` should NOT include raw full PII if you want to stay strict.
    """
    safe_fields = fields or {}
    # OPTIONAL: strip raw_text or long address if you don’t want any PII here.
    safe_fields = {
        k: v for k, v in safe_fields.items()
        if k not in ("raw_text",)  # you can add more keys to hide
    }

    payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "request_id": request_id,
        "decision": {
            "status": decision.get("status"),
            "auto_approve": decision.get("auto_approve"),
            "risk_level": decision.get("risk_level"),
            "summary": decision.get("summary"),
            "reasons": decision.get("reasons"),
            "internal_scores": decision.get("internal_scores"),
        },
        "fields": safe_fields,  # minimally useful metadata (no hashes)
    }
    _append_json_line(DECISION_LOG_PATH, payload)
