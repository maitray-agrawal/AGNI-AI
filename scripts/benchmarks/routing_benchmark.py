"""
AGNI-AI: Model Routing Benchmark Suite
Evaluates capability-aware routing correctness, explainability, and latency
across 60 representative industrial prompts without running full model inference.
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

from backend.app.models.router import model_router, CapabilityRouter
from backend.app.models.registry import model_registry

# Define 60 representative tasks across 5 categories
BENCHMARK_TASKS: List[Dict[str, Any]] = [
    # -------------------------------------------------------------
    # 1. REASONING (20 tasks) -> Expected capability: "reasoning" (llama3.1:8b)
    # -------------------------------------------------------------
    {"id": "R01", "task": "Analyze scanned inspection report for Crude Distillation Unit pump P-204.", "files": ["report.pdf"], "expected_role": "reasoning"},
    {"id": "R02", "task": "Synthesize refinery SOP compliance for high-pressure hydrocracker valve leakage.", "files": ["sop.pdf"], "expected_role": "reasoning"},
    {"id": "R03", "task": "Formulate root-cause analysis for recurring heat exchanger tube fouling.", "files": [], "expected_role": "reasoning"},
    {"id": "R04", "task": "Review API 570 inspection criteria for piping circuit thickness retirement.", "files": [], "expected_role": "reasoning"},
    {"id": "R05", "task": "Generate engineering approval disposition note for emergency boiler shutdown.", "files": ["report.pdf"], "expected_role": "reasoning"},
    {"id": "R06", "task": "Evaluate corrosion monitoring logs across crude preheat train.", "files": ["logs.pdf"], "expected_role": "reasoning"},
    {"id": "R07", "task": "Synthesize recommendations for atmospheric column overhead condenser overhaul.", "files": [], "expected_role": "reasoning"},
    {"id": "R08", "task": "Draft maintenance procedure for sour water stripper reboiler inspection.", "files": [], "expected_role": "reasoning"},
    {"id": "R09", "task": "Assess risk matrix for catalytic cracking unit regenerator refractory degradation.", "files": ["inspection.pdf"], "expected_role": "reasoning"},
    {"id": "R10", "task": "Analyze ultrasonic thickness testing report for vacuum gas oil piping.", "files": ["ut_report.pdf"], "expected_role": "reasoning"},
    {"id": "R11", "task": "Formulate engineering disposition for flare knock-out drum wall thinning.", "files": ["drum_inspection.pdf"], "expected_role": "reasoning"},
    {"id": "R12", "task": "Review ISO 10816 vibration severity guidelines for multi-stage centrifugal pump.", "files": [], "expected_role": "reasoning"},
    {"id": "R13", "task": "Evaluate pump vibration anomaly report and determine bearing replacement schedule.", "files": ["vibration.pdf"], "expected_role": "reasoning"},
    {"id": "R14", "task": "Summarize NDT magnetic particle inspection findings for storage tank weld seams.", "files": ["tank_ndt.pdf"], "expected_role": "reasoning"},
    {"id": "R15", "task": "Synthesize emergency response protocol for hydrogen sulfide gas leak in DHDS unit.", "files": [], "expected_role": "reasoning"},
    {"id": "R16", "task": "Conduct failure mode and effects analysis (FMEA) on refinery cooling water pumps.", "files": [], "expected_role": "reasoning"},
    {"id": "R17", "task": "Review safety clearance protocol for confined space entry in column C-101.", "files": [], "expected_role": "reasoning"},
    {"id": "R18", "task": "Interpret acoustic emission testing data on liquefied petroleum gas sphere.", "files": ["ae_data.pdf"], "expected_role": "reasoning"},
    {"id": "R19", "task": "Formulate maintenance plan for delayed coker hydraulic decoking valve.", "files": [], "expected_role": "reasoning"},
    {"id": "R20", "task": "Assess residual life expectancy of furnace radiant coils under creep conditions.", "files": ["furnace_eval.pdf"], "expected_role": "reasoning"},

    # -------------------------------------------------------------
    # 2. CODING & DETERMINISTIC CALCULATION (15 tasks) -> Expected: "coding" (qwen2.5-coder:7b)
    # -------------------------------------------------------------
    {"id": "C01", "task": "Calculate the percentage reduction from 8.2 mm to 7.4 mm wall thickness.", "files": [], "expected_role": "coding"},
    {"id": "C02", "task": "Write a Python script to parse sensor CSV logs and detect temperature spikes.", "files": [], "expected_role": "coding"},
    {"id": "C03", "task": "Calculate the corrosion rate in mm/year given initial 10.0 mm and current 8.5 mm over 3 years.", "files": [], "expected_role": "coding"},
    {"id": "C04", "task": "Compute Reynolds number for crude oil flow at 150 deg C through 8-inch schedule 40 pipe.", "files": [], "expected_role": "coding"},
    {"id": "C05", "task": "Generate Python code to plot vibration RMS trends against ISO 10816 alarm thresholds.", "files": [], "expected_role": "coding"},
    {"id": "C06", "task": "Calculate API 570 minimum required wall thickness using Barlow's formula.", "files": [], "expected_role": "coding"},
    {"id": "C07", "task": "Write an algorithm to compute moving average of distillation column tray differential pressure.", "files": [], "expected_role": "coding"},
    {"id": "C08", "task": "Calculate the pressure drop across an orifice plate using ISO 5167 formula.", "files": [], "expected_role": "coding"},
    {"id": "C09", "task": "Develop a Python function to compute pump hydraulic efficiency from head and flow rate.", "files": [], "expected_role": "coding"},
    {"id": "C10", "task": "Calculate heat exchanger log mean temperature difference (LMTD) for counter-current flow.", "files": [], "expected_role": "coding"},
    {"id": "C11", "task": "Write Python script to perform Monte Carlo simulation for equipment failure probabilities.", "files": [], "expected_role": "coding"},
    {"id": "C12", "task": "Compute centrifugal compressor polytropic head and gas power consumption.", "files": [], "expected_role": "coding"},
    {"id": "C13", "task": "Calculate remaining service life given t_actual=4.2mm, t_min=4.0mm, and corrosion_rate=0.08mm/yr.", "files": [], "expected_role": "coding"},
    {"id": "C14", "task": "Generate NumPy script to filter high-frequency noise from piezoelectric accelerometer telemetry.", "files": [], "expected_role": "coding"},
    {"id": "C15", "task": "Calculate thermal expansion stress on 12-inch carbon steel steam piping.", "files": [], "expected_role": "coding"},

    # -------------------------------------------------------------
    # 3. GENERAL TECHNICAL REASONING (10 tasks) -> Expected: "reasoning" or "general" (llama3.1:8b / mistral)
    # -------------------------------------------------------------
    {"id": "G01", "task": "What is the difference between an API 610 and API 676 pump?", "files": [], "expected_role": "reasoning"},
    {"id": "G02", "task": "Explain the operational purpose of a vacuum distillation unit in petroleum refining.", "files": [], "expected_role": "reasoning"},
    {"id": "G03", "task": "Summarize common non-destructive testing methods used in refinery turnaround.", "files": [], "expected_role": "reasoning"},
    {"id": "G04", "task": "Define cavitation in centrifugal pumps and list key prevention techniques.", "files": [], "expected_role": "reasoning"},
    {"id": "G05", "task": "Explain the chemical reaction mechanism of amine gas treating for H2S removal.", "files": [], "expected_role": "reasoning"},
    {"id": "G06", "task": "What does NACE MR0175 standard specify regarding sulfide stress cracking?", "files": [], "expected_role": "reasoning"},
    {"id": "G07", "task": "Outline standard shift handover protocol for refinery control room operators.", "files": [], "expected_role": "reasoning"},
    {"id": "G08", "task": "Explain the significance of flash point versus fire point in hydrocarbon classification.", "files": [], "expected_role": "reasoning"},
    {"id": "G09", "task": "Compare wet gas compressor trip mechanisms in fluid catalytic cracking units.", "files": [], "expected_role": "reasoning"},
    {"id": "G10", "task": "Describe the principles of cathodic protection on buried refinery pipelines.", "files": [], "expected_role": "reasoning"},

    # -------------------------------------------------------------
    # 4. VISION & MULTIMODAL ROUTING (10 tasks) -> Expected: "vision" (moondream)
    # -------------------------------------------------------------
    {"id": "V01", "task": "Inspect this P&ID drawing and identify pump P-204 discharge valve connections.", "files": ["pid_diagram.png"], "expected_role": "vision"},
    {"id": "V02", "task": "Analyze scanned isometric drawing for line 10-CDU-204-A1A.", "files": ["isometric.jpg"], "expected_role": "vision"},
    {"id": "V03", "task": "Identify control valve instrumentation symbols on this P&ID schematic.", "files": ["schematic.png"], "expected_role": "vision"},
    {"id": "V04", "task": "Inspect visual defect photo of cracked weld on crude pipeline elbow.", "files": ["crack_photo.jpg"], "expected_role": "vision"},
    {"id": "V05", "task": "Trace hydrocarbon feed line from furnace inlet through crude tower on drawing.", "files": ["cdu_pid.tiff"], "expected_role": "vision"},
    {"id": "V06", "task": "Extract equipment tag numbers and valve types from this scanned diagram.", "files": ["diagram.png"], "expected_role": "vision"},
    {"id": "V07", "task": "Examine thermal imaging thermogram of electrical switchgear for hotspots.", "files": ["thermogram.png"], "expected_role": "vision"},
    {"id": "V08", "task": "Analyze scanned P&ID piping layout for bypass line and isolation valves.", "files": ["bypass_pid.bmp"], "expected_role": "vision"},
    {"id": "V09", "task": "Inspect corrosion pit depth in high-resolution macro photograph.", "files": ["macro_pit.jpg"], "expected_role": "vision"},
    {"id": "V10", "task": "Identify pressure safety valve (PSV) tag and set pressure on schematic image.", "files": ["psv_drawing.png"], "expected_role": "vision"},

    # -------------------------------------------------------------
    # 5. AMBIGUOUS / MIXED (5 tasks) -> Expected: valid routing based on primary objective
    # -------------------------------------------------------------
    {"id": "A01", "task": "Calculate wall thickness reduction and draft an inspection report disposition.", "files": ["report.pdf"], "expected_role": "reasoning"},  # Report with pdf -> inspection workflow (reasoning orchestrator)
    {"id": "A02", "task": "Inspect P&ID diagram and compute total pipe equivalent length in Python.", "files": ["pid.png"], "expected_role": "vision"},  # Has diagram image
    {"id": "A03", "task": "Write Python code to calculate boiler efficiency and summarize recommendations.", "files": [], "expected_role": "coding"},  # Primary compute
    {"id": "A04", "task": "Verify pump vibration reading against standard limits.", "files": [], "expected_role": "reasoning"},
    {"id": "A05", "task": "Estimate crude oil viscosity using thermal formula.", "files": [], "expected_role": "coding"},
]


async def run_routing_benchmark() -> Dict[str, Any]:
    print("=" * 75)
    print("  AGNI-AI: CAPABILITY-AWARE MODEL ROUTING BENCHMARK (60 TASKS)")
    print("=" * 75)

    router = CapabilityRouter(registry=model_registry)
    await model_registry.refresh_available_models()

    results: List[Dict[str, Any]] = []
    category_counts: Dict[str, Dict[str, int]] = {}
    latencies: List[int] = []

    for item in BENCHMARK_TASKS:
        t_id = item["id"]
        task = item["task"]
        files = item["files"]
        expected_role = item["expected_role"]
        cat = "Reasoning" if t_id.startswith("R") else "Coding" if t_id.startswith("C") else "General" if t_id.startswith("G") else "Vision" if t_id.startswith("V") else "Ambiguous"

        decision = await router.route_task(task, files)
        latencies.append(decision.decision_latency_ms)

        # Check correctness: mapped role corresponds to expected capability
        assigned_profile = decision.task_profile or {}
        assigned_cap = assigned_profile.get("capability", "reasoning")

        correct = (assigned_cap == expected_role)
        # For ambiguous/general, reasoning or general is valid
        if expected_role in ["reasoning", "general"] and assigned_cap in ["reasoning", "general"]:
            correct = True

        if cat not in category_counts:
            category_counts[cat] = {"total": 0, "correct": 0}
        category_counts[cat]["total"] += 1
        if correct:
            category_counts[cat]["correct"] += 1

        results.append({
            "id": t_id,
            "category": cat,
            "task": task[:65] + "..." if len(task) > 65 else task,
            "expected_role": expected_role,
            "assigned_role": assigned_cap,
            "selected_model": decision.selected_model,
            "task_type": decision.task_type,
            "correct": correct,
            "decision_latency_ms": decision.decision_latency_ms,
            "fallback_used": decision.fallback_used,
            "reason": decision.reason,
        })

    # Summary calculations
    total_tasks = len(results)
    correct_routes = sum(1 for r in results if r["correct"])
    accuracy = (correct_routes / total_tasks) * 100.0
    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
    p95_latency = sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0.0

    print(f"\n[BENCHMARK RESULTS BREAKDOWN]:")
    print(f"{'Category':<15} | {'Total':<8} | {'Correct':<8} | {'Accuracy':<10}")
    print("-" * 50)
    for cat, data in category_counts.items():
        cat_acc = (data["correct"] / data["total"]) * 100.0
        print(f"{cat:<15} | {data['total']:<8} | {data['correct']:<8} | {cat_acc:.1f}%")
    print("-" * 50)
    print(f"{'OVERALL':<15} | {total_tasks:<8} | {correct_routes:<8} | {accuracy:.1f}%\n")

    print(f"[LATENCY METRICS]:")
    print(f"  • Average Routing Latency: {avg_latency:.2f} ms")
    print(f"  • P95 Routing Latency:     {p95_latency:.2f} ms")
    print(f"  • Min / Max Latency:       {min(latencies)} ms / {max(latencies)} ms")

    # Output artifact file
    output_dir = ROOT_DIR / "outputs" / "benchmarks"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "routing_benchmark_results.json"
    
    benchmark_payload = {
        "benchmark_name": "AGNI-AI Capability-Aware Model Routing Benchmark",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "test_type": "ROUTING_CORRECTNESS_ONLY",
        "real_local_inference_used": False,
        "success_definition": "Evaluates deterministic capability scoring and task profiling correctness against expected model assignment without running local model generation.",
        "limitations": "Evaluates routing logic in isolation; does not evaluate model text completion quality.",
        "total_tasks": total_tasks,
        "correct_routes": correct_routes,
        "routing_accuracy_pct": round(accuracy, 2),
        "latency_ms": {
            "average": round(avg_latency, 2),
            "p95": round(p95_latency, 2),
            "min": min(latencies),
            "max": max(latencies),
        },
        "category_summary": category_counts,
        "detailed_results": results,
    }

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(benchmark_payload, f, indent=2)

    print(f"\n[Artifact Generated]: {out_file} ({out_file.stat().st_size} bytes)")
    print("=" * 75)

    return benchmark_payload


if __name__ == "__main__":
    asyncio.run(run_routing_benchmark())
