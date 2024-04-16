from State import State
from utils import \
    tools_running, \
    stop_tools, \
    get_clean_generated_sentences, \
    clear_data_live_folder, \
    clean_text, \
    load_yaml, \
    build_prompt
from Message import Message
import logging
import time

class StateMachine:

    def __init__(self):
        self.states = {
            "WAIT_R"    : State(number=0, name="WAIT_R",
                                stop_tools=['T2'],
                                on_exit=(self.add_user_input_to_conversation,)),
            "BUILD"     : State(number=1, name="BUILD",
                                start_tools=['T10'],
                                on_exit=(self.add_documents_to_conversation, self.edit_prompt)),
            "GEN"       : State(number=2, name="GEN",
                                start_tools=['T2'],
                                on_exit=(self.add_assistant_output_to_conversation,)),
        }

        self.conditions = {
            "WAIT_R"    : {"BUILD"      : self.cond_input_file_change},
            "BUILD"     : {"GEN"        : self.cond_T10_finished},
            "GEN"       : {"WAIT_R"     : self.cond_T2_finished},
        }

        self.current_state = self.states["WAIT_R"]
        self.next_state = None
        self.last_input = ""

        self.params = load_yaml("StateMachine/SM_textual_parameters.yaml")

        self.conversation = [Message(role="system", content=\
"""Vous êtes un assistant utile qui répond aux questions des utilisateurs sur la base de plusieurs extraits de documents qui vous sont donnés.
Votre réponse doit être courte et pertinente. 
Répondez "Sans objet" si le texte n'est pas pertinent.
""")]

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

    def add_user_input_to_conversation(self):
        with open("data/live/text_transcribed.txt", "r", encoding="utf-8") as file:
            text = file.read()
        self.conversation.append(Message(role="user", content=text))
    
    def add_assistant_output_to_conversation(self):
        with open("data/live/text_generated.txt", "r", encoding="utf-8") as file:
            text = file.read()
        self.conversation.append(Message(role="assistant", content=text))

    def add_documents_to_conversation(self):
        with open("data/live/documents_context.txt", "r", encoding="utf-8") as file:
            text = file.read()
        self.conversation.append(Message(role="system", content=text))

    def edit_prompt(self):
        text = build_prompt(self.conversation)
        with open("data/live/text_prompt.txt", "w", encoding="utf-8") as file:
            file.write(text)
    
#%% CONDITIONS ==========================================================================================================

    def cond_else(self):
        return True

    def cond_input_file_change(self):
        with open("data/live/text_transcribed.txt", "r", encoding="utf-8") as file:
            current_input = file.read()
        if current_input != self.last_input:
            self.last_input = current_input
            return True
        return False

    def cond_T10_finished(self):
        return tools_running(['T10']) == ['False']

    def cond_T2_finished(self):
        return tools_running(['T2']) == ['False']
    
#%% RUN =================================================================================================================
    
    def run(self):

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
    from utils import stop_tools
    logging.basicConfig(format='[%(levelname)s] - %(asctime)s - %(message)s')
    logging.getLogger().setLevel(logging.INFO)
    sm = StateMachine()
    clear_data_live_folder()
    try:
        sm.run()
    except KeyboardInterrupt:
        stop_tools(['T2', 'T10'])