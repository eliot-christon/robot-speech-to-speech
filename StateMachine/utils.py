import time
import re

#%% BASIC FUNCTIONS ========================================================================================================

def sleep_02():
    time.sleep(0.2)

def time_strftime_to_seconds(time_strftime): # time_strftime: "speech detected at: 03/22/18 15:20:27"
    if time_strftime == None:
        return None
    return time.mktime(time.strptime(time_strftime, "%m/%d/%y %H:%M:%S"))

assert(time_strftime_to_seconds("03/22/24 14:06:46") == 1711112806.0)

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


#%% TOOL RELATED FUNCTIONS =================================================================================================

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

def send_command(command, fast_com_dir):
    with open(fast_com_dir + "command.txt", 'w') as file:
        file.write(command)
        
def get_status(fast_com_dir):
    with open(fast_com_dir + "status.txt", 'r') as file:
        return file.read()

def start_tools(list_tools):
    for tool in list_tools:
        send_command('start', fast_com_dict[tool])

def stop_tools(list_tools):
    for tool in list_tools:
        send_command('stop', fast_com_dict[tool])

def tools_running(list_tools):
    return [get_status(fast_com_dict[tool]) for tool in list_tools]

#%% FILE MANAGEMENT ========================================================================================================

def move_bonjour_to_generated():
    """Move the bonjour.wav file to audio_generated.wav"""
    with open("data/stored/assistant/bonjour.wav", "rb") as file:
        data = file.read()
    with open("data/live/audio_generated.wav", "wb") as file:
        file.write(data)

def empty_data_live_folder():
    # AUDIO
    with open("data/live/audio_recorded.wav", "w", encoding="utf-8") as file:
        file.write("")
    with open("data/live/audio_recorded.raw", "w", encoding="utf-8") as file:
        file.write("")
    with open("data/live/audio_generated.wav", "w", encoding="utf-8") as file:
        file.write("")
    # TEXT
    with open("data/live/text_prompt.txt", "w", encoding="utf-8") as file:
        file.write("")
    with open("data/live/text_generated.txt", "w", encoding="utf-8") as file:
        file.write("")
    with open("data/live/text_transcribed.txt", "w", encoding="utf-8") as file:
        file.write("")
    with open("data/live/time_speech_detected.txt", "w", encoding="utf-8") as file:
        file.write("")
    with open("data/live/text_to_say.txt", "w", encoding="utf-8") as file:
        file.write("")

def empty_time_speech_detected():
    with open("data/live/time_speech_detected.txt", "w", encoding="utf-8") as file:
        file.write("")


#%% READ SPECIFIC FILES ===================================================================================================

def last_speech_detected():
    with open("data/live/time_speech_detected.txt", "r", encoding="utf-8") as file:
        text = file.readlines()
    if len(text) < 1:
        return None
    return text[-1].split(": ")[1].strip()

def last_speech_detected_seconds():
    return time_strftime_to_seconds(last_speech_detected())

def text_transcribed():
    with open("data/live/text_transcribed.txt", "r", encoding="utf-8") as file:
        return file.read().strip()

def generated_sentences():
    with open("data/live/text_generated.txt", "r", encoding="utf-8") as file:
        message = file.read().replace("\n", " ").strip()

    return msg_to_sentences(message)


#%% PROMPTING ==============================================================================================================

prompt_templates = {
    "TheBloke--Mistral-7B-Instruct-v0.1-GGUF" : {"start":"<s>[INST] ", "mid":" [/INST]", "end":["</s>"]},
    "mistral" : {"start":"<s>[INST] ", "mid":" [/INST]", "end":["</s>"]},
    "Hvsq--ARIA-7B-V3-mistral-french-v1-GGUF" : {"start":"<s>[INST] ", "mid":" [/INST]", "end":["</s>"]},
    "TheBloke--LlaMA-Pro-8B-Instruct-GGUF" : {"start":"<|user|>\n", "mid":"\n<|assistant|>", "end":["</s>"]},
    "TheBloke--Llama-2-7B-GGUF" : {"start":"", "mid":"", "end":["</s>"]},
    "llama2" : {"start":"", "mid":"", "end":["</s>"]},
    "TheBloke--EstopianMaid-13B-GGUF" : {"start":"### Instruction:\n", "mid":"\n\n### Response:\n", "end":["</s>", "###"]},
    "TheBloke--openchat-3.5-0106-GGUF" : {"start":"GPT4 Correct User: ", "mid":"<|end_of_turn|>GPT4 Correct Assistant: ", "end":["<|end_of_turn|>", "</s>", "<|end", "<||", "< |end", "< | end"]},
}

def get_prompt_template(model_name:str) -> dict:
    # check if key in model_name
    for key in prompt_templates.keys():
        if key in model_name:
            return prompt_templates[key]
    return {"start":"", "mid":"", "end":["</s>"]}
