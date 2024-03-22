import time
import re
import logging

def sleep_02():
    time.sleep(0.2)

def send_command(command, fast_com_dir):
    with open(fast_com_dir + "command.txt", 'w') as file:
        file.write(command)
        
def get_status(fast_com_dir):
    with open(fast_com_dir + "status.txt", 'r') as file:
        return file.read()

fast_com_dict = {
    "T0": "Tools/T0_ReadAudio/fast_com/",
    "T1": "Tools/T1_PersonRecognition/fast_com/",
    "T2": "Tools/T2_TextGeneration/fast_com/",
    "T3": "Tools/T3_TTS/fast_com/",
    "T4": "Tools/T4_ActionSelection/fast_com/",
    "T5": "Tools/T5_PerformAction/fast_com/",
    "T6": "Tools/T6_RecordAudio/fast_com/",
    "T7": "Tools/T7_CaptureImages/fast_com/",
    "T8": "Tools/T8_STT/fast_com/"
}

def start_tools(list_tools):
    logging.info("Starting tools: " + str(list_tools))
    for tool in list_tools:
        send_command('start', fast_com_dict[tool])

def stop_tools(list_tools):
    logging.info("Stopping tools: " + str(list_tools))
    for tool in list_tools:
        send_command('stop', fast_com_dict[tool])

def tools_running(list_tools):
    return [get_status(fast_com_dict[tool]) for tool in list_tools]

def last_speech_detected():
    with open("data/live/time_speech_detected.txt", "r", encoding="utf-8") as file:
        text = file.readlines()
    if len(text) < 1:
        return None
    return text[-1].split(": ")[1].strip()

def time_strftime_to_seconds(time_strftime): # time_strftime: "speech detected at: 03/22/18 15:20:27"
    if time_strftime == None:
        return None
    return time.mktime(time.strptime(time_strftime, "%m/%d/%y %H:%M:%S"))

def last_speech_detected_seconds():
    return time_strftime_to_seconds(last_speech_detected())

assert(time_strftime_to_seconds("03/22/24 14:06:46") == 1711112806.0)

def text_transcribed():
    with open("data/live/text_transcribed.txt", "r", encoding="utf-8") as file:
        return file.read().strip()

def msg_to_sentences(msg):
    """ Convert a message to phrases """
    phrases = []
    current_phrase = ""

    ponctuation_marks = [".", "!", "?", '...', ':']
    pattern = '(' + '|'.join(re.escape(p) for p in ponctuation_marks) + ')'

    # Split the message by punctuation marks
    for sentence in re.split(pattern, msg):
        if sentence.strip():  # Check if the sentence is not empty
            if sentence.endswith(tuple(ponctuation_marks)):
                current_phrase += sentence.strip()
                if len(current_phrase) > 2:
                    phrases.append(current_phrase)
                current_phrase = ""
            else:
                current_phrase += sentence.strip()
    
    return phrases, current_phrase

def generated_sentences():
    with open("data/live/text_generated.txt", "r", encoding="utf-8") as file:
        message = file.read().replace("\n", " ").strip()

    return msg_to_sentences(message)
    