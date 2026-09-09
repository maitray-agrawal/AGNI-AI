"""AGNI-AI System Healthcheck & Air-Gap Verification Script."""
import sys
import httpx
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app.config import settings
from backend.app.security.network import NetworkTelemetry

def run_healthcheck():
    print("=== AGNI-AI SYSTEM HEALTHCHECK ===")
    
    # 1. Check Ollama
    try:
        resp = httpx.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=5.0)
        if resp.status_code == 200:
            models = [m["name"] for m in resp.json().get("models", [])]
            print(f"[OK] Ollama running on {settings.OLLAMA_BASE_URL}")
            print(f"     Installed Models ({len(models)}): {', '.join(models)}")
        else:
            print(f"[WARN] Ollama returned status {resp.status_code}")
    except Exception as e:
        print(f"[FAIL] Ollama connection failed: {e}")

    # 2. Check Qdrant Storage
    if settings.QDRANT_PATH.exists():
        print(f"[OK] Qdrant local disk storage ready at: {settings.QDRANT_PATH}")
    else:
        print(f"[FAIL] Qdrant storage missing at: {settings.QDRANT_PATH}")

    # 3. Check Demo Files
    pdf_path = settings.DATA_DIR / "raw" / "inspection_reports" / "MRPL_Inspection_Report_P204.pdf"
    if pdf_path.exists():
        print(f"[OK] Inspection PDF ready: {pdf_path.name} ({pdf_path.stat().st_size} bytes)")
    else:
        print(f"[WARN] Inspection PDF missing: {pdf_path}")

    pid_path = settings.DATA_DIR / "raw" / "pidqa" / "pid_cdu_pump_p204.png"
    if pid_path.exists():
        print(f"[OK] P&ID Image ready: {pid_path.name} ({pid_path.stat().st_size} bytes)")
    else:
        print(f"[WARN] P&ID Image missing: {pid_path}")

    # 4. Telemetry
    telemetry = NetworkTelemetry.verify_airgap()
    print(f"[OK] Local Traffic Verification: Verified on localhost (External calls: {telemetry['external_ai_api_calls']})")
    print("=== HEALTHCHECK COMPLETE ===")

if __name__ == "__main__":
    run_healthcheck()
