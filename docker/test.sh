#! /bin/bash

input="${1}"

if [ -z "$input" ]; then
    export log_level="INFO"
else
    export log_level="$input"
fi

export aws_default_region="us-west-2"

python3 ./main.py
