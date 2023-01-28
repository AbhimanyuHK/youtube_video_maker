from pathlib import Path

PROJECT_PATH = Path(str(__file__).split("src", maxsplit=1)[0])
print(PROJECT_PATH)


class Metadata:
    tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def get_absolute_path(x_path):
    return PROJECT_PATH / x_path
