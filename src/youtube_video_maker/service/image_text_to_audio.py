from dataclasses import dataclass

from PIL import Image
from pytesseract import pytesseract
from gtts import gTTS
from playsound import playsound

from . import MetaParams
from .. import Metadata


pytesseract.tesseract_cmd = Metadata.tesseract_cmd

END_NOTE = "Please Like, Share, Subscribe, and Thank you, for watching."

REPLACE_STR = {
    "(i)": "1.",
    "(ii)": "2.",
    "(iii)": "3.",
    "(iv)": "4.",
    "(v)": "5.",
    "(vi)": "6.",
    "(vii)": "7.",
    "(viii)": "8.",
    "(ix)": "9.",
    "(x)": "10.",
    "'": "",

}


class ImageToText:

    def __init__(self, meta_params):
        self.meta_params: MetaParams = meta_params

    def image_to_text(self):

        text_list = []
        if isinstance(self.meta_params.path_to_image, list):
            self.meta_params.path_to_image = list(sorted(self.meta_params.path_to_image))
            for image in self.meta_params.path_to_image:
                img = Image.open(image)
                text = pytesseract.image_to_string(img)
                text_list.append(text)
        else:
            img = Image.open(self.meta_params.path_to_image)
            text = pytesseract.image_to_string(img)
            text_list.append(text)

        text = [" ".join(x.split('\n')) for text in text_list for x in text.split("\n\n")]
        text.append(END_NOTE)
        self.meta_params.title = text[0]
        text = "\n\n".join(text)
        for x, v in REPLACE_STR.items():
            text = text.replace(x, v)

        # open(self.meta_params.text_output_file, "w").write(text)
        return text


class TextToAudio:

    def __init__(self, meta_params):
        self.meta_params: MetaParams = meta_params

    def text_to_audio(self, text, language='en', slow=True, play_sound=False):
        obj = gTTS(text=text, lang=language, slow=slow, tld="co.in")
        obj.save(self.meta_params.audio_file_name)

        # obj.write_to_fp(self.meta_params.audio_file_name)

        if play_sound:
            playsound(obj)
        return obj


# class ImageTextToAudio:
#
#     def __init__(self, text_image_path, audio_file_path, text_output_file, meta_params: MetaParams):
#         self.path_to_image = text_image_path
#         self.audio_file_name = audio_file_path
#         self.text_output_file = text_output_file
#
#         self.title = None
#         self.meta_params = meta_params
#
#     def start(self):
#         self.image_to_text()
#         text = open(self.text_output_file).read()
#         self.text_to_audio(text)
#
#     def image_to_text(self):
#         img = Image.open(self.path_to_image)
#         text = pytesseract.image_to_string(img)
#         print(text)
#         text = [" ".join(x.split('\n')) for x in text.split("\n\n")]
#         text.append(END_NOTE)
#         print(text)
#         self.title = text[0]
#         text = "\n\n".join(text)
#         for x, v in REPLACE_STR.items():
#             text = text.replace(x, v)
#
#         # open(self.text_output_file, "w").write(text)
#         return text
#
#     def text_to_audio(self, text, language='en', slow=True, play_sound=False):
#         obj = gTTS(text=text, lang=language, slow=slow, tld="co.in")
#         # obj.save(self.audio_file_name)
#         obj.write_to_fp(self.audio_file_name)
#
#         if play_sound:
#             playsound(self.audio_file_name)
