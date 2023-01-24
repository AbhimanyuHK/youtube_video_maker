import os
from typing import Optional

# os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"

print("p", __file__)

class MetaParams:
    path_to_image: str
    text_output_file: str
    audio_file_name: str
    temp_path = str
    video_path_name: str
    input_mp4_image_path: str

    title: Optional[str]
