import time

def send_command(command, fast_com_dir):
    with open(fast_com_dir + "command.txt", 'w') as file:
        file.write(command)
        
def get_status(fast_com_dir):
    with open(fast_com_dir + "status.txt", 'r') as file:
        return file.read()


if __name__ == "__main__":

    FAST_COM_T0 = "Tools/T0_ReadAudio/fast_com/"
    FAST_COM_T3 = "Tools/T3_TTS/fast_com/"
    FAST_COM_T6 = "Tools/T6_RecordAudio/fast_com/"
    FAST_COM_T8 = "Tools/T8_STT/fast_com/"

    # start recording and STT at the same time
    print("Recording and STT...")
    send_command('start', FAST_COM_T6)
    send_command('start', FAST_COM_T8)

    # Wait for a while to simulate some recording and STT time
    print("Waiting 5 seconds...")
    time.sleep(5)

    # stop recording and STT at the same time
    print("Stopping recording and STT...")
    send_command('stop', FAST_COM_T6)
    send_command('stop', FAST_COM_T8)

    # while STT status is running, wait
    print("Waiting for STT to finish...")
    status_T8 = get_status(FAST_COM_T8)
    while status_T8 != "False":
        print("STT status is " + status_T8 + ". Waiting...")
        status_T8 = get_status(FAST_COM_T8)
        time.sleep(0.2)

    # write the STT result from text_transcribed.txt to text_generated.txt
    print("Writing the STT result to text_generated.txt...")

    with open("data/live/text_transcribed.txt", "r", encoding="utf-8") as file:
        text = file.read()
    with open("data/live/text_generated.txt", "w", encoding="utf-8") as file:
        file.write(text)
    
    # start TTS
    print("Starting TTS...")
    send_command('start', FAST_COM_T3)
    time.sleep(0.2)

    # while TTS status is running, wait
    print("Waiting for TTS to finish...")
    status_T3 = get_status(FAST_COM_T3)
    while status_T3 != "False":
        print("TTS status is " + status_T3 + ". Waiting...")
        status_T3 = get_status(FAST_COM_T3)
        time.sleep(0.2)
    
    # Read the Audio file generated by TTS
    print("Reading the audio file generated by TTS...")
    send_command('start', FAST_COM_T0)

    # while ReadAudio status is running, wait
    print("Waiting for ReadAudio to finish...")
    status_T0 = get_status(FAST_COM_T0)
    while status_T0 != "False":
        print("ReadAudio status is " + status_T0 + ". Waiting...")
        status_T0 = get_status(FAST_COM_T0)
        time.sleep(0.2)
    
    print("All servers have finished their tasks.")
    print("The audio file generated by TTS has been read.")
    print("The text generated by STT is in text_generated.txt.")
    print("The audio file generated by TTS is in data/live/audio_generated.wav.")

    print("Exiting...")
