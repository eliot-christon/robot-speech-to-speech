from .State import State
from .utils import \
    last_speech_detected_seconds, \
    text_transcribed, \
    tools_running, \
    stop_tools, \
    send_command, \
    get_clean_generated_sentences, \
    clear_time_speech_detected, \
    clear_data_live_folder, \
    clear_text_transcribed, \
    clean_text, \
    play_sound_effect, \
    build_prompt, \
    load_yaml, \
    leds_blue, \
    leds_yellow, \
    leds_green, \
    leds_cyan, \
    leds_reset
from .Message import Message
import logging
import time

class StateMachine:
    """State machine for the NAO robot.
    The states are predefined in the __init__ method.
    Basically, the state machine is a loop that checks the conditions of the current state to determine the next state.
    The conditions are defined in the conditions dictionary.
    If you wish to add a new state, you must add it to the states dictionary and define the conditions in the conditions dictionary."""

    def __init__(self):
        self.states = {
            "WAIT"      : State(number=0, name="WAIT",
                                start_tools=['T6', 'T8'],
                                stop_tools=['T9'],
                                on_enter=(leds_reset,)),
            "IDENTIFY"  : State(number=14, name="IDENTIFY",
                                start_tools=['T1'],
                                on_enter=(leds_blue,),
                                on_exit=(self.store_person_recognized,),
                                stop_tools=['T6', 'T8']),
            "GEN_HI"    : State(number=13, name="GEN_HI",
                                start_tools=['T3'],
                                on_enter=(self.edit_first_phrase, leds_yellow)),
            "CONV"      : State(number=1, name="CONV",
                                start_tools=['T0'],
                                on_enter=(self.init_current_conversation, self.gesture_hi),
                                on_exit=(clear_time_speech_detected,)),
            "LISTEN"    : State(number=2, name="LISTEN",
                                start_tools=['T6', 'T8'],
                                on_enter=(clear_time_speech_detected, self.add_text_generated_to_conversation, self.update_time_when_entered_listen, clear_text_transcribed, leds_green),
                                stop_tools=['T11']),
            "CONTEXT"   : State(number=10, name="CONTEXT",
                                stop_tools=['T6', 'T8'],
                                on_enter=(leds_blue,)),
            "START_GEN" : State(number=3, name="START_GEN",
                                start_tools=['T2'],
                                on_enter=(self.add_transcribed_to_conversation, self.edit_prompt, self.update_time_when_entered_start_gen, self.filler_sound)),
            "GEN"       : State(number=4, name="GEN",
                                on_exit =(self.write_text_to_say, clear_time_speech_detected, leds_blue)),
            "TTS_AS"    : State(number=5, name="TTS_AS",
                                start_tools=['T3', 'T4'],
                                on_enter=(leds_cyan,)),
            "SAY_A"     : State(number=6, name="SAY_A",
                                start_tools=['T0', 'T11'],
                                on_enter=(self.update_sentences_said,)),
            "ACT_A"     : State(number=7, name="ACT_A",
                                start_tools=['T5']),
            "ACT_B"     : State(number=8, name="ACT_B",
                                start_tools=['T5']),
            "SAY_B"     : State(number=9, name="SAY_B",
                                start_tools=['T0', 'T11'],
                                on_enter=(self.update_sentences_said,)),
            "GEN_BYE"   : State(number=12, name="GEN_BYE",
                                start_tools=['T3'],
                                stop_tools=['T6', 'T8', 'T11'],
                                on_enter=(self.edit_last_phrase, leds_yellow)),
            "BYE"       : State(number=11, name="BYE",
                                start_tools=['T0'],
                                on_enter=(self.gesture_bye,),
                                stop_tools=['T8']),
        }

        self.conditions = {
            "WAIT"      : {"IDENTIFY"   : self.cond_start},
            "IDENTIFY"  : {"GEN_HI"     : self.cond_T1_finished},
            "GEN_HI"    : {"CONV"       : self.cond_T03_finished},
            "CONV"      : {"LISTEN"     : self.cond_T068_finished},
            "LISTEN"    : {"CONTEXT"    : self.cond_end_sentence,       "GEN_BYE"   : self.cond_nothing_said},
            "CONTEXT"   : {"START_GEN"  : self.cond_T10_finished},
            "START_GEN" : {"GEN"        : self.cond_not_empty_text_gen},
            "GEN"       : {"TTS_AS"     : self.cond_one_sentence,       "LISTEN"    : self.cond_nothing_to_say},
            "TTS_AS"    : {"SAY_A"      : self.cond_T03_finished,       "ACT_A"     : self.cond_T45_finished},
            "SAY_A"     : {"ACT_B"      : self.cond_T45_finished},
            "ACT_A"     : {"SAY_B"      : self.cond_T03_finished},
            "SAY_B"     : {"GEN_BYE"    : self.cond_bye,                "GEN"       : self.cond_else},
            "ACT_B"     : {"GEN_BYE"    : self.cond_bye,                "GEN"       : self.cond_else},
            "GEN_BYE"   : {"BYE"        : self.cond_T03_finished},
            "BYE"       : {"WAIT"       : self.cond_T068_finished},
        }

        self.current_state = self.states["WAIT"]
        self.next_state = None

        # thresholds (in seconds)
        self.threshold_nothing_said  = 8
        self.threshold_recently_said = 3
        self.threshold_end_sentence  = 2
        self.threshold_nothing_gen   = 2

        # key words
        self.key_words = {
            "start" : ["bonjour", "salut" , "coucou"],
            "bye"   : ["au revoir", "bye", "ciao", "à plus", "à bientôt", "à la prochaine", "bye bye", "goodbye", "good bye"],
        }

        self.sentences_said = []
        self.sentences_to_say = []
        self.current_sentence_generated = ""
        self.model_name = load_yaml("Tools/parameters.yaml")["T2_TextGeneration"]["model_name"]

        self.time_when_entered_listen = None
        self.time_when_entered_start_gen = None

        # conversation
        self.current_conversation = []
        self.person_recognized = "Unknown"
        self.first_phrase = ""

        logging.info("StateMachine initialized")

#%% METHODS ===============================================================================================================
    
    def gesture_hi(self):
        """Send the command to the gesture tool to make the robot wave its hand and point himself."""
        send_command("hi", "Tools/T11_Gesture/fast_com/")
    
    def gesture_bye(self):
        """Send the command to the gesture tool to make the robot wave its hand."""
        send_command("bye", "Tools/T11_Gesture/fast_com/")
    
    def filler_sound(self):
        """Play a filler sound effect. (Generally used when the robot is thinking, to minimize awkward silence.)"""
        # play_sound_effect("filler")
        pass # for now, no filler sounds, because they are very inadequate
    
    def store_person_recognized(self):
        """Store the name of the person recognized in the person_recognized file."""
        with open("data/live/person_recognized.txt", "r", encoding="utf-8") as file:
            person_recognized = file.read()
        self.person_recognized = person_recognized

    def edit_first_phrase(self):
        """Edit and write the first phrase to say in text_to_say, by replacing the [prenom] tag by the name of the person recognized."""
        with open("data/stored/assistant/hi.txt", "r", encoding="utf-8") as file:
            hi_content = file.read()
        self.first_phrase = hi_content.replace("[prenom]", self.person_recognized.split("_")[0].capitalize())
        # now write the first phrase in the text_to_say file
        with open("data/live/text_to_say.txt", "w", encoding="utf-8") as file:
            file.write(self.first_phrase)
    
    def edit_last_phrase(self):
        """Edit and write the last phrase to say in text_to_say, by replacing the [prenom] tag by the name of the person recognized."""
        with open("data/stored/assistant/bye.txt", "r", encoding="utf-8") as file:
            bye_content = file.read()
        bye_content = bye_content.replace("[prenom]", self.person_recognized.split("_")[0].capitalize())
        # now write the last phrase in the text_to_say file
        with open("data/live/text_to_say.txt", "w", encoding="utf-8") as file:
            file.write(bye_content)
        
    def init_current_conversation(self):
        """Initialize the current conversation with the system context and the first phrase to say."""
        with open("data/stored/assistant/context.txt", "r", encoding="utf-8") as file:
            system_context = file.read()
        self.current_conversation = [
            Message(role="system",    content=system_context,    timestamp=time.time()),
            Message(role="assistant", content=self.first_phrase, timestamp=time.time())
        ]
        # could also add person info in system context
        with open("data/live/text_generated.txt", "w", encoding="utf-8") as file:
            file.write("")

    def update_next_state(self):
        """Update the next state based on the conditions of the current state."""
        else_state = self.current_state
        for potential_next_state, condition in self.conditions[self.current_state.name].items():
            if condition() and condition != self.cond_else:
                self.next_state = self.states[potential_next_state]
                return
            elif condition == self.cond_else:
                else_state = self.states[potential_next_state]
        self.next_state = else_state
    
    def write_text_to_say(self):
        with open("data/live/text_to_say.txt", "w", encoding="utf-8") as file:
            file.write(" ".join(self.sentences_to_say))

    def update_sentences_to_say(self):
        sentences, current_sentence_generated = get_clean_generated_sentences()
        self.sentences_to_say = [sentence for sentence in sentences if sentence not in self.sentences_said]
        self.current_sentence_generated = current_sentence_generated
    
    def update_sentences_said(self):
        self.sentences_said += self.sentences_to_say
        self.sentences_to_say = []
    
    def update_time_when_entered_listen(self):
        """Update the time when entered listen state."""
        self.time_when_entered_listen = time.time()
    
    def update_time_when_entered_start_gen(self):
        self.time_when_entered_start_gen = time.time()
    
    def add_transcribed_to_conversation(self):
        """Adds the text from the transcribed file to the current conversation."""
        with open("data/live/text_transcribed.txt", "r", encoding="utf-8") as file:
            text = file.read()
        self.current_conversation.append(Message(role="user", content=text, timestamp=time.time()))

    def add_text_generated_to_conversation(self):
        """Adds the text from the generated file to the current conversation."""
        with open("data/live/text_generated.txt", "r", encoding="utf-8") as file:
            text = file.read()
        text = clean_text(text)
        if text not in ["", " ", "."]:
            self.current_conversation.append(Message(role="assistant", content=text, timestamp=time.time()))

    def edit_prompt(self):
        """Edit the prompt file with the current conversation."""
        text = build_prompt(self.current_conversation)
        with open("data/live/text_prompt.txt", "w", encoding="utf-8") as file:
            file.write(text)
    
    def empty_time_speech_detected(self):
        """Empty the time_speech_detected file only."""
        with open("data/live/time_speech_detected.txt", "w", encoding="utf-8") as file:
            file.write("")
    
#%% CONDITIONS ==========================================================================================================
        
    def cond_start(self):
        lsds = last_speech_detected_seconds()
        if lsds == None:
            return False
        text = text_transcribed()
        return (abs(lsds - time.time()) < self.threshold_recently_said) and any(word in text.lower() for word in self.key_words["start"])

    def cond_end_sentence(self):
        lsds = last_speech_detected_seconds()
        if lsds == None:
            return False
        with open("data/live/text_transcribed.txt", "r", encoding="utf-8") as file:
            text = file.read()
        return abs(lsds - time.time()) > self.threshold_end_sentence and len(text) > 1
    
    def cond_nothing_said(self):
        lsds = last_speech_detected_seconds()
        if lsds != None:
            self.update_time_when_entered_listen()
        return abs(self.time_when_entered_listen - time.time()) > self.threshold_nothing_said
    
    def cond_nothing_gen(self):
        if self.time_when_entered_start_gen == None:
            self.update_time_when_entered_start_gen()
        return abs(self.time_when_entered_start_gen - time.time()) > self.threshold_nothing_gen

    def cond_T1_finished(self):
        return tools_running(['T1']) == ['False']

    def cond_T10_finished(self):
        # return tools_running(['T1', 'T10']) == ['False'] * 2
        return True # TODO T10 NOT_IMPLEMENTED

    def cond_T03_finished(self):
        return tools_running(['T0', 'T3']) == ['False', 'False']
    
    def cond_T45_finished(self):
        # return tools_running(['T4']) == ['False']
        return True # tools_running(['T4', 'T5']) == ['False', 'False'] # TODO NOT_IMPLEMENTED
    
    def cond_T068_finished(self):
        return tools_running(['T0', 'T6', 'T8']) == ['False'] * 3
    
    def cond_bye(self):
        # with open("data/live/action_selected.txt", "r", encoding="utf-8") as file:
        #     action_selected = file.read()
        # return action_selected == "dire au revoir"
        return False # TODO NOT_IMPLEMENTED
    
    def cond_else(self):
        return True
    
    def cond_one_sentence(self):
        self.update_sentences_to_say()
        return len(self.sentences_to_say) >= 1
    
    def cond_nothing_to_say(self):
        self.update_sentences_to_say()
        return len(self.sentences_to_say) == 0 and tools_running(['T0', 'T2']) == ['False'] * 2 and len(self.current_sentence_generated) == 0
    
    def cond_not_empty_text_gen(self):
        self.update_sentences_to_say()
        return len(self.sentences_to_say) > 0 or len(self.current_sentence_generated) > 0
    
#%% RUN =================================================================================================================
    
    def run(self):
        """Main loop of the state machine."""

        logging.info(f"Starting StateMachine with initial state {self.current_state}")

        self.current_state.on_enter()

        while True:
            self.update_next_state()
            if self.next_state != self.current_state:
                logging.info(f"Transition    {self.current_state}" + " "*(16 - len(str(self.current_state))) + f" -->    {self.next_state}")
                self.current_state.on_exit()
                self.current_state = self.next_state
                self.current_state.on_enter()
            time.sleep(0.1)

#%% MAIN ================================================================================================================
if __name__ == "__main__":
    from .utils import stop_tools
    
    logging.basicConfig(format='[%(levelname)s] - %(asctime)s - %(message)s', filename='StateMachine/log.txt', filemode='w')
    logging.getLogger().setLevel(logging.INFO)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger().addHandler(console)

    sm = StateMachine()
    clear_data_live_folder()
    play_sound_effect("start")
    try:
        sm.run()
    except KeyboardInterrupt:
        stop_tools(['T0', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11'])
    
    play_sound_effect("stop")

    time.sleep(1)
    send_command("sit", "Tools/T11_Gesture/fast_com/")