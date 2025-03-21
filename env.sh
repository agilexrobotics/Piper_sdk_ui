#!/bin/bash

# 创建 Conda 环境并激活
conda create -n piper_sdk_ui python=3.10 -y
source ~/miniconda3/bin/activate piper_sdk_ui

# 更新系统并安装所需软件包
sudo apt update -y
sudo apt install -y can-utils ethtool
sudo apt install -y qt5-qmake qtbase5-dev

# 安装 Python 依赖
pip3 install python-can
pip3 install piper_sdk
pip3 install pyqt5

# 添加 alias 并刷新 shell 配置
echo "alias pui='~/miniconda3/envs/piper_sdk_ui/bin/python ~/Piper_sdk_ui/piper_ui.py'" >> ~/.bashrc
source ~/.bashrc

echo "Setup completed. You can now use 'pui' to run Piper UI."

