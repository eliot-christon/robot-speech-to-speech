import time
import re
import yaml
from Message import Message

#%% BASIC FUNCTIONS ========================================================================================================

def sleep_02():
    time.sleep(0.2)

def time_strftime_to_seconds(time_strftime): # time_strftime: "speech detected at: 03/22/18 15:20:27"
    if time_strftime == None:
        return None
    return time.mktime(time.strptime(time_strftime, "%m/%d/%y %H:%M:%S"))

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

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
        return data

# TESTS

assert(time_strftime_to_seconds("03/22/24 14:06:46") == 1711112806.0)


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
    "T8": "Tools/T8_STT/fast_com/",
    "T9": "Tools/T9_LEDS/fast_com/"
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

def move_hi_to_say():
    """Move the hi.txt file to text_to_say.txt"""
    with open("data/stored/assistant/hi.txt", "r", encoding="utf-8") as file:
        text = file.read()
    with open("data/live/text_to_say.txt", "w", encoding="utf-8") as file:
        file.write(text)

def move_bye_to_say():
    """Move the bye.txt file to text_to_say.txt"""
    with open("data/stored/assistant/bye.txt", "r", encoding="utf-8") as file:
        text = file.read()
    with open("data/live/text_to_say.txt", "w", encoding="utf-8") as file:
        file.write(text)

def clear_data_live_folder():
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

def clear_time_speech_detected():
    with open("data/live/time_speech_detected.txt", "w", encoding="utf-8") as file:
        file.write("")

def clear_text_transcribed():
    with open("data/live/text_transcribed.txt", "w", encoding="utf-8") as file:
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
    "gemma"    : {
        "user"      : {"start":"<start_of_turn>user\n",     "end":["<end_of_turn>\n"]},
        "assistant" : {"start":"<start_of_turn>model\n",    "end":["<end_of_turn>model\n"]},
        "system"    : {"start":"<start_of_turn>system\n",   "end":["<end_of_turn>system\n"]}},
    "test"     : {
        "user"      : {"start": "<s>[INST]",                "end":["[/INST]"]},
        "assistant" : {"start":"",                          "end":["</s>"]},
        "system"    : {"start":"<s>[INST] <<SYS>>",         "end":["<</SYS>>\n"]}},
    "mistral"  : {
        "user"      : {"start": "<s>[INST]",                "end":["[/INST]"]},
        "assistant" : {"start":"",                          "end":["</s>"]},
        "system"    : {"start":"<s>[INST] <<SYS>>",         "end":["<</SYS>>\n"]}},
    "llama2"   : {
        "user"      : {"start": "<s>[INST]",                "end":["[/INST]"]},
        "assistant" : {"start":"",                          "end":["</s>"]},
        "system"    : {"start":"<s>[INST] <<SYS>>\n",       "end":["\n<</SYS>>\n\n"]}},
    "openchat" : {
        "user"      : {"start":"GPT4 Correct User: ",       "end":["<|end_of_turn|>"]},
        "assistant" : {"start":"GPT4 Correct Assistant: ",  "end":["<|end_of_turn|>", "</s>", "<|end", "<||", "< |end", "< | end"]},
        "system"    : {"start":"<|system|>\n",              "end":["<|/system|>\n"]}},
    "openhermes" : {
        "user"      : {"start":"<|im_start|>user\n",        "end":["<|im_end|>\n"]},
        "assistant" : {"start":"<|im_start|>assistant\n",   "end":["<|im_end|>\n", "<|im_end|>", "###"]},
        "system"    : {"start":"<|im_start|>system\n",      "end":["<|im_end|>\n"]}},
}

def get_prompt_template(model_name:str) -> dict:
    # check if key in model_name
    for key in prompt_templates.keys():
        if key in model_name:
            return prompt_templates[key]
    return {"start":"", "mid":"", "end":["</s>"]}


def build_prompt(model_name:str, list_messages:list) -> str:
    prompt_template = get_prompt_template(model_name)

    prompt = ""
    
    last_user_message = True

    for message in list_messages[::-1]:
        if last_user_message and message.role == "user":
            prompt = prompt_template[message.role]["start"] + message.content + " (réponds moi en deux phrases uniquement)" + prompt_template[message.role]["end"][0] + prompt
            last_user_message = False
        elif message.role in prompt_template.keys():
            prompt = prompt_template[message.role]["start"] + message.content + prompt_template[message.role]["end"][0] + prompt
        else:
            raise ValueError(f"Unknown role: {message.role}")
    
    prompt = prompt.replace(prompt_template["system"]["end"][0] + prompt_template["system"]["start"], "\n")
    prompt = prompt.replace("<</SYS>>\n<s>[INST]", "<</SYS>>\n")

    return prompt

# TESTS

assert(get_prompt_template("mistral") == prompt_templates["mistral"])
list_messages = [Message("system", "réponds en deux phrases en français"), Message("user", "Hello"), Message("assistant", "Hi")]
assert(build_prompt("test", list_messages) == "<s>[INST] <<SYS>>réponds en deux phrases en français<</SYS>>\nHello (réponds moi en deux phrases uniquement)[/INST]Hi</s>")


#%% LEDS ==================================================================================================================

def write_led_color(color):
    with open("data/live/led_rgb.txt", "w", encoding="utf-8") as file:
        file.write(color)

def leds_cyan():
    write_led_color("cyan")
    send_command("start", fast_com_dict["T9"])

def leds_magenta():
    write_led_color("magenta")
    send_command("start", fast_com_dict["T9"])

def leds_yellow():
    write_led_color("yellow")
    send_command("start", fast_com_dict["T9"])

def leds_red():
    write_led_color("red")
    send_command("start", fast_com_dict["T9"])

def leds_green():
    write_led_color("green")
    send_command("start", fast_com_dict["T9"])

def leds_blue():
    write_led_color("blue")
    send_command("start", fast_com_dict["T9"])

def leds_reset():
    send_command("reset", fast_com_dict["T9"])