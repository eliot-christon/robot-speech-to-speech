# robot-speech-to-speech 🤖🗣️
Pacte Novation Internship Project - 2024

## State Machine 0️⃣ ➡️ 1️⃣

<div style="text-align:center"><img src=SM_example.png/></div>

The State Machine is a system that allows the assistant to interact with the user. It is composed of several states, each state corresponds to a step in the interaction. The assistant can move from one state to another depending on diverse conditions. The State Machine is a powerful tool that allows a great flexibility and modularity in the interaction. [Wikipedia link for more details](https://en.wikipedia.org/wiki/Finite-state_machine)

### How does it work? 🤔
Each state machine is a new class using several instances of the [```State.py```](State.py) class and defining explicitly the transitions between the states. The transitions are defined by the conditions that must be met to move from one state to another. Each state has the ability to start, stop, and execute specific actions referenced as Tools. They can also run specific functions to adapt the interaction to the user's needs.

### How to use it? 🛠️
To use it, simply run one of the ```SM_*.py``` files after having started the processes (see the [Tools folder](../Tools/)). The assistant will then interact with you according to the state machine you have chosen.

### Parameters 📚
The State Machine has several parameters that can be modified to adapt the interaction to your needs. These parameters are defined in a ```.yaml``` file with the same name as the state machine. The parameters are directly related to the Tools used by the assistant.