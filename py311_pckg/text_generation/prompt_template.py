prompt_templates = {
    "TheBloke--Mistral-7B-Instruct-v0.1-GGUF" : {"start":"<s>[INST] ", "mid":" [/INST]", "end":["</s>"]},
    "mistral" : {"start":"<s>[INST] ", "mid":" [/INST]", "end":["</s>"]},
    "Hvsq--ARIA-7B-V3-mistral-french-v1-GGUF" : {"start":"<s>[INST] ", "mid":" [/INST]", "end":["</s>"]},
    "TheBloke--LlaMA-Pro-8B-Instruct-GGUF" : {"start":"<|user|>\n", "mid":"\n<|assistant|>", "end":["</s>"]},
    "TheBloke--Llama-2-7B-GGUF" : {"start":"", "mid":"", "end":["</s>"]},
    "llama2" : {"start":"", "mid":"", "end":["</s>"]},
    "TheBloke--EstopianMaid-13B-GGUF" : {"start":"### Instruction:\n", "mid":"\n\n### Response:\n", "end":["</s>", "###"]},
    "TheBloke--openchat-3.5-0106-GGUF" : {"start":"GPT4 Correct User: ", "mid":"<|end_of_turn|>GPT4 Correct Assistant: ", "end":["<|end_of_turn|>", "</s>", "<|end", "<||", "< |end", "< | end"]},
}

def get_prompt_template(model_name:str) -> dict:
    # check if key in model_name
    for key in prompt_templates.keys():
        if key in model_name:
            return prompt_templates[key]
    return {"start":"", "mid":"", "end":["</s>"]}
