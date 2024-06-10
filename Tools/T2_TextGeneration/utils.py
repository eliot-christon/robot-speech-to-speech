from .prompt_template import TEMPLATE


def build_prompt(model_name: str, input_list: list[dict]) -> str:
    """Builds a prompt string from the given list of dictionaries, role and content pairs."""
    prompt_template = TEMPLATE[model_name]
    prompt = ''

    my_parts = msg_list_to_part_list(input_list)

    for part in my_parts:
        prompt += place_part_in_template(part, prompt_template)
    
    return prompt
            

def place_part_in_template(part: dict, template_input: str) -> str:
    """Places the given part in the given template and returns the resulting string."""
    # if role, delete {{ if .role }} and {{ end .role }} and replace {{ .role }} with content
    # else delete everything between {{ if .role }} and {{ end .role }}

    res_template = template_input[:]

    for role in ['system', 'user', 'assistant']:
        if role in part.keys():
            res_template = res_template.replace(f"{{{{ if .{role} }}}}", "").replace(f"{{{{ end .{role} }}}}", "")
            res_template = res_template.replace(f"{{{{ .{role} }}}}", part[role])
        else:
            start_tag = "{{ if ." + role + " }}"
            end_tag = "{{ end ." + role + " }}"
            start_index = res_template.find(start_tag)
            end_index = res_template.find(end_tag)
            if start_index != -1 and end_index != -1:
                res_template = res_template[:start_index] + res_template[end_index + len(end_tag):]

    return res_template


def msg_list_to_part_list(input_list:list[dict]) -> list[dict]:
    """
    input : list of dict {'role':str, 'content':str}
    output : list of parts
    parts being dict {'role':'content'}

    there are three roles : system, user, assistant.

    The rules are as follow :
    - break the list in parts before seeing any role other than assistant after an assistant.
    - in each part, sort the roles as follow : system (facultative), user, assistant
    - merge the contents of the consecutive same role
    - check the last part has no assistant message, raise error
    """

    part_list = []
    current_part = dict()
    last_role = None

    # 1. Break the list in parts before seeing any role other than assistant after an assistant.
    for i, message in enumerate(input_list):
        role = message['role']
        if role != 'assistant' and last_role == 'assistant':
            part_list.append(current_part)
            current_part = dict()
        
        if role in current_part.keys():
            current_part[role] += ' ' + message['content']
        else:
            current_part[role] = message['content']
        last_role = role

    part_list.append(current_part)

    # 4. Check the last part has no assistant message, raise error
    if 'assistant' in part_list[-1].keys():
        raise ValueError("The last part has an assistant message.")

    return part_list


if __name__ == "__main__":

    # Test the function
    input_list = [
        {'role': 'user', 'content': 'Message 1'},
        {'role': 'assistant', 'content': 'Assistant message 1'},
        {'role': 'system', 'content': 'System message 1'},
        {'role': 'user', 'content': 'Message 2'},
        {'role': 'user', 'content': 'Message 2b'},
        {'role': 'system', 'content': 'System message 2'},
        {'role': 'assistant', 'content': 'Assistant message 2'},
        {'role': 'assistant', 'content': 'Assistant message 3'},
        {'role': 'user', 'content': 'Message 3'},
        {'role': 'assistant', 'content': 'Assistant message 4'},
        {'role': 'user', 'content': 'Message 4'},
    ]

    prompt = build_prompt('mistral', input_list)

    print(prompt)