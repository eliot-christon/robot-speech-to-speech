from .utils import start_tools, stop_tools

class State:
    """Base class for all states"""

    def __init__(self, number:int, name:str, on_enter:tuple=(), on_exit:tuple=(), start_tools:list=[], stop_tools:list=[]):
        self.number = number
        self.name = name
        self.on_enter_functions = on_enter
        self.on_exit_functions = on_exit
        self.start_tools = start_tools
        self.stop_tools = stop_tools
    
    def on_enter(self):
        for function in self.on_enter_functions:
            if function is not None:
                function()
        start_tools(self.start_tools)
        stop_tools(self.stop_tools)
    
    def on_exit(self):
        for function in self.on_exit_functions:
            function()

    def __repr__(self):
        """Leaves room for debugging."""
        return self.__str__()

    def __str__(self):
        """Leaves room for debugging."""
        return f"S{self.number} - {self.name}"