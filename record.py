
import vlc
import os
import time
from datetime import datetime
import getpass


class Recorder:
    """Менеджер записи аудиопотока через VLC"""

    def __init__(self):
        self.instance = vlc.Instance()
        self.media_player = None
        self.is_recording = False
        self.current_file = None
        self.recordings_folder = rf"C:\Users\{getpass.getuser()}\Videos\pz-radio"
        
        if not os.path.exists(self.recordings_folder):
            os.makedirs(self.recordings_folder)

    def start_record(self, stream_url, station_name="Recording"):
        """Начинает запись радиопотока в MP3"""
        if self.is_recording:
            return False

        try:
            if not os.path.exists(self.recordings_folder):
                os.makedirs(self.recordings_folder)
            
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{station_name}_{timestamp}.mp3"
            filepath = os.path.join(self.recordings_folder, filename)
            filepath = os.path.abspath(filepath).replace("\\", "/")
            self.current_file = filepath
            
            media = self.instance.media_new(stream_url)
            sout_option = f":sout=#transcode{{acodec=mpga,ab=128,channels=2}}:standard{{access=file,mux=raw,dst={filepath}}}"
            media.add_option(sout_option)
            
            self.media_player = self.instance.media_list_player_new()
            media_list = self.instance.media_list_new()
            media_list.add_media(media)
            self.media_player.set_media_list(media_list)
            self.media_player.play()
            time.sleep(1)
            
            self.is_recording = True
            return True
            
        except Exception as e:
            print(f"Ошибка при запуске записи: {e}")
            self.is_recording = False
            return False

    def stop_record(self):
        """Останавливает запись"""
        if not self.is_recording or not self.media_player:
            return False

        try:
            self.media_player.stop()
            time.sleep(0.5)
            
            self.is_recording = False
            file_saved = self.current_file
            self.current_file = None
            
            if file_saved and os.path.exists(file_saved):
                file_size_mb = os.path.getsize(file_saved) / (1024 * 1024)
                print(f"Запись сохранена: {file_saved} ({file_size_mb:.1f} МБ)")
            return True
        except Exception as e:
            print(f"Ошибка при остановке записи: {e}")
            self.is_recording = False
            return False

    def get_recordings_folder(self):
        return os.path.abspath(self.recordings_folder)
