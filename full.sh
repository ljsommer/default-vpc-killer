#! /bin/bash

input="${1}"

if [ -z "$input" ]; then
    log_level="INFO"
else
    log_level="$input"
fi

aws_default_region="us-west-2"

container_aws_dir="/root/.aws/"
container_ssh_dir="/root/.ssh/"

local_aws_dir="${HOME}/.aws/"
local_ssh_dir="${HOME}/.ssh/"

container_name="default-vpc-killer"
image_name="default-vpc-killer"

echo "Building Docker image: $image_name"
docker build -t $image_name ./docker

docker run -i -t --rm \
    --name $image_name \
    -e "AWS_DEFAULT_REGION=$aws_default_region" \
    -e "log_level=$log_level" \
    -v $local_aws_dir:$container_aws_dir \
    -v $local_ssh_dir:$container_ssh_dir \
    $image_name