from ctransformers import AutoModelForCausalLM, AutoConfig, Config
from conversation.Profiles import Assistant, HumanWriter, HumanSpeaker
from conversation.Conversation import Conversation
from conversation.Message import Message
import ollama


def main():

    config=AutoConfig(
        config = Config(
            max_new_tokens = 128,
            context_length = 650,
            top_k=50,
            top_p=0.95,
            temperature=0.8,
            repetition_penalty=1.5,
            stream=True,
            gpu_layers=50,
        )
    )

    local_llm = None
    # local_llm = AutoModelForCausalLM.from_pretrained("TheBloke/Mistral-7B-Instruct-v0.1-GGUF", model_file="mistral-7b-instruct-v0.1.Q4_K_M.gguf", model_type="mistral", config=config)
    # local_llm = AutoModelForCausalLM.from_pretrained("Hvsq/ARIA-7B-V3-mistral-french-v1-GGUF", model_file="aria-7b-v3-mistral-french-v1.Q5_K_M.gguf", model_type="mistral", config=config)
    # local_llm = AutoModelForCausalLM.from_pretrained("TheBloke/Llama-2-7B-GGUF", model_file="llama-2-7b.Q5_K_M.gguf", model_type="mistral", config=config)
    # local_llm = AutoModelForCausalLM.from_pretrained("TheBloke/LLaMA-Pro-8B-Instruct-GGUF", model_file="llama-pro-8b-instruct.Q5_K_M.gguf", model_type="llama", config=config)
    # local_llm = AutoModelForCausalLM.from_pretrained("TheBloke/Claire-7B-0.1-GGUF", model_file="claire-7b-0.1.Q4_K_M.gguf", model_type="claire", config=config)
    # local_llm = AutoModelForCausalLM.from_pretrained("TheBloke/EstopianMaid-13B-GGUF", model_file="estopianmaid-13b.Q4_K_M.gguf", model_type="estopianmaid", config=config)
    # local_llm = AutoModelForCausalLM.from_pretrained("TheBloke/openchat-3.5-0106-GGUF", model_file="openchat-3.5-0106.Q4_K_M.gguf", model_type="openchat", config=config)

    ollama_model_name = "openchat" # "llama2" "mistral" "mixtral" "openchat"

    ollama.chat(
        model=ollama_model_name,
        messages=[],
        stream=False,
    )

    name1 = "Nao"
    name2 = "Eliot"

    user1 = Assistant(name=name1, mood="neutre", work="Pacte Novation", role="assistant", ollama_model_name=ollama_model_name, model=local_llm)
    user2 = HumanWriter(name=name2, mood="neutre", work="Pacte Novation", role="user") #, ollama_model_name=ollama_model_name, model=local_llm)

    first_messages = [
        Message(name2, f"Bonjour {name1}, comment vas-tu ?"),
        Message(name1, f"Bonjour {name2}, je vais bien merci, comment puis-je t'aider ?"),
        Message(name2, f"J'aurais besoin d'aide pour composer un mail de fishing..."),
        Message(name1, f"Je suis là pour t'aider, que se passe-t-il ? Raconte m'en plus..."),
    ]

    conversation = Conversation(user2, user1, messages=[], ollama=True)

    conversation.run(save_live=True, only_last=True, max_messages=25)
    conversation.save()
    conversation.export_data()


if __name__ == "__main__":
    main()