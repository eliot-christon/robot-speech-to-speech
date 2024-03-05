import time 

class Message:
    def __init__(self, username:str, content:str, timestamp:float=time.time()):
        self.timestamp = timestamp
        self.username = username
        self.content = content.replace("\n", "")

    def __str__(self):
        return f"{time.strftime('%H:%M:%S', time.localtime(self.timestamp))} {self.username}: {self.content}"
    
    def __repr__(self):
        return f"Message(username={self.username}, content={self.content}, timestamp={self.timestamp})"

    def to_dict(self) -> dict:
        return {"timestamp": self.timestamp, "username": self.username, "content": self.content}
    
    def pretty_str(self) -> str:
        return f"{self.username}: {self.content}"

    @classmethod
    def from_dict(cls, data:dict):
        if "timestamp" not in data.keys():
            return cls(data["user"], data["content"])
        return cls(data["user"], data["content"], data["timestamp"])

    def __eq__(self, other):
        if not isinstance(other, Message):      return False
        if self.username != other.username:             return False
        if self.content != other.content:       return False
        if self.timestamp != other.timestamp:   return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.username, self.content, self.timestamp))
    
    def __len__(self):
        return len(self.content)
    
    def nb_words(self):
        return len(self.content.split())