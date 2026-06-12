from pydantic import BaseModel
import fitz
from api.utils.text_cleaning import clean_text


def _sanitize_utf8(text: str) -> str:
    """
    Round-trip the string through UTF-8 encode → decode with 'replace' to
    strip any surrogate / malformed code-points that PyMuPDF occasionally
    emits from corrupt PDF streams.  Valid Unicode (including Greek, etc.)
    is preserved; only truly undecodable bytes are turned into U+FFFD.
    """
    return text.encode("utf-8", errors="replace").decode("utf-8", errors="replace")

class PageContent(BaseModel):
    page_number: int
    text: str

class PDFExtractor:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def extract_text(self) -> list[PageContent]:
        """
        Extracts text from the PDF page by page.
        Returns a list of PageContent objects.
        """
        extracted_data = []
        try:
            doc = fitz.open(self.file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                raw = page.get_text()
                text = clean_text(_sanitize_utf8(raw))
                extracted_data.append(PageContent(
                    page_number=page_num + 1,
                    text=text
                ))
            doc.close()
        except Exception as e:
            print(f"Error extracting PDF: {e}")
        return extracted_data
