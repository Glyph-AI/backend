import pdf2image
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract


class ImageProcessor:
    def process(self, filepath):
        with open("/temp/output.txt", "w+") as f:
            text = pytesseract.image_to_string(Image.open(filepath))
            f.write(text)

        return "/temp/output.txt"
