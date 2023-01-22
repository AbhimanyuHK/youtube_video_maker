from PIL import Image
from pytesseract import pytesseract
from gtts import gTTS
from playsound import playsound

pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

END_NOTE = "Please Like, Share, Subscribe, and Thank you, for watching."


class ImageTextToAudio:

    def __init__(self, text_image_path, audio_file_path):
        self.path_to_image = text_image_path
        self.audio_file_name = audio_file_path
        self.title = None

    def start(self):
        text = self.image_to_text()
        self.text_to_audio(text)

    def image_to_text(self):
        img = Image.open(self.path_to_image)
        text = pytesseract.image_to_string(img)
        print(text)
        text = [" ".join(x.split('\n')) for x in text.split("\n\n")]
        self.title = text[0]
        text.append(END_NOTE)
        print(text)
        text = "\n\n".join(text)
        return text

    def text_to_audio(self, text, language='en', slow=True, play_sound=False):
        obj = gTTS(text=text, lang=language, slow=slow, tld="co.in")
        obj.save(self.audio_file_name)

        if play_sound:
            playsound(self.audio_file_name)
