"""
AGNI-AI: Agent Reliability Benchmark Suite
Executes 20 representative workflows across reasoning, coding, industrial document,
and edge-case/failure scenarios. Evaluates end-to-end reliability, planning validity,
routing correctness, verifier gating, and latency breakdowns.
"""
import asyncio
import json
import time
from pathlib import Path
from typing import List, Dict, Any
import sys

# Ensure root directory is on PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app.agent.graph import run_agent

SAMPLE_PDF = "data/raw/inspection_reports/MRPL_Inspection_Report_P204.pdf"

# 20 representative workflows across 4 categories
WORKFLOW_SUITE: List[Dict[str, Any]] = [
    # -------------------------------------------------------------
    # 1. REASONING WORKFLOWS (5 workflows)
    # -------------------------------------------------------------
    {
        "id": "WF-R01",
        "category": "Reasoning",
        "task": "Summarize standard maintenance procedures for Crude Distillation Unit pump overhaul.",
        "files": [],
        "expected_model": "llama3.1:8b",
        "expected_verdict": "passed",
    },
    {
        "id": "WF-R02",
        "category": "Reasoning",
        "task": "Explain API 570 piping inspection intervals and thickness measurement locations (TML).",
        "files": [],
        "expected_model": "llama3.1:8b",
        "expected_verdict": "passed",
    },
    {
        "id": "WF-R03",
        "category": "Reasoning",
        "task": "Formulate root-cause analysis hypotheses for recurring centrifugal pump cavitation in CDU-II.",
        "files": [],
        "expected_model": "llama3.1:8b",
        "expected_verdict": "passed",
    },
    {
        "id": "WF-R04",
        "category": "Reasoning",
        "task": "Review ISO 10816 vibration severity limits and explain alarm versus trip thresholds.",
        "files": [],
        "expected_model": "llama3.1:8b",
        "expected_verdict": "passed",
    },
    {
        "id": "WF-R05",
        "category": "Reasoning",
        "task": "Synthesize emergency response action steps for sour crude line flange leak.",
        "files": [],
        "expected_model": "llama3.1:8b",
        "expected_verdict": "passed",
    },

    # -------------------------------------------------------------
    # 2. CODING & CALCULATION WORKFLOWS (5 workflows)
    # -------------------------------------------------------------
    {
        "id": "WF-C01",
        "category": "Coding",
        "task": "Calculate the percentage reduction from 8.2 mm to 7.4 mm wall thickness.",
        "files": [],
        "expected_model": "qwen2.5-coder:7b",
        "expected_verdict": "passed",
    },
    {
        "id": "WF-C02",
        "category": "Coding",
        "task": "Calculate corrosion rate: Initial thickness 9.0 mm, final 7.5 mm, duration 2.5 years.",
        "files": [],
        "expected_model": "qwen2.5-coder:7b",
        "expected_verdict": "passed",
    },
    {
        "id": "WF-C03",
        "category": "Coding",
        "task": "Calculate remaining life: current thickness 4.8 mm, retirement 4.0 mm, corrosion rate 0.1 mm/yr.",
        "files": [],
        "expected_model": "qwen2.5-coder:7b",
        "expected_verdict": "passed",
    },
    {
        "id": "WF-C04",
        "category": "Coding",
        "task": "Compute percentage wall loss: original 12.0 mm, measured 8.4 mm.",
        "files": [],
        "expected_model": "qwen2.5-coder:7b",
        "expected_verdict": "passed",
    },
    {
        "id": "WF-C05",
        "category": "Coding",
        "task": "Write Python logic to calculate pump hydraulic power from flow rate 150 m3/h and head 45 m.",
        "files": [],
        "expected_model": "qwen2.5-coder:7b",
        "expected_verdict": "passed",
    },

    # -------------------------------------------------------------
    # 3. INDUSTRIAL DOCUMENT WORKFLOWS (5 workflows)
    # -------------------------------------------------------------
    {
        "id": "WF-D01",
        "category": "Document",
        "task": "Analyze this inspection report, identify critical findings, consult SOPs, verify and generate approval note.",
        "files": [SAMPLE_PDF],
        "expected_model": "llama3.1:8b",
        "expected_verdict": "passed",
    },
    {
        "id": "WF-D02",
        "category": "Document",
        "task": "Process scanned NDT inspection report for P-204, evaluate wall thickness, and draft clearance disposition.",
        "files": [SAMPLE_PDF],
        "expected_model": "llama3.1:8b",
        "expected_verdict": "passed",
    },
    {
        "id": "WF-D03",
        "category": "Document",
        "task": "Review P-204 ultrasonic thickness testing data against API 570 retirement limit and produce approval note.",
        "files": [SAMPLE_PDF],
        "expected_model": "llama3.1:8b",
        "expected_verdict": "passed",
    },
    {
        "id": "WF-D04",
        "category": "Document",
        "task": "Analyze inspection report findings for CDU pump vibration and wall thinning, generate official DOCX deliverable.",
        "files": [SAMPLE_PDF],
        "expected_model": "llama3.1:8b",
        "expected_verdict": "passed",
    },
    {
        "id": "WF-D05",
        "category": "Document",
        "task": "Inspect equipment P-204 report, check grounding in API 570 standards, and compile maintenance disposition.",
        "files": [SAMPLE_PDF],
        "expected_model": "llama3.1:8b",
        "expected_verdict": "passed",
    },

    # -------------------------------------------------------------
    # 4. EDGE-CASE & FAILURE HANDLING WORKFLOWS (5 workflows)
    # -------------------------------------------------------------
    {
        "id": "WF-E01",
        "category": "EdgeCase",
        "task": "Analyze missing equipment file with empty parameters.",
        "files": ["non_existent_file_999.pdf"],
        "expected_model": "llama3.1:8b",
        "expected_verdict": "passed",  # Handles non-existent file gracefully through fallback
    },
    {
        "id": "WF-E02",
        "category": "EdgeCase",
        "task": "Calculate",  # Minimalist incomplete calculation prompt
        "files": [],
        "expected_model": "qwen2.5-coder:7b",
        "expected_verdict": "passed",
    },
    {
        "id": "WF-E03",
        "category": "EdgeCase",
        "task": "Refinery turnaround summary.",  # Very brief query
        "files": [],
        "expected_model": "llama3.1:8b",
        "expected_verdict": "passed",
    },
    {
        "id": "WF-E04",
        "category": "EdgeCase",
        "task": "Inspect drawing and compute formula.",  # Ambiguous multi-domain task
        "files": [],
        "expected_model": "qwen2.5-coder:7b",
        "expected_verdict": "passed",
    },
    {
        "id": "WF-E05",
        "category": "EdgeCase",
        "task": "Evaluate API 570 criteria without equipment data.",
        "files": [],
        "expected_model": "llama3.1:8b",
        "expected_verdict": "passed",
    },
]


async def run_reliability_benchmark() -> Dict[str, Any]:
    print("=" * 75)
    print("  AGNI-AI: AGENT RELIABILITY BENCHMARK SUITE (20 WORKFLOWS)")
    print("=" * 75)

    results: List[Dict[str, Any]] = []
    category_summary: Dict[str, Dict[str, int]] = {}
    latencies: List[int] = []

    for item in WORKFLOW_SUITE:
        wf_id = item["id"]
        cat = item["category"]
        task = item["task"]
        files = item["files"]
        expected_model = item["expected_model"]

        print(f"\n[{wf_id}] Executing {cat} Workflow: '{task[:50]}...'")
        t0 = time.time()
        
        try:
            state = await run_agent(task=task, files=files)
            duration_ms = int((time.time() - t0) * 1000)
            latencies.append(duration_ms)

            # Extract metrics
            plan = state.get("plan", [])
            plan_valid = len(plan) >= 3
            selected_model = state.get("selected_model", "")
            actual_model = state.get("actual_model", selected_model)
            routing_correct = (expected_model in selected_model or expected_model.split(":")[0] in selected_model)
            
            verification = state.get("verification", {})
            verdict_status = verification.get("status", "failed")
            verifier_passed = (verdict_status == "passed")
            
            errors = state.get("errors", [])
            has_fatal_errors = len(errors) > 0
            
            fallbacks = state.get("fallbacks", [])
            fallback_used = len(fallbacks) > 0

            workflow_success = plan_valid and verifier_passed and not has_fatal_errors

            if cat not in category_summary:
                category_summary[cat] = {"total": 0, "successful": 0, "verifier_passed": 0}
            category_summary[cat]["total"] += 1
            if workflow_success:
                category_summary[cat]["successful"] += 1
            if verifier_passed:
                category_summary[cat]["verifier_passed"] += 1

            res_record = {
                "id": wf_id,
                "category": cat,
                "task": task,
                "selected_model": selected_model,
                "actual_model": actual_model,
                "routing_correct": routing_correct,
                "plan_steps_count": len(plan),
                "plan_valid": plan_valid,
                "verifier_status": verdict_status,
                "verifier_passed": verifier_passed,
                "fallback_used": fallback_used,
                "errors_count": len(errors),
                "workflow_success": workflow_success,
                "duration_ms": duration_ms,
                "latency_breakdown": state.get("latency_breakdown", {}),
            }
            results.append(res_record)

            mark = "[PASS]" if workflow_success else "[FAIL]"
            print(f"  {mark} Model: {actual_model} | Verifier: {verdict_status} | Duration: {duration_ms}ms")

        except Exception as e:
            duration_ms = int((time.time() - t0) * 1000)
            print(f"  [EXCEPTION]: {e}")
            if cat not in category_summary:
                category_summary[cat] = {"total": 0, "successful": 0, "verifier_passed": 0}
            category_summary[cat]["total"] += 1
            results.append({
                "id": wf_id,
                "category": cat,
                "task": task,
                "workflow_success": False,
                "error": str(e),
                "duration_ms": duration_ms,
            })

    import statistics

    # Metric computations
    total_workflows = len(results)
    successful_workflows = sum(1 for r in results if r.get("workflow_success"))
    failed_workflows = total_workflows - successful_workflows
    success_rate = (successful_workflows / total_workflows) * 100.0 if total_workflows else 0.0

    routing_correct_count = sum(1 for r in results if r.get("routing_correct"))
    routing_acc = (routing_correct_count / total_workflows) * 100.0 if total_workflows else 0.0

    verifier_passed_count = sum(1 for r in results if r.get("verifier_passed"))
    verifier_pass_rate = (verifier_passed_count / total_workflows) * 100.0 if total_workflows else 0.0

    fallback_count = sum(1 for r in results if r.get("fallback_used"))
    fallback_rate = (fallback_count / total_workflows) * 100.0 if total_workflows else 0.0

    # Failure category classification
    failure_categories: Dict[str, int] = {}
    for r in results:
        if not r.get("workflow_success"):
            if r.get("error"):
                cat = "UnhandledException"
            elif not r.get("plan_valid"):
                cat = "InvalidPlan"
            elif not r.get("verifier_passed"):
                cat = "VerifierGateRejection"
            else:
                cat = "ExecutionFailure"
            failure_categories[cat] = failure_categories.get(cat, 0) + 1

    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
    median_latency = statistics.median(latencies) if latencies else 0.0
    p95_latency = sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0.0

    print("\n" + "=" * 75)
    print("  AGNI-AI AGENT RELIABILITY BENCHMARK REPORT")
    print("=" * 75)
    print(f"Test Type: End-to-End Autonomous Agent Workflows")
    print(f"Real Local Inference via Ollama: True")
    print(f"Hardware Constraint: 16 GB RAM / Sequential Inference (No CUDA)")
    print("-" * 75)
    print(f"{'Category':<15} | {'Total':<8} | {'Successful':<12} | {'Success Rate':<12}")
    print("-" * 55)
    for cat, data in category_summary.items():
        cat_rate = (data["successful"] / data["total"]) * 100.0 if data["total"] else 0.0
        print(f"{cat:<15} | {data['total']:<8} | {data['successful']:<12} | {cat_rate:.1f}%")
    print("-" * 55)
    print(f"{'OVERALL':<15} | {total_workflows:<8} | {successful_workflows:<12} | {success_rate:.1f}%\n")

    print("[CORE SYSTEM RELIABILITY METRICS]:")
    print(f"  • Total Workflows Evaluated:  {total_workflows}")
    print(f"  • Successful Workflows:       {successful_workflows}")
    print(f"  • Failed / Edge-case Caught:  {failed_workflows}")
    print(f"  • Workflow Success Rate:      {success_rate:.1f}%")
    print(f"  • Model Routing Accuracy:     {routing_acc:.1f}% ({routing_correct_count}/{total_workflows})")
    print(f"  • 8-Point Verifier Pass Rate: {verifier_pass_rate:.1f}% ({verifier_passed_count}/{total_workflows})")
    print(f"  • Model Fallback Count / Rate: {fallback_count} ({fallback_rate:.1f}%)")
    print(f"  • Failure Categories:         {failure_categories}")
    print(f"\n[END-TO-END LATENCY BREAKDOWN]:")
    print(f"  • Min Latency:                {min(latencies) / 1000.0:.2f} s" if latencies else "N/A")
    print(f"  • Median Latency:             {median_latency / 1000.0:.2f} s")
    print(f"  • Average Latency:            {avg_latency / 1000.0:.2f} s")
    print(f"  • P95 Latency:                {p95_latency / 1000.0:.2f} s")
    print(f"  • Max Latency:                {max(latencies) / 1000.0:.2f} s" if latencies else "N/A")

    output_dir = ROOT_DIR / "outputs" / "benchmarks"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "agent_reliability_results.json"

    benchmark_payload = {
        "benchmark_name": "AGNI-AI Agent Reliability Benchmark",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "test_type": "REAL_LOCAL_INFERENCE_WORKFLOW",
        "real_local_inference_used": True,
        "success_definition": "Workflow generates valid multi-step plan, passes 8-point domain verification gate, and encounters zero unhandled exceptions.",
        "limitations": "Evaluated sequentially on single-machine host with 16 GB RAM and shared Intel Arc Graphics. Model loading and context switching account for significant portions of measured end-to-end duration.",
        "total_workflows": total_workflows,
        "successful_workflows": successful_workflows,
        "failed_workflows": failed_workflows,
        "workflow_success_rate_pct": round(success_rate, 2),
        "routing_correct_count": routing_correct_count,
        "routing_accuracy_pct": round(routing_acc, 2),
        "verifier_passed_count": verifier_passed_count,
        "verifier_pass_rate_pct": round(verifier_pass_rate, 2),
        "fallback_count": fallback_count,
        "fallback_rate_pct": round(fallback_rate, 2),
        "failure_categories": failure_categories,
        "latencies_ms": {
            "min": min(latencies) if latencies else 0,
            "median": round(median_latency, 2),
            "average": round(avg_latency, 2),
            "p95": round(p95_latency, 2),
            "max": max(latencies) if latencies else 0,
        },
        "category_summary": category_summary,
        "detailed_results": results,
    }

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(benchmark_payload, f, indent=2)

    print(f"\n[Artifact Saved]: {out_file} ({out_file.stat().st_size} bytes)")
    print("=" * 75)
    return benchmark_payload


if __name__ == "__main__":
    asyncio.run(run_reliability_benchmark())
