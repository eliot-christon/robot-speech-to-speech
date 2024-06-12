import time
from .utils import send_command


if __name__ == '__main__':
    while True:
        try:
            send_command("bye", "Tools/T11_Gesture/fast_com/")
            time.sleep(60)
        except KeyboardInterrupt:
            break