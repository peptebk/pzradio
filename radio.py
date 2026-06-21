import time
import vlc
import stations
import os 

os.environ['PATH'] = os.path.dirname(__file__) + r'vlc' + os.pathsep + os.environ['PATH']

class Radio:
    """Воспроизведение аудио через VLC"""

    def __init__(self):
        self.instance = vlc.Instance()
        self.media_player = None
        self.is_playing = False
        self.current_url = None

    def play(self, url):
        """Воспроизводит радиопоток"""
        try:
            self.stop()
            time.sleep(0.3)
            
            self.media_player = self.instance.media_list_player_new()
            media = self.instance.media_new(url)
            media_list = self.instance.media_list_new()
            media_list.add_media(media)
            
            self.media_player.set_media_list(media_list)
            self.media_player.play()
            
            self.is_playing = True
            self.current_url = url
            return True
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.is_playing = False
            return False

    def stop(self):
        """Останавливает воспроизведение"""
        try:
            if self.media_player:
                self.media_player.stop()
            self.is_playing = False
            return True
        except Exception as e:
            return False

    def set_volume(self, volume):
        """Устанавливает громкость (0-100)"""
        try:
            if self.media_player:
                volume = max(0, min(100, volume))
                player = self.media_player.get_media_player()
                if player:
                    player.audio_set_volume(volume)
                    return True
            return False
        except Exception:
            return False

    def get_volume(self):
        """Получает текущую громкость"""
        try:
            if self.media_player:
                player = self.media_player.get_media_player()
                if player:
                    return player.audio_get_volume()
            return 50
        except Exception:
            return 50