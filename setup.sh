#!/bin/bash

# Function to print 5 blank lines
print_blank_lines() {
    for _ in {1..5}; do
        echo ""
    done
}

create_venv() {
    tool_path=$1
    python_version=$2

    # Print blank lines for readability
    print_blank_lines

    # Check if the specified Python version is installed
    if ! command -v $python_version &> /dev/null; then
        echo "Error: $python_version is not installed or not in PATH."
        return 1
    fi

    # Install virtualenv if it's not installed
    if [ "$python_version" == "python2.7" ] && ! command -v virtualenv &> /dev/null; then
        echo "Installing virtualenv for Python 2.7..."
        $python_version -m pip install virtualenv
        if [ $? -ne 0 ]; then
            echo "Error: Failed to install virtualenv for $python_version."
            return 1
        fi
    fi

    # Remove existing venv directory if present
    if [ -d "$tool_path/venv" ]; then
        rm -rf "$tool_path/venv"
    fi

    # Create a virtual environment for the tool
    if [ "$python_version" == "python2.7" ]; then
        $python_version -m virtualenv "$tool_path/venv"

    else
        $python_version -m venv --without-pip "$tool_path/venv"
    fi

    # Check if the virtual environment was created successfully
    if [ ! -f "$tool_path/venv/bin/activate" ]; then
        echo "Error: Failed to create virtual environment for $tool_path with $python_version."
        return 1
    fi

    # Activate the virtual environment
    source "$tool_path/venv/bin/activate"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to activate virtual environment for $tool_path."
        return 1
    fi

    # Install pip if not present and upgrade pip, setuptools, and wheel
    if [ "$python_version" != "python2.7" ]; then
        $tool_path/venv/bin/python -m ensurepip --upgrade
        if [ $? -ne 0 ]; then
            echo "ensurepip failed, trying manual installation of pip..."
            curl https://bootstrap.pypa.io/get-pip.py | $tool_path/venv/bin/python
            if [ $? -ne 0 ]; then
                echo "Error: Failed to manually install pip for $tool_path."
                deactivate
                return 1
            fi
        fi
    fi

    # Upgrade pip, setuptools, and wheel
    $tool_path/venv/bin/pip install --upgrade pip setuptools wheel
    if [ $? -ne 0 ]; then
        echo "Error: Failed to upgrade pip, setuptools, and wheel for $tool_path."
        deactivate
        return 1
    fi

    # Install the requirements for the tool
    if [ "$python_version" != "python2.7" ]; then
        pip install -r "$tool_path/requirements.txt"
        if [ $? -ne 0 ]; then
            echo "Error: Failed to install requirements for $tool_path."
            deactivate
            return 1
        fi
    else # Python 2.7
        $python_version -m pip install -r "$tool_path/requirements.txt"
    fi

    deactivate
    echo "Success: $(basename $tool_path) venv created with $python_version"
}

create_fast_com_files() {
    # for all the directories beginning with Tools/T* create the fast_com_files directory : tool_path/fast_com/command.txt and tool_path/fast_com/status.txt

    tool_dirs=$(find Tools -type d -name "T*" -print)

    for tool_path in $tool_dirs; do
        mkdir -p "$tool_path/fast_com"
        touch "$tool_path/fast_com/command.txt"
        touch "$tool_path/fast_com/status.txt"
    done
}


echo "write NAO IP adress here" > Tools/nao_ip.txt

# Define the tools and their corresponding Python versions
declare -A tools
tools=( ["Tools/T1_PersonRecognition"]="python3.11"
        ["Tools/T2_TextGeneration"]="python3.11"
        ["Tools/T3_TTS"]="python3.10"
        ["Tools/T4_ActionSelection"]="python3.11"
        ["Tools/T8_STT"]="python3.11"
        ["Tools/nao_env"]="python2.7" )

# Loop over the tools array and create virtual environments
for tool in "${!tools[@]}"; do
    create_venv "$tool" "${tools[$tool]}"
done

# Create fast_com_files for each tool
create_fast_com_files
echo "Setup completed successfully."