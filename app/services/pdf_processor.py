import pdf2image
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

class PdfProcessor():
    def process(self, filepath):
        # read pdf in
        images = pdf2image.convert_from_path(filepath)
        with open("/temp/output.txt", "w+") as f:
            for idx, pg in enumerate(images):
                page_text = pytesseract.image_to_string(pg)
                f.write(page_text)
            

        return "/temp/output.txt"

        