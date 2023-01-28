import asyncio
import os
import traceback
from asyncio import sleep
from concurrent.futures import ThreadPoolExecutor
from functools import wraps, partial
from threading import Thread

import toga
from toga.constants import COLUMN, ROW
from toga.style import Pack

from . import Metadata
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


class ProgressButton(toga.Button):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.progress_bar = toga.ProgressBar()
        self.progress_bar.max = None

    def add_progress(self):
        self.add(self.progress_bar)

    def start(self):
        self.progress_bar.start()

    def stop(self):
        self.progress_bar.stop()


def wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    return run


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


@wrap
def text_mp4_process(text):
    audio_object = TextToAudio(MetaParams).text_to_audio(text)

    MetaParams.title = text.strip().split("\n")[0].strip()

    if MetaParams.title:
        output_mp4_file = MetaParams.video_path_name.split("/")
        output_mp4_file.pop()
        output_mp4_file.append(f"{MetaParams.title}.mp4")
        MetaParams.video_path_name = "/".join(output_mp4_file)

    if not MetaParams.video_path_name:
        MetaParams.video_path_name = OUTPUT_MP4_PATH

    MP3ToMP4(
        audio_path=MetaParams.audio_file_name,
        video_path_name=MetaParams.video_path_name,
        temp_path=MetaParams.temp_path,
        input_mp4_image_path=MetaParams.input_mp4_image_path,
        audio_object=audio_object
    )


class YoutubeVideoMaker(toga.App):
    file_video_background_image = None
    text_file_name = None

    def do_clear(self, widget, **kwargs):
        self.converted_text.value = ""
        self.display_video_background_image.image = None

        self.label.text = "Ready."

    def action_btn_clear_and_reset(self, widget):
        create_folders(f"{BASE_OUTPUT_APP}/mp3/")
        create_folders(f"{BASE_OUTPUT_APP}/mp4/")
        create_folders(f"{BASE_OUTPUT_APP}/temp/")
        create_folders(f"{BASE_OUTPUT_APP}/text/")
        self.label.text = "Ready."

    def action_list_videos(self, widget):

        lt = []
        for ix, x in enumerate(os.listdir(f"{BASE_OUTPUT_APP}/mp4/")):
            print(ix, x)
            lt.append([ix, x])

        self.video_list_widget_table.data = lt

    async def action_btn_open_video_background_image_dialog(self, widget):
        try:
            self.file_video_background_image = await self.main_window.open_file_dialog(
                title="Open file with Toga", multiselect=False
            )
            if self.file_video_background_image is not None:
                self.label.text = f"File to open: {self.file_video_background_image}"
                self.display_video_background_image.image = toga.Image(self.file_video_background_image)
            else:
                self.label.text = "No file selected!"
        except ValueError:
            self.label.text = "Open file dialog was canceled"

    async def action_btn_create_video(self, widget):
        self.label.text = "Creating New video. Please wait a moment."
        try:
            text = self.converted_text.value
            MetaParams.input_mp4_image_path = self.file_video_background_image
            self.progress.start()
            await text_mp4_process(text)
            self.progress.stop()
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
            self.progress.stop()
            raise e

    async def action_btn_open_input_text_image_dialog(self, widget):
        try:
            file_name = await self.main_window.open_file_dialog(
                title="Open file with Toga", multiselect=True
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
        self.converted_text.MIN_HEIGHT = 200

        btn_open_video_background_image = toga.Button(
            "Select Video Background Image", on_press=self.action_btn_open_video_background_image_dialog,
            style=btn_style
        )

        self.display_video_background_image = toga.ImageView()

        btn_create_video_style = Pack(flex=1, padding=20, color="Green")
        self.btn_create_video = ProgressButton(
            "Create Video", on_press=self.action_btn_create_video,
            style=btn_create_video_style
        )
        # self.btn_create_video.add_progress()

        btn_clear = toga.Button("Clear", on_press=self.do_clear, style=btn_style)

        btn_clear_and_reset = toga.Button("Reset", on_press=self.action_btn_clear_and_reset, style=btn_style)

        btn_list_videos = toga.Button("Refresh Videos", on_press=self.action_list_videos, style=btn_style)

        # Outermost box
        refresh_box = toga.Box(
            children=[
                btn_clear,
                btn_clear_and_reset,
                btn_list_videos,
            ],
            style=Pack(flex=1, direction=ROW),
        )

        mp4_image_box = toga.Box(
            children=[
                btn_open_video_background_image,
                self.display_video_background_image,
            ],
            style=Pack(flex=1, direction=COLUMN, padding=10,
                       # background_color="#00ffff"
                       ),
        )

        text_box = toga.Box(
            children=[
                btn_open_input_text_image,
                self.converted_text,
            ],
            style=Pack(flex=1, direction=COLUMN, padding=10,
                       # background_color="#ffff00"
                       ),
        )
        text_image_div = toga.Box(
            children=[
                text_box,
                mp4_image_box,
            ],
            style=Pack(flex=1, direction=ROW, background_color="#00ffff", padding=10),
        )

        self.progress = toga.ProgressBar()
        self.progress.max = None

        self.create_video_box = toga.Box(
            children=[
                self.btn_create_video,
                self.progress,
            ],
            style=Pack(flex=1, direction=COLUMN, padding=10),
        )

        self.video_list_widget_table = toga.Table(['SL. NO.', 'Video Name'], style=Pack(padding=10))

        video_list_container = toga.ScrollContainer(
            content=self.video_list_widget_table,  style=Pack(padding=10)
        )

        video_list_box = toga.Box(
            children=[
                video_list_container
            ],
            style=Pack(flex=1, direction=ROW),
        )

        box = toga.Box(
            children=[
                text_image_div,
                self.create_video_box,
                refresh_box,
                self.label,
                video_list_container,
                # self.window_label,
            ],
            style=Pack(flex=1, direction=COLUMN, padding=30),
        )

        # Add the content on the main window
        self.main_window.content = toga.ScrollContainer(content=box, style=Pack(flex=1, direction=COLUMN))
        self.tool_bar()

        # Show the main window
        self.main_window.full_screen = True
        self.main_window.show()

    def tool_bar(self):
        things = toga.Group("Settings")
        cmd0 = toga.Command(
            self.action_set_py_tesseracts_path,
            text="Set PyTesseracts Path",
            tooltip="Perform Set PyTesseracts Path",
            # icon=brutus_icon,
            group=things,
        )

        self.commands.add(cmd0)

    def action0(self):
        pass

    def action_set_py_tesseracts_path(self):
        file_name = self.main_window.open_file_dialog(
            title="Open file", multiselect=False
        )
        if file_name:
            Metadata.tesseract_cmd = file_name


def main():
    return YoutubeVideoMaker()


if __name__ == "__main__":
    app = main()
    app.main_loop()
