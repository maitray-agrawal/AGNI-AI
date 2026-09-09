import fitz  # PyMuPDF
from pathlib import Path

def create_sample_inspection_pdf():
    target_dir = Path("data/raw/inspection_reports")
    target_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = target_dir / "MRPL_Inspection_Report_P204.pdf"

    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # A4

    # Draw header box
    header_rect = fitz.Rect(40, 40, 555, 110)
    page.draw_rect(header_rect, color=(0.1, 0.2, 0.4), fill=(0.95, 0.96, 0.98), width=1.5)
    
    page.insert_text((55, 65), "MANGALORE REFINERY AND PETROCHEMICALS LIMITED (MRPL)", fontsize=13, fontname="helv", color=(0.06, 0.17, 0.34))
    page.insert_text((55, 82), "REFINERY BLOCK 3 — CRUDE DISTILLATION UNIT II (CDU-II)", fontsize=10, fontname="helv", color=(0.4, 0.4, 0.4))
    page.insert_text((55, 100), "NON-DESTRUCTIVE TESTING (NDT) & ROTATING EQUIPMENT INSPECTION REPORT", fontsize=10, fontname="helv", color=(0.76, 0.25, 0.05))

    # Metadata Block
    page.insert_text((40, 135), "1. GENERAL ASSET & INSPECTION METADATA", fontsize=11, fontname="helv", color=(0.06, 0.17, 0.34))
    
    meta_box = fitz.Rect(40, 145, 555, 230)
    page.draw_rect(meta_box, color=(0.7, 0.7, 0.7), width=0.8)
    
    meta_lines = [
        "Equipment Identifier: P-204 A/B (Heavy Gas Oil Transfer Pump)",
        "Service Fluid: Heavy Gas Oil (HGO) @ 360°C Operating Temp, 24 kg/cm²g",
        "Plant Unit: CDU-II Primary Fractionation Section",
        "Inspection Date: 2026-08-14",
        "Inspector Lead: Rajesh K. Sharma (Level-II NDT Inspector)",
        "Inspection Method: Ultrasonic Thickness Gauging (UTG) & Vibration Spectrum Analysis",
    ]
    y = 162
    for line in meta_lines:
        page.insert_text((50, y), line, fontsize=9.5, fontname="helv", color=(0.1, 0.1, 0.1))
        y += 14

    # Quantitative Findings
    page.insert_text((40, 255), "2. NON-DESTRUCTIVE TESTING (NDT) MEASUREMENTS & FINDINGS", fontsize=11, fontname="helv", color=(0.06, 0.17, 0.34))

    table_box = fitz.Rect(40, 265, 555, 410)
    page.draw_rect(table_box, color=(0.7, 0.7, 0.7), width=0.8)
    
    # Table header
    hdr_box = fitz.Rect(40, 265, 555, 285)
    page.draw_rect(hdr_box, color=(0.1, 0.2, 0.4), fill=(0.1, 0.2, 0.4))
    page.insert_text((45, 279), "Parameter", fontsize=9, fontname="helv", color=(1, 1, 1))
    page.insert_text((180, 279), "Measured Value", fontsize=9, fontname="helv", color=(1, 1, 1))
    page.insert_text((300, 279), "Design / Limit", fontsize=9, fontname="helv", color=(1, 1, 1))
    page.insert_text((440, 279), "Assessment", fontsize=9, fontname="helv", color=(1, 1, 1))

    findings_rows = [
        ("Nominal Wall Thickness", "8.2 mm", "8.2 mm (Sched 80 CS)", "Baseline"),
        ("Minimum Wall Thickness (Discharge Bend)", "4.2 mm", "4.0 mm Retirement (API 570)", "CRITICAL (Near Retirement)"),
        ("Corrosion Rate (High Temp Sulfidic)", "0.8 mm/year", "0.15 mm/year Design Limit", "HIGH / ACCELERATED"),
        ("Overall Vibration (Pump DE Horizontal)", "7.8 mm/s RMS", "4.5 Alarm / 7.1 Trip (ISO)", "CRITICAL (Zone D Exceeded)"),
        ("Pump Bearing Temperature", "88.4 °C", "85.0 °C Maximum Continuous", "WARNING (Elevated)"),
    ]
    ty = 302
    for p, m, d, s in findings_rows:
        page.insert_text((45, ty), p, fontsize=8.5, fontname="helv", color=(0.1, 0.1, 0.1))
        page.insert_text((180, ty), m, fontsize=8.5, fontname="helv", color=(0.76, 0.1, 0.1) if "CRITICAL" in s else (0.1, 0.1, 0.1))
        page.insert_text((300, ty), d, fontsize=8.5, fontname="helv", color=(0.2, 0.2, 0.2))
        page.insert_text((440, ty), s, fontsize=8.5, fontname="helv", color=(0.76, 0.1, 0.1) if "CRITICAL" in s else (0.1, 0.1, 0.1))
        ty += 24

    # Technical Observations
    page.insert_text((40, 435), "3. INSPECTION OBSERVATIONS & DEFECT LOG", fontsize=11, fontname="helv", color=(0.06, 0.17, 0.34))
    obs_box = fitz.Rect(40, 445, 555, 545)
    page.draw_rect(obs_box, color=(0.7, 0.7, 0.7), width=0.8)

    obs = [
        "• Severe localized wall thinning detected at the 90-degree discharge elbow bend downstream of P-204.",
        "• Thickness measured at 4.2 mm, indicating only 0.2 mm remaining margin above API 570 retirement (4.0 mm).",
        "• Vibration spectrum indicates significant 1x RPM shaft unbalance and 2x blade pass frequency spikes.",
        "• Inboard bearing audible distress noted during run; cavitation surging observed at suction strainer.",
        "• Risk of catastrophic pressurized hydrocarbon leak if run continues without immediate containment.",
    ]
    oy = 465
    for o in obs:
        page.insert_text((50, oy), o, fontsize=8.5, fontname="helv", color=(0.15, 0.15, 0.15))
        oy += 16

    # Inspector Sign-off
    page.insert_text((40, 575), "4. OFFICIAL INSPECTOR ENDORSEMENT", fontsize=11, fontname="helv", color=(0.06, 0.17, 0.34))
    sign_box = fitz.Rect(40, 585, 555, 660)
    page.draw_rect(sign_box, color=(0.7, 0.7, 0.7), width=0.8)
    page.insert_text((50, 608), "Recorded By: Rajesh K. Sharma, Level-II NDT Inspector (NDT-CERT-MRPL-4092)", fontsize=9, fontname="helv")
    page.insert_text((50, 626), "Disposition: CONDITIONAL — Immediate Spool Wrap or Replacement Mandated before return to run.", fontsize=9, fontname="helv", color=(0.76, 0.1, 0.1))
    page.insert_text((50, 644), "Document Reference: MRPL/CDU2/INSP/2026/08/P204", fontsize=8.5, fontname="helv", color=(0.4, 0.4, 0.4))

    doc.save(str(pdf_path))
    doc.close()
    print(f"Created sample PDF: {pdf_path}")

if __name__ == "__main__":
    create_sample_inspection_pdf()
