import base64
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
import fitz  # PyMuPDF

logger = logging.getLogger("agni.tools.document")


class DocumentParser:
    """Extracts text, metadata, and renders high-res page images for multimodal analysis."""

    @staticmethod
    def parse_pdf(file_path: str, render_dpi: int = 150) -> Dict[str, Any]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Document file not found: {file_path}")

        doc = fitz.open(str(path))
        pages_data: List[Dict[str, Any]] = []
        total_text_length = 0

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()
            total_text_length += len(text)

            # Render page to image (PNG) for multimodal vision analysis
            pix = page.get_pixmap(dpi=render_dpi)
            img_bytes = pix.tobytes("png")
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")

            pages_data.append({
                "page": page_num + 1,
                "text": text,
                "char_count": len(text),
                "image_base64": img_b64,
                "width": pix.width,
                "height": pix.height,
            })

        is_scanned = total_text_length < 50 * len(doc)  # Very little extractable digital text

        result = {
            "filename": path.name,
            "filepath": str(path).replace("\\", "/"),
            "page_count": len(doc),
            "is_scanned": is_scanned,
            "total_chars": total_text_length,
            "pages": pages_data,
        }
        logger.info(f"Parsed PDF '{path.name}': {len(doc)} pages, is_scanned={is_scanned}, chars={total_text_length}")
        return result

    @staticmethod
    def load_image_base64(file_path: str) -> str:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {file_path}")
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")


# Global parser instance
document_parser = DocumentParser()
