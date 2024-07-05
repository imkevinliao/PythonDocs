#!/bin/bash

if command -v python3 &>/dev/null; then
    :
else
    echo "installing Python3"
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
    else
        echo "Error: Unsupported OS"
        exit 1
    fi
    case $OS in
        "Ubuntu" | "Debian GNU/Linux")
            sudo apt update
            sudo apt install python3 -y
            ;;
        "CentOS Linux" | "Red Hat Enterprise Linux")
            sudo yum update
            sudo yum install python3 -y
            ;;
        *)
            echo "Error: Unsupported OS"
            exit 1
            ;;
    esac
fi

# 执行python脚本
curl -sSL https://raw.githubusercontent.com/imkevinliao/[project name]/[project branch]/[python script] | python3

# https://raw.githubusercontent.com/imkevinliao/python_docs/master/install.sh
