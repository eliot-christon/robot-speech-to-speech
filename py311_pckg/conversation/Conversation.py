from .Profiles import User, HumanWriter, Assistant
from .Message import Message
from typing import List
import time
from text_generation.prompt_template import get_prompt_template


class Conversation:
    def __init__(self, user1:User, user2:User, messages:List[Message]=[], txt_filename:str=None, csv_filename:str=None):
        self.user1 = user1
        self.user2 = user2
        self.current_user = user1
        self.filename = txt_filename
        self.csv_filename = csv_filename
        if self.filename is None:
            self.filename = "py311_pckg\\conversation\\historique\\conversation-" + time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) + ".txt"
        if self.csv_filename is None:
            self.csv_filename = "py311_pckg\\conversation\\historique\\conversation-" + time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) + ".csv"

        self.messages = [Message("","")]
        self.save(only_last=True)  # create the empty file
        self.messages = messages
        self.initial_messages = len(self.messages)

        self.data = {
            "modelname": [],
            "timestamp": [],
            "username": [],
            "usertype": [],
            "messages_content": [],
            "prompt_latency": [None]*len(self.messages),
            "response_latency": [None]*len(self.messages),
            "save_latency": [None]*len(self.messages),
        }

    def __str__(self):
        return "Conversation between {} and {}".format(self.user1, self.user2) + "\n" + "\n".join([str(message) for message in self.messages])
    
    def __repr__(self):
        return "Conversation(user1={}, user2={}, messages={})".format(self.user1, self.user2, self.messages)
    
    def run(self, save_live:bool=False, only_last:bool=False, max_messages:int=100):
        while True:
            try:
                t1 = time.time()
                prompt = self.build_prompt(self.current_user)

                # print the prompt
                # print("\n" + "="*50)
                # print(prompt)
                # print("="*50 + "\n\n")

                t2 = time.time()
                response = self.current_user(prompt)
                t3 = time.time()
                self.messages.append(Message(self.current_user.name + "", response.content, time.time()))
                self.current_user = self.other_user(self.current_user)
                t4 = time.time()

                if save_live:
                    self.save(only_last=only_last)

                self.data["prompt_latency"].append(t2 - t1)
                self.data["response_latency"].append(t3 - t2)
                self.data["save_latency"].append(t4 - t3)

                if len(self.messages) >= max_messages:
                    time.sleep(1)
                    break

            except KeyboardInterrupt:
                self.user1.reset()
                self.user2.reset()
                break
        print(self)

    def other_user(self, user:User) -> User:
        if user == self.user1:
            return self.user2
        return self.user1

    def build_prompt(self, current_user:User, max_words:int=150) -> str:

        if isinstance(current_user, HumanWriter):
            return ""
        
        # initialisation
        word_count = 0
        context = ""

        # get prompt template
        prompt_template = get_prompt_template(current_user.get_modelname())
        start_prompt = prompt_template["start"]
        mid_prompt = prompt_template["mid"]
        end_prompt = prompt_template["end"][0]

        for message in self.messages[::-1]:
            word_count += message.nb_words()
            if word_count > max_words:
                break
            if message.username == current_user.name:
                context = message.content + end_prompt + "\n" + context
            else:
                if message == self.messages[-1]:
                    context = start_prompt + message.content  + " (fais des phrases courtes, réponds-moi en une phrase ou deux en français)" + mid_prompt + "\n" + context
                else:
                    context = start_prompt + message.content + mid_prompt + "\n" + context

        context = start_prompt + current_user.describe(for_other=False) + " " + self.other_user(current_user).describe(for_other=True) + mid_prompt + context
        context = context.replace(mid_prompt+start_prompt, "")
        return context
    
    def save(self, only_last:bool=False):
        import os
        if not os.path.exists(os.path.dirname(self.filename)):
            os.makedirs(os.path.dirname(self.filename))
        with open(self.filename, "w", encoding='utf-8') as file:
            if not only_last:
                file.write(str(self))
                file.write("\n\n=====================CONTEXTS=====================\n\n")
                file.write(self.build_prompt(self.current_user))
                file.write("\n\n")
                file.write(self.build_prompt(self.other_user(self.current_user)))
            else:
                file.write(str(self.messages[-1]))

    def build_data(self):
        dict_user_type = {
            self.user1.name: self.user1.__class__.__name__,
            self.user2.name: self.user2.__class__.__name__,
        }

        dict_user_modelname = {
            self.user1.name: self.user1.get_modelname(),
            self.user2.name: self.user2.get_modelname(),
        }

        for message in self.messages:
            self.data["modelname"].append(dict_user_modelname[message.username])
            self.data["timestamp"].append(message.timestamp)
            self.data["username"].append(message.username)
            self.data["usertype"].append(dict_user_type[message.username])
            self.data["messages_content"].append(message.content)


    def export_data(self):

        self.build_data()

        for key in self.data.keys():
            print(key, len(self.data[key]))
            if len(self.data[key]) != len(self.messages):
                print(self.data[key])

        import pandas as pd

        self.data

        df = pd.DataFrame(self.data)
        df.to_csv(self.csv_filename, index=False)

        return df
    