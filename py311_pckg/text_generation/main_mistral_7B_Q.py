
if __name__ == "__main__":

    from ctransformers import AutoModelForCausalLM
    from conversation.Profiles import User, HumanWriter, Assistant, UserBot
    from conversation.Conversation import Conversation

    # mistral = AutoModelForCausalLM.from_pretrained("TheBloke/Mistral-7B-Instruct-v0.1-GGUF", model_file="mistral-7b-instruct-v0.1.Q5_K_M.gguf", model_type="mistral", gpu_layers=50)
    mistral = AutoModelForCausalLM.from_pretrained("Hvsq/ARIA-7B-V3-mistral-french-v1-GGUF", model_file="aria-7b-v3-mistral-french-v1.Q5_K_M.gguf", model_type="mistral", gpu_layers=50)

    user1 = Assistant(mistral, "Nao", "triste", "Pacte Novation")
    user2 = HumanWriter("Paolo", "joyeux", "sans emploi")

    conversation = Conversation(user2, user1)

    conversation.run()

    conversation.save()