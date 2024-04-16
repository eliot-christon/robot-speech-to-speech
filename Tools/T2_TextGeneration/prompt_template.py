prompt = {
    1 : "[INST] {{ if .system }}<<SYS>>{{ .system }}<</SYS>>\n\n{{ end .system }}{{ .user }} [/INST]\n{{ if .assistant }}{{ .assistant }}\n{{ end .assistant }}",
    2 : "<start_of_turn>user\n{{ if .system }}{{ .system }} {{ end .system }}{{ .user }}<end_of_turn>\n<start_of_turn>model\n{{ if .assistant }}{{ .assistant }}<end_of_turn>\n{{ end .assistant }}",
    3 : "{{ if .system }}<|im_start|>system\n{{ .system }}<|im_end|>{{ end .system }}<|im_start|>user\n{{ .user }}<|im_end|>\n<|im_start|>assistant\n{{ if .assistant }}{{ .assistant }}<|im_end|>\n{{ end .assistant }}",
    4 : "{{ .system }}<|end_of_turn|>GPT4 Correct User: {{ .user }}<|end_of_turn|>GPT4 Correct Assistant: {{ if .assistant }}{{ .assistant }}{{ end .assistant }}",
    5 : "{{ if .system }}<<SYS>>{{ .system }}<</SYS>> \n\n{{ end .system }}<|UTILISATEUR|>: {{ .user }}\n<|ASSISTANT|>: {{ if .assistant }}{{ .assistant }}\n{{ end .assistant }}",
    6 : "{{ if .system }}<<SYS>>{{ .system }}<</SYS>>\n\n{{ end .system }}User: {{ .user }}\nAssistant: {{ if .assistant }}{{ .assistant }}\n{{ end .assistant }}",
}


TEMPLATE = {
    "llama2"            : prompt[1],
    "mistral"           : prompt[1],
    "vigostral"         : prompt[1],
    "gemma"             : prompt[2],
    "qwen:4b"           : prompt[3],
    "qwen:7b"           : prompt[3],
    "openhermes"        : prompt[3],
    "openchat"          : prompt[4],
    "vigogne"           : prompt[4],
    "openbuddy-mistral" : prompt[6],
}
