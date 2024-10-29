import os
import yt_dlp
import asyncio
from concurrent.futures import ThreadPoolExecutor

from utils.conf import PATH_SAVED_VIDEO


class DownloadManager:
    def __init__(self, id_name, url, output_path=PATH_SAVED_VIDEO, resolution="quality_high"):
        self.output_path = output_path
        self.id_name = id_name
        self.url = url
        self.resolution = resolution
        self.download_status = "Not started"
        self.estimated_time = None

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            self.download_status = {"percent": d['_percent_str'], "total_bytes_str": d['_total_bytes_str'],
                                    "speed_str": d['_speed_str'], "ETA": d['_eta_str']}
            self.estimated_time = d['_eta_str']
        elif d['status'] == 'finished':
            self.download_status = "Download finished"
            self.estimated_time = None
        elif d['status'] == 'error':
            self.download_status = "An error occurred during the download"
            self.estimated_time = None

    def create_manager(self):
        # Удаляем расширение .mp4 из id_name для правильного формирования имени файла
        base_name = os.path.splitext(self.id_name)[0]
        if self.resolution == "quality_low":
            self.resolution = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]"
        elif self.resolution == "quality_medium":
            self.resolution = "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]"
        elif self.resolution == "quality_high":
            self.resolution = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best"

        ydl_opts = {
            'format': self.resolution,
            'socket_timeout': 60,
            'quiet': True,
            'outtmpl': os.path.join(self.output_path, f"{base_name}.%(ext)s"),  # Используем base_name
            'progress_hooks': [self.progress_hook],
            'merge_output_format': 'mp4'
        }
        return yt_dlp.YoutubeDL(ydl_opts)

    def get_info_video(self) -> dict:
        try:
            with self.create_manager() as ydl:
                info_dict = ydl.extract_info(self.url, download=False)
            return info_dict
        except Exception as error:
            print(f"Error retrieving video info: {error}")

    async def download_video_async(self):
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(pool, self.download_video_sync)

    def download_video_sync(self):
        try:
            with self.create_manager() as ydl:
                ydl.download([self.url])
        except Exception as error:
            self.download_status = f"Error downloading video: {error}"
            self.estimated_time = None
            print(self.download_status)

    def delete_video(self):
        path_video = os.path.join(self.output_path, f"{os.path.splitext(self.id_name)[0]}.mp4")
        print(f"Deleting video {path_video}")
        try:
            os.unlink(path_video)
            print(f"File {path_video} has been deleted successfully.")
        except FileNotFoundError:
            print(f"File {path_video} not found.")
        except PermissionError:
            print(f"No permission to delete {path_video}.")
        except Exception as e:
            print(f"Error occurred while deleting file: {e}")

    def get_download_status(self):
        return {
            "status": self.download_status,
            "estimated_time": self.estimated_time
        }
