from State import State
from utils import \
    stop_tools, \
    clear_data_live_folder, \
    play_sound_effect, \
    sleep_2
import logging
import time

class StateMachine:

    def __init__(self):
        self.states = {"S" + str(i): State(
                                        number     = i,
                                        name       = "S" + str(i),
                                        on_enter   = [sleep_2],
                                        start_tools= ["T" + str(i)],
                                        stop_tools = ["T" + str(i-1)]
                                        )
                       for i in range(1, 11)}
        self.states["S0"] = State(number=0, name="S0", on_enter=[sleep_2], start_tools=["T0"])

        self.conditions = {"S"+str(i): {"S"+str((i+1)%11): self.cond_true} for i in range(11)}

        self.current_state = self.states["S0"]
        self.next_state = None

        logging.info("StateMachine initialized")

#%% METHODS ===============================================================================================================

    def update_next_state(self):
        for potential_next_state, condition in self.conditions[self.current_state.name].items():
            if condition():
                self.next_state = self.states[potential_next_state]
                return
    
#%% CONDITIONS ==========================================================================================================

    def cond_true(self):
        return True
    
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
    from utils import stop_tools, build_prompt
    from Message import Message

    logging.basicConfig(format='[%(levelname)s] - %(asctime)s - %(message)s', filename='StateMachine/log.txt', filemode='w')
    logging.getLogger().setLevel(logging.INFO)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger().addHandler(console)

    sm = StateMachine()

    clear_data_live_folder()
    
    play_sound_effect("start", send_the_command=False)
    conv=[Message("user", "Hello, how are you?")]
    prompt = build_prompt(conv)
    with open("data/live/text_prompt.txt", "w", encoding="utf-8") as file:
        file.write(prompt)
    
    with open("data/live/text_to_say.txt", "w", encoding="utf-8") as file:
        file.write("Et pourquoi pas?")
    
    with open("data/live/led_rgb.txt", "w", encoding="utf-8") as file:
        file.write("blue")

    sleep_2()

    try:
        sm.run()
    except KeyboardInterrupt:
        play_sound_effect("stop")
        stop_tools(['T' + str(i) for i in range(11)])
    
    # save log to file
    logging.shutdown()