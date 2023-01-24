import os
import traceback

import toga
from toga.constants import COLUMN
from toga.style import Pack

from .service import MetaParams
from .service.image_text_to_audio import ImageToText, TextToAudio
from .service.mp3_to_mp4 import MP3ToMP4

# BASE_OUTPUT_APP = get_absolute_path(".temp")
BASE_OUTPUT_APP = ".youtube_video_maker"
OUTPUT_MP3_PATH = f"{BASE_OUTPUT_APP}/mp3/audio_output.mp3"
OUTPUT_MP4_PATH = f"{BASE_OUTPUT_APP}/mp4/video_output.mp4"
OUTPUT_TEMP_PATH = f"{BASE_OUTPUT_APP}/temp/"
OUTPUT_TEXT_PATH = f"{BASE_OUTPUT_APP}/text/text_output.txt"

MetaParams.text_output_file = OUTPUT_TEXT_PATH
MetaParams.video_path_name = OUTPUT_MP4_PATH
MetaParams.audio_file_name = OUTPUT_MP3_PATH
MetaParams.temp_path = OUTPUT_TEMP_PATH


def create_folders(md_path):
    # input_folder = Path(md_path)
    # if input_folder.is_dir():
    #     pass
    # else:
    #     input_folder.mkdir(parents=True)

    is_existing = os.path.isdir(md_path)
    if not is_existing:
        os.makedirs(md_path, exist_ok=True)

    print(md_path)


class YoutubeVideoMaker(toga.App):
    file_video_background_image = None
    text_file_name = None

    def do_clear(self, widget, **kwargs):
        self.label.text = "Ready."

    def action_btn_clear_and_reset(self, widget):
        create_folders(f"{BASE_OUTPUT_APP}/mp3/")
        create_folders(f"{BASE_OUTPUT_APP}/mp4/")
        create_folders(f"{BASE_OUTPUT_APP}/temp/")
        create_folders(f"{BASE_OUTPUT_APP}/text/")
        self.label.text = "Ready."

    async def action_btn_open_video_background_image_dialog(self, widget):
        try:
            self.file_video_background_image = await self.main_window.open_file_dialog(
                title="Open file with Toga", multiselect=False
            )
            if self.file_video_background_image is not None:
                pass
                self.label.text = f"File to open: {self.file_video_background_image}"
            else:
                self.label.text = "No file selected!"
        except ValueError:
            self.label.text = "Open file dialog was canceled"

    def action_btn_create_video(self, widget):
        self.label.text = "Creating New video. Please wait a moment."
        try:

            # ImageToText(MetaParams).image_to_text()
            #
            # text = open(MetaParams.text_output_file).read()

            text = self.converted_text.value
            audio_object = TextToAudio(MetaParams).text_to_audio(text)

            MetaParams.title = text.strip().split("\n")[0].strip()

            if MetaParams.title:
                output_mp4_file = MetaParams.video_path_name.split("/")
                output_mp4_file.pop()
                output_mp4_file.append(f"{MetaParams.title}.mp4")
                MetaParams.video_path_name = "/".join(output_mp4_file)

            if not MetaParams.video_path_name:
                MetaParams.video_path_name = OUTPUT_MP4_PATH

            MetaParams.input_mp4_image_path = self.file_video_background_image

            MP3ToMP4(
                audio_path=MetaParams.audio_file_name,
                video_path_name=MetaParams.video_path_name,
                temp_path=MetaParams.temp_path,
                input_mp4_image_path=MetaParams.input_mp4_image_path,
                audio_object=audio_object
            )
            self.label.text = "Created New video"
        except Exception as e:
            print(e)
            print(e.__traceback__)

            self.main_window.stack_trace_dialog(
                "Error!",
                f"{e}",
                "".join(traceback.format_stack()),
            )
            self.label.text = str(e)
            raise e

    async def action_btn_open_input_text_image_dialog(self, widget):
        try:
            file_name = await self.main_window.open_file_dialog(
                title="Open file with Toga", multiselect=False
            )
            if file_name is not None:
                self.text_file_name = file_name
                MetaParams.path_to_image = file_name
                data = ImageToText(MetaParams).image_to_text()
                self.converted_text.value = data

            else:
                self.label.text = "No file selected!"
        except ValueError:
            self.label.text = "Open file dialog was canceled"

    async def exit_handler(self, app):
        # Return True if app should close, and False if it should remain open
        if await self.main_window.confirm_dialog(
                self.name, "Are you sure you want to quit?"
        ):
            print(f"Label text was '{self.label.text}' when you quit the app")
            return True
        else:
            self.label.text = "Exit canceled"
            return False

    def set_window_label_text(self, num_windows):
        self.window_label.text = f"{num_windows} secondary window(s) open"

    def startup(self):

        print(__file__)
        # Set up main window
        self.main_window = toga.MainWindow(title=self.name)
        self.on_exit = self.exit_handler

        self.input_mp4_image_path = None

        self.total_text = toga.TextInput()

        # Label to show responses.
        self.label = toga.Label("Ready.", style=Pack(padding_top=20))
        self.window_label = toga.Label("", style=Pack(padding_top=20))
        self.window_counter = 0
        self.close_attempts = set()
        self.set_window_label_text(0)

        # Buttons
        btn_style = Pack(flex=1, padding=20)

        def x_print(widget):
            print("ddddddddddddddd")

        btn_open_input_text_image = toga.Button(
            "Select Text Image File", on_press=self.action_btn_open_input_text_image_dialog, style=btn_style
        )
        self.converted_text = toga.MultilineTextInput()

        btn_open_video_background_image = toga.Button(
            "Select Video Background Image", on_press=self.action_btn_open_video_background_image_dialog,
            style=btn_style
        )

        btn_create_video = toga.Button(
            "Create Video", on_press=self.action_btn_create_video,
            style=btn_style
        )

        btn_clear = toga.Button("Clear", on_press=self.do_clear, style=btn_style)

        btn_clear_and_reset = toga.Button("Reset", on_press=self.action_btn_clear_and_reset, style=btn_style)

        # Outermost box
        box = toga.Box(
            children=[
                btn_open_input_text_image,
                self.converted_text,
                btn_open_video_background_image,
                btn_create_video,
                btn_clear,
                btn_clear_and_reset,
                self.label,
                self.window_label,
            ],
            style=Pack(flex=1, direction=COLUMN, padding=30),
        )

        # Add the content on the main window
        self.main_window.content = box

        # Show the main window
        self.main_window.show()


def main():
    return YoutubeVideoMaker()


if __name__ == "__main__":
    app = main()
    app.main_loop()
