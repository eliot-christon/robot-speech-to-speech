#!/bin/bash

create_venv() {
    tool_path=$1
    python_version=$2
    if [ -d "$tool_path/venv" ]; then
        rm -rf "$tool_path/venv"
    fi
    cd "$tool_path"
    if [ "$python_version" == "python2.7" ]; then
        virtualenv -p $python_version venv
    else
        $python_version -m venv venv
    fi
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
    echo "success, $(basename $tool_path) venv created with $python_version"
}

# Define the tools and their corresponding Python versions
declare -A tools
tools=( ["Tools/T1_PersonRecognition"]="python3.11"
        ["Tools/T2_TextGeneration"]="python3.11"
        ["Tools/T3_TTS"]="python3.11"
        ["Tools/T4_ActionSelection"]="python3.11"
        ["Tools/T8_STT"]="python3.10"
        ["Tools/nao_env"]="python2.7" )

# Loop over the tools array and create virtual environments
for tool in "${!tools[@]}"; do
    create_venv "$tool" "${tools[$tool]}"
done
