import vlc
import time

player = vlc.MediaPlayer("1khz.mp3")
player.play()

# Give VLC time to start
time.sleep(0.5)

while True:
    state = player.get_state()

    if state == vlc.State.Ended:
        player.stop()            # Stop first
        player.set_position(0.0) # Rewind to beginning
        player.play()            # Play again

    elif state == vlc.State.Error:
        print("Playback error")
        break

    time.sleep(0.1)
