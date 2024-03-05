from ctransformers import AutoModelForCausalLM
from conversation.Profiles import Assistant, Human
from conversation.Conversation import Conversation
from conversation.HumanSpeaker import HumanSpeaker

mistral = AutoModelForCausalLM.from_pretrained("TheBloke/Mistral-7B-Instruct-v0.1-GGUF", model_file="mistral-7b-instruct-v0.1.Q4_K_M.gguf", model_type="mistral", gpu_layers=50)
# mistral = AutoModelForCausalLM.from_pretrained("Hvsq/ARIA-7B-V3-mistral-french-v1-GGUF", model_file="aria-7b-v3-mistral-french-v1.Q5_K_M.gguf", model_type="mistral", gpu_layers=50)
# mistral = AutoModelForCausalLM.from_pretrained("TheBloke/Llama-2-7B-GGUF", model_file="llama-2-7b.Q5_K_M.gguf", model_type="mistral", gpu_layers=50)
# mistral = AutoModelForCausalLM.from_pretrained("TheBloke/LLaMA-Pro-8B-Instruct-GGUF", model_file="llama-pro-8b-instruct.Q5_K_M.gguf", model_type="llama", gpu_layers=50)
# mistral = AutoModelForCausalLM.from_pretrained("TheBloke/Claire-7B-0.1-GGUF", model_file="claire-7b-0.1.Q4_K_M.gguf", model_type="claire", gpu_layers=50)


user1 = Assistant(mistral, "Nao", "neutre", "Pacte Novation")
user2 = HumanSpeaker("Eliot", "neutre", "Pacte Novation")

conversation = Conversation(user2, user1, txt_filename="py_com\\py311_msg_to_say.txt")

conversation.run(save_live=True, only_last=True, max_messages=25)
conversation.save()
conversation.export_data()