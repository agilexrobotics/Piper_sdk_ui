[中文](README.MD)

|Ubuntu |STATE|
|---|---|
|![ubuntu18.04](https://img.shields.io/badge/Ubuntu-18.04-orange.svg)|![Pass](https://img.shields.io/badge/Pass-blue.svg)|
|![ubuntu20.04](https://img.shields.io/badge/Ubuntu-20.04-orange.svg)|![Pass](https://img.shields.io/badge/Pass-blue.svg)|
|![ubuntu22.04](https://img.shields.io/badge/Ubuntu-22.04-orange.svg)|![Pass](https://img.shields.io/badge/Pass-blue.svg)|

Test:

|PYTHON |STATE|
|---|---|
|![python3.6](https://img.shields.io/badge/Python-3.6-blue.svg)|![Pass](https://img.shields.io/badge/Pass-blue.svg)|
|![python3.8](https://img.shields.io/badge/Python-3.8-blue.svg)|![Pass](https://img.shields.io/badge/Pass-blue.svg)|
|![python3.10](https://img.shields.io/badge/Python-3.10-blue.svg)|![Pass](https://img.shields.io/badge/Pass-blue.svg)|

## 1 Installation Method

### 1.1 Installation Environment

Note: Python version is 3.10, it is recommended to use a conda environment, and python-can version should be higher than 4.3.1.

Create and activate the conda environment

```shell
conda create -n pyqt5 python=3.10
```
```shell
conda activate pyqt5
```

### 1.2 Install Dependencies

Install can and sdk

```shell
pip3 install python-can
```
```shell
pip3 install piper_sdk
```

View the details of piper_sdk, such as installation path, version, etc.

```shell
pip3 show piper_sdk
```
Ensure that the SDK version is 0.1.9.

0.0.x is the sdk version supported before the robotic arm V1.5-2 firmware.

The last version number of 0.0.x is 0.1.9.

To uninstall

```shell
pip3 uninstall piper_sdk
```

### 1.2 Install can Tools

```shell
sudo apt update && sudo apt install can-utils ethtool
```

If you encounter ip: command not found when executing bash scripts, install the ip command with sudo apt-get install iproute2.

### 1.3 Install PyQt5

Install Qt development tools
```shell
sudo apt install qt5-qmake qtbase5-dev
```

Install PyQt5

```shell
pip install pyqt5

```
## 2 Quick Start

### 2.1 Run

#### 2.1.1 Regular Run

```shell
cd ~/Piper_sdk_ui
conda activate pyqt5
```
```shell
python piper_ui.py
```

#### 2.1.2 Quick Run

Configuration (Note: Bash terminal required)

Check the conda environment location

```shell
conda env list
```
Output the environment location, for example
```
# conda environments:
#
base                   /home/tian/miniconda3
pyqt                   /home/tian/miniconda3/envs/pyqt
```
Add a shortcut command in ./bashrc
```shell
echo "alias pui='~/miniconda3/envs/pyqt5/bin/python ~/Piper_sdk_ui/piper_ui.py'" >> ~/.bashrc && source ~/.bashrc
```
Make sure to change the conda environment and piper_ui.py paths to your own.

Run

source ~/.bashrc can automatically source upon restarting the terminal
```shell
source ~/.bashrc
```

```shell
pui
```

### 2.2 Features

|Operation |Action|
|---|---|
|Find CAN Port button|Find the current CAN port, requires root password|
| (can0 / can*) options| Select the corresponding port to operate the robotic arm and display whether the port is activated. | 
| CAN port rename input box | Enter or change the port name, apply after activation. |
|Activate CAN Port button|Activate the port (after this, all subsequent functions can only be used after the port is activated)|
|Enable button|Enable the robotic arm|
|Disable button|Disable the robotic arm|
|Reset button|Reset the robotic arm, needs to be executed once after setting to teach mode (Note: after reset, the robotic arm will fall)|
|Gripper Zero button|Set the zero point for the robotic arm's gripper|
|Go Zero button|Move the robotic arm to the zero point|
|（Slave / Master）option|Set the robotic arm as Slave/Master (Master refers to teach mode)|
|Config init button|Set all joint limits, maximum joint speed, and joint acceleration to default values|
|Hardware version button|Output (update) the firmware version of the robotic arm controller in the top-right text box|
|Teach pendant stroke slider|Adjust teach pendant gripper percentage from 100%-200% (set to master arm, value displayed in the text box on the right)|
|Gripper stroke option|Set the stroke of the gripper currently in use (default is 70, select and confirm after choice)|
|Gripper control slider|Enable and control the opening/closing of the gripper, value displayed in the text box on the right|
|Gripper disable and clear err|Disable the gripper and clear errors (used when the gripper overheats and triggers an error)|
|Status information reading option|Start button begins/Stop button stops (prints in the lower-right text box and continuously updates)|
| |Angle Speed Limit: Read the maximum angle and speed limits of all the robotic arm's motors|
| |Joint Status: Read the joint angle message|
| |Gripper Status: Read the robotic arm's gripper status|
| |Piper Status: Read the robotic arm's status (different mode statuses)|
| |FK: Read the forward kinematics (FK) of the robot arm control and feedback for each joint|
|Max Acc Limit button|Print the current joint maximum acceleration limit in the lower-right text box|
|Installation position option|Select the installation direction of the robotic arm (select and confirm after choice)|
| |Parallel: Horizontal standard installation|
| |Left: Left side installation|
| |Right: Right side installation|
|Joint enable status text box|Displays the enable status of six joints (1 for enabled, 0 for disabled, starting from the first joint on the base)|
|Cancel button|Cancel the current operation|
|Exit button|Close the window|

## Notes

- CAN devices must be activated first, and the correct baud rate should be set before reading messages or controlling the robotic arm.
- The C_PiperInterface interface class can pass the activated CAN route name during instantiation, which can be obtained via ifconfig.
- Sometimes when executing CAN send, the terminal may show "Message NOT sent," meaning the CAN module has not successfully connected to the device. Check the module's connection to the robotic arm, then power cycle the robotic arm before retrying.
- After creating an instance of the SDK interface, it will check if the built-in CAN module is activated. For other CAN devices, set the second parameter to False, e.g., piper = C_PiperInterface_V2("can0", False).
- **The mit protocol for controlling individual joint motors of the robotic arm is an advanced feature. Improper use of this protocol may lead to damage to the robotic arm!**
