import subprocess
import time

server_processes = []


def start_servers():

    # Command to start each server
    server_T6_command = "py -2.7 Tools/T6_RecordAudio/fast_app.py"
    server_T7_command = "py -2.7 Tools/T7_CaptureImages/fast_app.py"
    server_T8_command = "py -3.11 Tools/T8_STT/fast_app.py"
    server_T3_command = "py -3.10 Tools/T3_TTS/fast_app.py"
    server_T0_command = "py -2.7 Tools/T0_ReadAudio/fast_app.py"

    # Start each server in a separate subprocess
    server_processes.append(subprocess.Popen(server_T6_command, shell=True))
    server_processes.append(subprocess.Popen(server_T7_command, shell=True))
    server_processes.append(subprocess.Popen(server_T8_command, shell=True))
    server_processes.append(subprocess.Popen(server_T3_command, shell=True))
    server_processes.append(subprocess.Popen(server_T0_command, shell=True))


def stop_servers():
    # Terminate each server process
    for process in server_processes:
        process.terminate()
    # Wait for all processes to terminate
    for process in server_processes:
        process.wait()

if __name__ == "__main__":
    try:
        start_servers()

        # Keep the script running until a keyboard interrupt occurs
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected. Stopping servers...")
        stop_servers()