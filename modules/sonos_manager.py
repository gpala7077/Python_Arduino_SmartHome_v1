import time
import random
from soco import SoCo


def calc_duration(message):
    return max(2, len(message) / 6) + 6


class Sonos:
    def __init__(self, ip_address):
        self.player = SoCo(ip_address)

    def tts(self, message):
        locale = "en-US"
        self.player.play_uri("x-rincon-mp3radio://translate.google.com/translate_tts?ie=UTF-8&tl=%s&client=tw-ob&q=%s" %
                             (locale, message))

    def speak(self, message):
        current_transport_info = self.player.get_current_transport_info()[u'current_transport_state']
        current_position = self.player.get_current_track_info()[u'position']
        current_uri = self.player.get_current_track_info()[u'uri']

        player_source = "QUEUE"
        if self.player.is_playing_radio:
            player_source = "RADIO"
        elif self.player.is_playing_line_in:
            player_source = "LINE_IN"
        elif self.player.is_playing_tv:
            player_source = "TV"

        duration = calc_duration(message)

        print("Sending TTS.")
        self.tts(message.replace(" ", "+"))
        print("Going to sleep for %d seconds" % duration)
        time.sleep(duration)
        self.player.stop()
        print("Stopped TTS")
        pause = True

        if player_source == "QUEUE":
            if current_transport_info in ["PLAYING", "PAUSED_PLAYBACK"]:
                self.player.play_from_queue(0)
                self.player.seek(current_position)
                pause = (current_transport_info == "PAUSED_PLAYBACK")
        else:
            self.player.play_uri(current_uri)
            pause = (current_transport_info == "STOPPED")

        if pause:
            self.player.pause()
            print("Returned to %s, paused" % player_source)
        else:
            print("Playing from %s again" % player_source)

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
