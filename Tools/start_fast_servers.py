import subprocess
import time

server_processes = []


def start_servers():

    # Command to start each server
    server_command_T = [None] * 9
    server_command_T[0] = "py -2.7 Tools/T0_ReadAudio/fast_app.py"
    server_command_T[2] = "py -3.11 Tools/T2_TextGeneration/fast_app.py"
    server_command_T[3] = "py -3.10 Tools/T3_TTS/fast_app.py"
    server_command_T[6] = "py -2.7 Tools/T6_RecordAudio/fast_app.py"
    server_command_T[7] = "py -2.7 Tools/T7_CaptureImages/fast_app.py"
    server_command_T[8] = "py -3.11 Tools/T8_STT/fast_app.py"

    # Start each server in a separate subprocess
    for server_command in server_command_T:
        if server_command:
            server_processes.append(subprocess.Popen(server_command, shell=True))


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