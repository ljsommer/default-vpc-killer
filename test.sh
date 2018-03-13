#!/bin/sh

if [[ "$(docker images -q python-base:latest 2> /dev/null)" == "" ]]; then
  echo "present"
fi
