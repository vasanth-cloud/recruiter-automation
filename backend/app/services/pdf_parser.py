from pathlib import Path
from PyPDF2 import PdfReader


def parse_resume(file_path: str) -> dict:
    path = Path(file_path)

    if not path.exists():
        return {
            "name": path.stem,
            "text": "",
            "skills": [],
            "experience": [],
            "education": [],
            "email": "",
            "phone": ""
        }

    try:
        reader = PdfReader(str(path))
        text_parts = []

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        full_text = "\n".join(text_parts).strip()

        lines = [line.strip() for line in full_text.splitlines() if line.strip()]
        candidate_name = lines[0] if lines else path.stem

        return {
            "name": candidate_name,
            "text": full_text,
            "skills": [],
            "experience": [],
            "education": [],
            "email": "",
            "phone": ""
        }

    except Exception as e:
        return {
            "name": path.stem,
            "text": "",
            "skills": [],
            "experience": [],
            "education": [],
            "email": "",
            "phone": "",
            "error": str(e)
        }
