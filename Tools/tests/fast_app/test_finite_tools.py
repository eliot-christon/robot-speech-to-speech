import time


# T0_ReadAudio
# T1_PersonRecognition
# T2_TextGeneration
# T3_TTS
# T4_ActionSelection
# T5_PerformAction

tool_code = "T3_TTS"

COMMAND_FILE_PATH = "Tools/" + tool_code + "/fast_com/command.txt"
STATUS_FILE_PATH = "Tools/" + tool_code + "/fast_com/status.txt"

def send_command(command):
    with open(COMMAND_FILE_PATH, 'w') as file:
        file.write(command)
        
def get_status():
    with open(STATUS_FILE_PATH, 'r') as file:
        return file.read()


if __name__ == "__main__":
    # Test starting
    print("Sending 'start' command...")
    send_command('start')

    time.sleep(0.1)  # wait for status to be True

    # wait for status to be False
    print("Waiting for status to be True...")
    status = get_status()
    while status != "False":
        print("Status is " + status + ". Waiting...")
        status = get_status()
        time.sleep(0.1)

    print("Status is False. Exiting...")