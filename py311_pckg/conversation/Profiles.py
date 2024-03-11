__author__ = "Eliot CHRISTON"
__email__ = "eliot.christon@gmail.com"


# IMPORTS ================================================================================================================

from .Message import Message
from text_generation.prompt_template import get_prompt_template

from abc import ABC, abstractmethod
from ctransformers import AutoModelForCausalLM
import os
import ollama


#%% USER CLASSES ========================================================================================================

class User(ABC):
    def __init__(self, name:str="name", mood:str="neutre", work:str="Pacte Novation", role="user", save_filename:str=None):
        self.name = name
        self.mood = mood
        self.work = work
        self.role = role
        self.filename = save_filename
    
    def __str__(self):
        return "Utilisateur-" + self.name
    
    def __repr__(self):
        return "User(name={}, mood={}, work={}, role={})".format(self.name, self.mood, self.work, self.role)
    
    @abstractmethod
    def describe(self, for_other:bool=False):
        pass
    
    @abstractmethod
    def __call__(self, prompt:str) -> Message:
        pass

    @abstractmethod
    def get_modelname(self) -> str:
        pass

    def reset(self):
        self.save("")

    def save(self, message:str):
        # if the file does not exist, create it
        if self.filename is None:
            return
        if not os.path.exists(self.filename):
            os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        
        # write the message
        with open(self.filename, "w", encoding='utf-8') as f:
            f.write(message)



#%% HUMAN CLASSES ========================================================================================================
        

class HumanWriter(User):
    def __init__(self, name:str="Paolo", mood:str="neutre", work:str="Pacte Novation", role="user", save_filename:str=None):
        super().__init__(name, mood, work, role, save_filename)
    
    def describe(self, for_other:bool=False):
        return "Je m'appelle {}. Je travaille à {}. Je suis d'humeur {}.".format(self.name, self.work, self.mood)
    
    def __str__(self):
        return "Humain-" + self.name
    
    def __repr__(self):
        return "Human(name={}, mood={}, work={})".format(self.name, self.mood, self.work)
    
    def __call__(self, prompt:str) -> Message:
        response = input(Message(self.name, ""))
        if response.lower() in ["exit", "quit", "bye"]:
            raise KeyboardInterrupt
        message = Message(self.name, response)
        self.save(str(message))
        return message
    
    def get_modelname(self) -> str:
        return "Written_Model"



class HumanSpeaker(HumanWriter):
    def __init__(self, name: str = "Pierre", mood: str = "neutre", work: str = "Pacte Novation", role="user", save_filename:str=None, **kwargs):
        super().__init__(name, mood, work, role, save_filename)
        from stt.real_time_transcribe_wav import SpeechTranscriber
        self.transcriber = SpeechTranscriber(**kwargs)

    def describe(self, for_other: bool = False):
        return super().describe(for_other)

    def __str__(self):
        return super().__str__()

    def __repr__(self):
        return "HumanSpeaker(name={}, mood={}, work={})".format(self.name, self.mood, self.work)

    def write_listen(self, listen:bool):
        """ Write the conversation state to a file """
        with open("py_com\\py311_listen.txt", "w") as f:
            f.write("yes" if listen else "no")

    def __call__(self, prompt: str) -> Message:
        self.write_listen(True)
        response = self.transcriber.start_transcribing(stop_after_one_phrase=True)
        self.write_listen(False)
        message = Message(self.name, response)
        self.save(str(message))
        return message
    
    def get_modelname(self) -> str:
        return "Audio_Model"

    def reset(self):
        self.write_listen(False)
        self.save("")


#%% ASSISTANT CLASSES ========================================================================================================


class Assistant(User):
    def __init__(self, name:str="Nao", mood:str="neutre", work:str="Pacte Novation", role="user",  model:AutoModelForCausalLM=None, ollama_model_name='llama2', save_filename:str="py_com\\py311_msg_to_say.txt"):
        self.model = model
        self.ollama_model_name = ollama_model_name
        super().__init__(name, mood, work, role, save_filename)
        self.stop_char = get_prompt_template(self.get_modelname())["end"]

    def describe(self, for_other:bool=False):
        if for_other:
            return "Je m'appelle {}. Je travaille à {} . Je suis d'humeur {}.".format(self.name, self.work, self.mood)
        return "Tu es un robot assistant appelé {}. Tu travailles à {}. Tu es d'humeur {}. Tu dois absolument être aimable et courtois".format(self.name, self.work, self.mood)

    def __str__(self):
        return "Assistant-" + self.name
    
    def __repr__(self):
        return "Assistant(name={}, mood={}, work={})".format(self.name, self.mood, self.work)
    
    def __call__(self, prompt) -> Message:

        res = Message(self.name, "")

        if self.model:
            response = ""
            stop_char_found = False
            print(res, end="")
            for text in self.model(prompt, stream=True):
                if stop_char_found:
                    break
                print(text, end="", flush=True)
                response += text
                res.content = response
                self.save(str(res))
                for stop_char in self.stop_char:
                    if stop_char in response:
                        stop_char_found = True
                        break
            print()

        else: # ollama
            response = ""
            stream = ollama.generate(
                model=self.ollama_model_name,
                prompt=prompt,
                stream=True,
                options={
                    "top_k": 50,
                    "top_p": 0.95,
                    "temperature": 0.85,
                    "repeat_penalty": 1.9,
                    "repeat_last_n": 100,
                }
            )
            print(res, end=" ")
            for chunk in stream:
                print(chunk['response'], end='', flush=True)
                response += chunk['response']
                res.content = response
                self.save(str(res))
            print()
        
        response = response.replace("\n", "").replace("\n", "")
        for stop_char in self.stop_char:
            response = response.replace(stop_char, "")
        res.content = response
        self.save(str(res)+".")

        return res
    
    def get_modelname(self) -> str:
        if self.model:
            return self.model.model_path.replace("C:\\Users\\echriston\\.cache\\huggingface\\hub\\models--", "")
        return self.ollama_model_name