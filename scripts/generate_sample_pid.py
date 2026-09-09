import fitz
from pathlib import Path

def create_sample_pid():
    target_dir = Path("data/raw/pidqa")
    target_dir.mkdir(parents=True, exist_ok=True)
    img_path = target_dir / "pid_cdu_pump_p204.png"

    # Create a blank drawing page
    doc = fitz.open()
    page = doc.new_page(width=900, height=600)

    # Background
    page.draw_rect(fitz.Rect(0, 0, 900, 600), color=(0.95, 0.95, 0.95), fill=(0.98, 0.98, 0.98))

    # Border & Title Block
    page.draw_rect(fitz.Rect(20, 20, 880, 580), color=(0.1, 0.1, 0.2), width=2.0)
    title_rect = fitz.Rect(580, 500, 880, 580)
    page.draw_rect(title_rect, color=(0.1, 0.1, 0.2), fill=(0.92, 0.93, 0.95), width=1.5)
    page.insert_text((590, 525), "MRPL — PIPING & INSTRUMENTATION DIAGRAM", fontsize=10, fontname="helv", color=(0.1, 0.1, 0.3))
    page.insert_text((590, 545), "UNIT: CDU-II FRACTIONATION | DWG NO: PID-MRPL-P204-01", fontsize=8.5, fontname="helv")
    page.insert_text((590, 565), "SERVICE: HEAVY GAS OIL (HGO) PUMP P-204 A/B", fontsize=8.5, fontname="helv", color=(0.7, 0.2, 0.1))

    # Suction Tank TK-201
    tk_rect = fitz.Rect(60, 150, 180, 420)
    page.draw_rect(tk_rect, color=(0.2, 0.3, 0.5), fill=(0.88, 0.92, 0.96), width=2.0)
    page.insert_text((85, 280), "TK-201\nCDU BOTTOMS\nFEED VESSEL", fontsize=10, fontname="helv")

    # Suction Line
    page.draw_line(fitz.Point(180, 320), fitz.Point(360, 320), color=(0.1, 0.1, 0.1), width=3.0)
    page.insert_text((220, 310), '10"-HGO-301-CS', fontsize=9, fontname="helv")

    # Pump P-204A
    p1_center = fitz.Point(400, 260)
    page.draw_circle(p1_center, 40, color=(0.1, 0.4, 0.7), fill=(0.85, 0.92, 0.98), width=2.5)
    page.insert_text((380, 265), "P-204A", fontsize=10, fontname="helv")

    # Pump P-204B (Standby)
    p2_center = fitz.Point(400, 380)
    page.draw_circle(p2_center, 40, color=(0.1, 0.4, 0.7), fill=(0.85, 0.92, 0.98), width=2.5)
    page.insert_text((380, 385), "P-204B", fontsize=10, fontname="helv")

    # Discharge Line with elbow
    page.draw_line(fitz.Point(440, 260), fitz.Point(540, 260), color=(0.1, 0.1, 0.1), width=3.0)
    page.draw_line(fitz.Point(440, 380), fitz.Point(540, 380), color=(0.1, 0.1, 0.1), width=3.0)
    page.draw_line(fitz.Point(540, 260), fitz.Point(540, 380), color=(0.1, 0.1, 0.1), width=3.0)
    page.draw_line(fitz.Point(540, 320), fitz.Point(750, 320), color=(0.1, 0.1, 0.1), width=3.0)
    page.insert_text((560, 310), '8"-HGO-302-CS (CRITICAL ELBOW)', fontsize=9, fontname="helv", color=(0.8, 0.1, 0.1))

    # Control Valve CV-204
    cv_rect = fitz.Rect(650, 305, 680, 335)
    page.draw_rect(cv_rect, color=(0.7, 0.1, 0.1), fill=(1.0, 0.85, 0.85), width=1.5)
    page.insert_text((645, 295), "FCV-204", fontsize=9, fontname="helv", color=(0.8, 0.1, 0.1))

    # Instruments
    pi_center = fitz.Point(490, 210)
    page.draw_circle(pi_center, 18, color=(0.2, 0.2, 0.2), fill=(1, 1, 1), width=1.5)
    page.insert_text((478, 215), "PT-204", fontsize=8, fontname="helv")
    page.draw_line(fitz.Point(490, 228), fitz.Point(490, 260), color=(0.2, 0.2, 0.2), width=1.0)

    # Render to PNG
    pix = page.get_pixmap(dpi=150)
    pix.save(str(img_path))
    doc.close()
    print(f"Created sample P&ID diagram: {img_path}")

if __name__ == "__main__":
    create_sample_pid()
