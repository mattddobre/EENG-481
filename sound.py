import vlc
import time

player = vlc.MediaPlayer("1khz.mp3")
player.play()

# Give VLC time to start
time.sleep(0.5)

# Keep script alive while audio plays
while True:
    state = player.get_state()
    if state in (vlc.State.Ended, vlc.State.Error, vlc.State.Stopped):
        break
    time.sleep(0.1)
