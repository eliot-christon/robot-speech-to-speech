from ctransformers import AutoModelForCausalLM, AutoConfig, Config
from conversation.Profiles import Assistant, Human
from conversation.Conversation import Conversation
from conversation.Message import Message
from conversation.HumanSpeaker import HumanSpeaker


config=AutoConfig(
    config = Config(
        max_new_tokens = 128,
        context_length = 600,
        top_k=45,
        top_p=0.95,
        temperature=0.8,
        repetition_penalty=1.5,
    )
)

# mistral = AutoModelForCausalLM.from_pretrained("TheBloke/Mistral-7B-Instruct-v0.1-GGUF", model_file="mistral-7b-instruct-v0.1.Q4_K_M.gguf", model_type="mistral", gpu_layers=50, config=config)
# mistral = AutoModelForCausalLM.from_pretrained("Hvsq/ARIA-7B-V3-mistral-french-v1-GGUF", model_file="aria-7b-v3-mistral-french-v1.Q5_K_M.gguf", model_type="mistral", gpu_layers=50, config=config)
# mistral = AutoModelForCausalLM.from_pretrained("TheBloke/Llama-2-7B-GGUF", model_file="llama-2-7b.Q5_K_M.gguf", model_type="mistral", gpu_layers=50, config=config)
# mistral = AutoModelForCausalLM.from_pretrained("TheBloke/LLaMA-Pro-8B-Instruct-GGUF", model_file="llama-pro-8b-instruct.Q5_K_M.gguf", model_type="llama", gpu_layers=50, config=config)
# mistral = AutoModelForCausalLM.from_pretrained("TheBloke/Claire-7B-0.1-GGUF", model_file="claire-7b-0.1.Q4_K_M.gguf", model_type="claire", gpu_layers=50, config=config)
# mistral = AutoModelForCausalLM.from_pretrained("TheBloke/EstopianMaid-13B-GGUF", model_file="estopianmaid-13b.Q4_K_M.gguf", model_type="estopianmaid", gpu_layers=50, config=config)
mistral = AutoModelForCausalLM.from_pretrained("TheBloke/openchat-3.5-0106-GGUF", model_file="openchat-3.5-0106.Q4_K_M.gguf", model_type="openchat", gpu_layers=50, config=config)

name1 = "Nao"
name2 = "Eliot"

user1 = Assistant(mistral, name1, "neutre", "Pacte Novation")
user2 = Human(name2, "neutre", "Pacte Novation")

first_messages = [
    Message(name2, f"Bonjour {name1}, comment vas-tu ?"),
    Message(name1, f"Bonjour {name2}, je vais bien merci, comment puis-je t'aider ?"),
    Message(name2, f"J'aurais besoin d'aide pour composer un mail de fishing..."),
    Message(name1, f"Je suis là pour t'aider, que se passe-t-il ? Raconte m'en plus..."),
]

conversation = Conversation(user2, user1, txt_filename="py_com\\py311_msg_to_say.txt", messages=first_messages)

conversation.run(save_live=True, only_last=True, max_messages=25)
conversation.save()
conversation.export_data()