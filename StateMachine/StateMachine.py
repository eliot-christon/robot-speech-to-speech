from State import State
from utils import start_tools, stop_tools, last_speech_detected_seconds, text_transcribed, tools_running, generated_sentences, sleep_02
import logging
import time

class StateMachine:

    def __init__(self):
        self.states = {
            "WAIT"      : State(number=0, name="WAIT",      start_tools=['T6', 'T8'], stop_tools=['T7']),
            "CONV"      : State(number=1, name="CONV",      stop_tools=['T6', 'T8'], on_enter=(sleep_02,)),
            "LISTEN"    : State(number=2, name="LISTEN",    start_tools=['T1', 'T6', 'T7', 'T8'], on_exit=(self.edit_prompt,)),
            "START_GEN" : State(number=3, name="START_GEN", start_tools=['T2'], stop_tools=['T6', 'T7', 'T8']),
            "GEN"       : State(number=4, name="GEN",       on_exit =(self.write_text_to_say, self.update_sentences_said)),
            "TTS_AS"    : State(number=5, name="TTS_AS",    start_tools=['T3', 'T4']),
            "SAY_A"     : State(number=6, name="SAY_A",     start_tools=['T0']),
            "ACT_A"     : State(number=7, name="ACT_A",     start_tools=['T5']),
            "ACT_B"     : State(number=8, name="ACT_B",     start_tools=['T5']),
            "SAY_B"     : State(number=9, name="SAY_B",     start_tools=['T0']),
        }

        self.conditions = {
            "WAIT"      : {"CONV"       : self.cond_start},
            "CONV"      : {"LISTEN"     : self.cond_T68_finished},
            "LISTEN"    : {"START_GEN"  : self.cond_end_sentence,   "WAIT"      : self.cond_nothing_said},
            "START_GEN" : {"GEN"        : self.cond_true},
            "GEN"       : {"TTS_AS"     : self.cond_one_sentence,   "LISTEN"    : self.cond_nothing_to_say},
            "TTS_AS"    : {"SAY_A"      : self.cond_T03_finished,   "ACT_A"     : self.cond_T45_finished},
            "SAY_A"     : {"ACT_B"      : self.cond_T45_finished},
            "ACT_A"     : {"SAY_B"      : self.cond_T03_finished},
            "SAY_B"     : {"WAIT"       : self.cond_bye,            "GEN"       : self.cond_else},
            "ACT_B"     : {"WAIT"       : self.cond_bye,            "GEN"       : self.cond_else},
        }

        self.current_state = self.states["WAIT"]
        self.next_state = None

        # thresholds
        self.threshold_nothing_said = 6
        self.threshold_recently_said = 3
        self.threshold_end_sentence = 1.5

        # key words
        self.key_words = {
            "start" : ["bonjour", "salut", "hello", "hi", "coucou", "hey"],
            "bye"   : ["au revoir", "bye", "ciao", "à plus", "à bientôt", "à la prochaine", "bye bye", "goodbye", "good bye"],
        }

        self.sentences_said = []
        self.sentences_to_say = []
        self.current_sentence_generated = ""

        logging.info("StateMachine initialized")

#%% METHODS ===============================================================================================================

    def update_next_state(self):
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
        sentences, current_sentence_generated = generated_sentences()
        self.sentences_to_say = [sentence for sentence in sentences if sentence not in self.sentences_said]
        self.current_sentence_generated = current_sentence_generated
    
    def update_sentences_said(self):
        self.sentences_said += self.sentences_to_say
        self.sentences_to_say = []
    
    def edit_prompt(self):
        with open("data/live/text_transcribed.txt", "r", encoding="utf-8") as file:
            text = file.read()
        with open("data/live/prompt.txt", "w", encoding="utf-8") as file:
            file.write(text + " (réponds impérativement en français)")
    
    def empty_time_speech_detected(self):
        with open("data/live/time_speech_detected.txt", "w", encoding="utf-8") as file:
            file.write("")
    
#%% CONDITIONS ==========================================================================================================
        
    def cond_start(self):
        lsds = last_speech_detected_seconds()
        if lsds == None:
            return False
        return lsds - time.time() < self.threshold_recently_said and any(word in text_transcribed().lower() for word in self.key_words["start"])
    
    def cond_true(self):
        return True

    def cond_end_sentence(self):
        lsds = last_speech_detected_seconds()
        if lsds == None:
            return False
        return last_speech_detected_seconds() > self.threshold_end_sentence
    
    def cond_nothing_said(self):
        lsds = last_speech_detected_seconds()
        if lsds == None:
            return False
        return last_speech_detected_seconds() > self.threshold_nothing_said
    
    def cond_T03_finished(self):
        return tools_running(['T0', 'T3']) == ['False', 'False']
    
    def cond_T45_finished(self):
        return tools_running(['T4', 'T5']) == ['False', 'False']
    
    def cond_T68_finished(self):
        return tools_running(['T6', 'T8']) == ['False', 'False']
    
    def cond_bye(self):
        return False # TODO
    
    def cond_else(self):
        return True
    
    def cond_one_sentence(self):
        self.update_sentences_to_say()
        return len(self.sentences_to_say) >= 1
    
    def cond_nothing_to_say(self):
        self.update_sentences_to_say()
        return len(self.sentences_to_say) == 0 and not self.current_sentence_generated
    
#%% RUN =================================================================================================================
    
    def run(self):

        logging.info(f"Starting StateMachine with initial state {self.current_state}")

        self.current_state.on_enter()

        while True:
            self.update_next_state()
            if self.next_state != self.current_state:
                logging.info(f"Transition from {self.current_state} to {self.next_state}")
                self.current_state.on_exit()
                self.current_state = self.next_state
                self.current_state.on_enter()
            time.sleep(0.1)

#%% MAIN ================================================================================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sm = StateMachine()
    sm.run()