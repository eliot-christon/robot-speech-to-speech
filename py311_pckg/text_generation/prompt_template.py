prompt_templates = {
    "TheBloke--Mistral-7B-Instruct-v0.1-GGUF" : {"start":"<s>[INST] ", "mid":" [/INST]", "end":"</s>"},
    "Hvsq--ARIA-7B-V3-mistral-french-v1-GGUF" : {"start":"<s>[INST] ", "mid":" [/INST]", "end":"</s>"},
    "TheBloke--LlaMA-Pro-8B-Instruct-GGUF" : {"start":"<|user|>\n", "mid":"\n<|assistant|>", "end":"</s>"},
    "TheBloke--Llama-2-7B-GGUF" : {"start":"", "mid":"", "end":"</s>"},
}

def get_prompt_template(model_name:str) -> dict:
    # check if key in model_name
    for key in prompt_templates.keys():
        if key in model_name:
            return prompt_templates[key]
    raise Warning("Model name not found in prompt_templates")
    return {"start":"<s>[INST] ", "mid":" [/INST]", "end":"</s>"}