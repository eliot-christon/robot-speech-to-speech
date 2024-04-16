import time 

class Message:
    def __init__(self, role:str, content:str, timestamp:float=None):
        self.timestamp = timestamp
        if self.timestamp is None:
            self.timestamp = time.time()
        self.role = role
        self.content = content.replace("\n", "/n")

    def __str__(self):
        return f"{time.strftime('%H:%M:%S', time.localtime(self.timestamp))} {self.role}: {self.content}"
    
    def __repr__(self):
        return f"Message(role={self.role}, content={self.content}, timestamp={self.timestamp})"

    def to_dict(self) -> dict:
        return {"timestamp": self.timestamp, "role": self.role, "content": self.content}
    
    def pretty_str(self) -> str:
        return f"{self.role}: {self.content}"

    @classmethod
    def from_dict(cls, data:dict):
        if "timestamp" not in data.keys():
            return cls(data["user"], data["content"])
        return cls(data["user"], data["content"], data["timestamp"])

    def __eq__(self, other):
        if not isinstance(other, Message):      return False
        if self.role != other.role:             return False
        if self.content != other.content:       return False
        if self.timestamp != other.timestamp:   return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.role, self.content, self.timestamp))
    
    def __len__(self):
        return len(self.content)
    
    def nb_words(self):
        return len(self.content.split())