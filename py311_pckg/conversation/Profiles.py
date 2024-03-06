from .Message import Message
from text_generation.prompt_template import get_prompt_template

from abc import ABC, abstractmethod
from ctransformers import AutoModelForCausalLM


class User(ABC):
    def __init__(self, name:str="name", mood:str="neutre", work:str="Pacte Novation"):
        self.name = name
        self.mood = mood
        self.work = work
    
    def __str__(self):
        return "Utilisateur-" + self.name
    
    def __repr__(self):
        return "User(name={}, mood={}, work={})".format(self.name, self.mood, self.work)
    
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
        pass
        

class Human(User):
    def __init__(self, name:str="Paolo", mood:str="neutre", work:str="Pacte Novation"):
        super().__init__(name, mood, work)
    
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
        return Message(self.name, response)
    
    def get_modelname(self) -> str:
        return "Written_Model"


class Assistant(User):
    def __init__(self, model:AutoModelForCausalLM, name:str="Nao", mood:str="neutre", work:str="Pacte Novation"):
        self.model = model
        super().__init__(name, mood, work)
        self.stop_char = get_prompt_template(self.get_modelname())["end"]

    def describe(self, for_other:bool=False):
        if for_other:
            return "Je m'appelle {}. Je travaille à {} . Je suis d'humeur {}.".format(self.name, self.work, self.mood)
        return "Tu es un robot assistant appelé {}. Tu travailles à {}. Tu es d'humeur {}. Tu dois absolument être aimable et courtois".format(self.name, self.work, self.mood)

    def __str__(self):
        return "Assistant-" + self.name
    
    def __repr__(self):
        return "Assistant(name={}, mood={}, work={})".format(self.name, self.mood, self.work)
    
    def __call__(self, prompt:str) -> Message:
        # response to cuda
        response = self.model(
            prompt=prompt,
            max_new_tokens=128,
            top_k=50,
            top_p=0.95,
            temperature=0.8,
            repetition_penalty=1.5,
            stop=self.stop_char,
            )
        response = response.replace("\n", "").replace("\n", "")
        for stop_char in self.stop_char:
            response = response.replace(stop_char, "")
        res = Message(self.name, response)
        print(res)
        return res
    
    def get_modelname(self) -> str:
        return self.model.model_path.replace("C:\\Users\\echriston\\.cache\\huggingface\\hub\\models--", "")