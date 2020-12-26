import random
import time
from soco import SoCo
import pyttsx3


class Sonos:
    """SoCo class container."""

    def __init__(self, ip_address):
        self.player = SoCo(ip_address)
        self.engine = pyttsx3.init()
        self.engine.setProperty('voice', 'english+m7')
        self.engine.setProperty('rate', 125)

    def tts(self, message):
        """Sends and plays string message using google's tts"""

        self.engine.save_to_file(message, '/home/gerardo/IoT/audio_clips/voice.mp3') # Add this folder to shared drive
        self.engine.runAndWait()
        self.player.music_library.start_library_update()
        time.sleep(.25)
        self.player.play_uri('x-file-cifs://192.168.50.173/Share/voice.mp3')

    def speak(self, message):
        current_transport_info = self.player.get_current_transport_info()[u'current_transport_state']
        current_position = self.player.get_current_track_info()[u'position']
        current_uri = self.player.get_current_track_info()[u'uri']

        duration = max(2, len(message) / 6)
        self.tts(message)
        time.sleep(duration)
        self.player.stop()
        pause = True

        if current_transport_info in ["PLAYING", "PAUSED_PLAYBACK"]:
            self.player.play_from_queue(0)
            self.player.seek(current_position)
            pause = (current_transport_info == "PAUSED_PLAYBACK")
        else:
            self.player.play_uri(current_uri)
            pause = (current_transport_info == "STOPPED")

        if pause:
            self.player.pause()

    def listen(self, playlist='random'):
        print('Listening to {}'.format(playlist))
        self.player.stop()
        self.player.clear_queue()
        favorites = self.player.get_sonos_playlists()
        if playlist != 'random':
            for track in range(len(favorites)):
                name = str(favorites[track])
                if playlist in name:
                    self.player.add_uri_to_queue(favorites[track].resources[0].uri)
                    self.player.play()

        else:
            random_playlist = random.choice(favorites)
            self.player.add_uri_to_queue(random_playlist.resources[0].uri)
            self.player.play()

