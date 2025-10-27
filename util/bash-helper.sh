#!/bin/bash

# Copyright (C) 2024-2025 Burak Günaydin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

error() {
    local error_message=$1
    echo 
    echo -e "\033[31mERROR - $error_message \033[0m" 
    echo 
}

exit_error() {
    local error_message=$1
    echo 
    echo -e "\033[35mFATAL EXIT ERROR - $error_message \033[0m"
    echo 
    exit 1 
}

# Generic implemented trap registration
implemented_trap() {
    local trap_function=$1

    # Register trap for SIGINT
    trap '
        echo
        echo
        echo -e "\033[35mIMPLEMENTED TRAP ERROR - Script interrupted.\033[0m"
        echo

        if declare -f '"$trap_function"' > /dev/null; then
            '"$trap_function"'
        else
            echo -e "\033[31mERROR - Function '"'$trap_function'"' not found!\033[0m"
        fi
        exit 1
    ' SIGINT
}

hint() {
    local hint_message=$1
    echo -e "\033[96mHINT - $hint_message \033[0m" 
}

prompt() {
    local __resultvar=$1
    local prompt_message=$2
    local options=$3
    local default_value=$4

    echo ""
    if [ -n "$options" ]; then
        prompt_message="$prompt_message [$options]"
    fi

    echo -e "\033[92m$prompt_message\033[0m"

    if [ -z "$default_value" ]; then
        echo -ne "> "
    else
        echo -ne "\033[90m(Or press ENTER to accept default value ['$default_value'])\033[0m:\n> "
    fi

    read input_value

    if [ -z "$input_value" ]; then
        input_value=$default_value
    fi

    # Validate against options if provided
    if [ -n "$options" ]; then
        IFS='/' read -ra opt_array <<< "$options"
        local valid=false
        for opt in "${opt_array[@]}"; do
            if [ "$input_value" == "$opt" ]; then
                valid=true
                break
            fi
        done
        if [ "$valid" = false ]; then
            exit_error "Invalid option: '$input_value'"
        fi
    fi

    echo ""
    printf -v "$__resultvar" '%s' "$input_value"
}

prepare_env() {
    set -e
}

prepare_sudo_env() {
    set -e
    sudo -v >/dev/null 2>&1
}

prompt_for_env_variable() {
    local env_path=$1
    local prompt_message=$2
    local var_name=$3
    local default_value=$4

    echo -e "\033[92m$prompt_message\033[0m" 
    read -p "(Or press ENTER to accept default value ['$default_value']): " input_value 
    if [ -z "$input_value" ]; then
        input_value=$default_value 
    fi
    write_env_variable "$env_path" $var_name $input_value 
}

prompt_for_env_path() {
    local env_path=$1
    local prompt_message=$2
    local var_name=$3
    local default_value=$4
    
    local default_prompt_message="Please provide a path for the $prompt_message"

    echo -e "\033[92m$default_prompt_message\033[0m" 
    read -p "(Or press ENTER to accept default path ['$default_value']): " input_value 
    if [ -z "$input_value" ]; then
        input_value=$default_value 
    fi
    write_env_variable "$env_path" $var_name $input_value 
}

warn() {
    local warn_message=$1
    echo -e "\033[93mWARNING - $warn_message \033[0m" 
}

write_env_variable() {
    local env_path=$1
    local variable_name=$2
    local variable_value=$3
    if grep -q "^$variable_name=" "$env_path"; then
        sed -i "/^$variable_name=/d" "$env_path" 
    fi
    echo "$variable_name=$variable_value" >> "$env_path" 
    . "$env_path" 
}