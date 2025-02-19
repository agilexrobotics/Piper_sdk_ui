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

Note: The Python version should be 3.10. It is recommended to use a conda environment, and the python-can version should be higher than 4.3.1.

Create and activate the conda environment:

```shell
conda create -n pyqt5 python=3.10
```

```shell
conda activate pyqt5
```

### 1.2 Install Dependencies

Install can and sdk:

```shell
pip3 install python-can
```

```shell
pip3 install piper_sdk
```

Check the details of piper_sdk, such as installation path, version, etc.:

```shell
pip3 show piper_sdk
```

Ensure the sdk version is 0.1.9.

The 0.0.x versions support firmware versions prior to robotic arm V1.5-2.

The last version of 0.0.x is 0.1.9.

To uninstall:

```shell
pip3 uninstall piper_sdk
```

### 1.3 Install CAN Tools

```shell
sudo apt update && sudo apt install can-utils ethtool
```

If you encounter the error "ip: command not found" when running a bash script, install the `ip` command by running:

```shell
sudo apt-get install iproute2
```

### 1.4 Install PyQt5

Install Qt development tools:

```shell
sudo apt install qt5-qmake qtbase5-dev
```

Install PyQt5:

```shell
pip install pyqt5
```

## 2 Quick Start

### 2.1 Running

#### 2.1.1 Regular Run

```shell
cd ~/Piper_sdk_ui
conda activate pyqt5
```

```shell
python piper_ui.py
```

#### 2.1.2 Quick Run

Configure (make sure it's a bash terminal).

Check the location of your conda environment:

```shell
conda env list
```

Example output:

```
# conda environments:
#
base                   /home/tian/miniconda3
pyqt                   /home/tian/miniconda3/envs/pyqt
```

Add a shortcut command to `~/.bashrc`:

```shell
echo "alias pui='~/miniconda3/envs/pyqt5/bin/python ~/Piper_sdk_ui/piper_ui.py'" >> ~/.bashrc && source ~/.bashrc
```

Make sure to change the conda environment and piper_ui.py paths to your own paths.

Run:

```shell
source ~/.bashrc
```

Then execute:

```shell
pui
```

### 2.2 Features

|Operation |Action|
|---|---|
|Find CAN Port Button|Search for the current CAN port, root password is required|
|(can0 / can*) Options|Select the robotic arm to operate based on the corresponding port, and check if the port is activated|
|CAN Port Rename Input Box|Enter or change the port name, apply after activation|
|Activate CAN Port Button|Activate the port (all subsequent functions can only be used after activation)|
|Enable Button|Enable the robotic arm|
|Disable Button|Disable the robotic arm|
|Reset Button|Reset the robotic arm, needs to be done after setting to teach mode (note: the arm will fall after reset)|
|Gripper Zero Button|Set the gripper's zero point|
|Go Zero Button|Move the robotic arm to the zero point|
|(Slave / Master) Option|Set the robotic arm to Slave/Master (Master is the teach mode)|
|Config Init Button|Set all joint limits, max speed, and max acceleration to default values|
|Stop button|The robotic arm slowly drops. After use, it needs to be reset and enabled twice again|
|Hardware Version Button|Display (update) the main control firmware version of the robotic arm in the top-right corner|
|Teach Pendant Stroke Slider|Zoom in/out the teach pendant stroke from 100%-200% (set to master arm, value displayed on the right)|
|Gripper Stroke Option|Set the current gripper stroke (default is 70, select and confirm)|
|Gripper Control Slider|Enable and control the gripper, value displayed on the right|
|Gripper Disable and Clear Error|Disable gripper and clear errors (use if gripper overheats)|
|Status Information Reading Option|Start/Stop button (prints in the lower-right text box, constantly updating)|
| |Angle Speed Limit: Read the maximum angle and speed limits of all the motors|
| |Joint Status: Read joint angle messages|
| |Gripper Status: Read the gripper status|
| |Piper Status: Read the robotic arm status (different modes)|
| |FK: Read the forward kinematics feedback for each joint|
|Max Acc Limit Button|Display the current joint max acceleration limit in the lower-right text box|
|Installation Position Option|Select the robotic arm installation direction (confirm after selection)|
| |Parallel: Horizontal installation|
| |Left: Left-side installation|
| |Right: Right-side installation|
|Joint Enable Status Text Box|Displays the joint enable status for all six joints (1 for enabled, 0 for disabled, first joint is the base)|
|Cancel Button|Cancel the current operation|
|Exit Button|Close the window|

## Q&A

- **Error**: libGL error: MESA-LOADER: failed to open iris: /usr/lib/dri/iris_dri.so: cannot open shared object file: No such file or directory (search paths /usr/lib/x86_64-linux-gnu/dri:$${ORIGIN}/dri:/usr/lib/dri, suffix _dri)

- **Solution**:
    ```
    conda install -c conda-forge gcc
    ```

## Notes

- You need to first activate the CAN device and set the correct baud rate before reading or controlling the robotic arm messages.
- The `C_PiperInterface` interface class allows passing the activated CAN route name when instantiating, which can be obtained via `ifconfig`.
- If you receive the "Message NOT sent" error when trying to send a CAN message, the CAN module may not be connected to the device. Check the connection, power cycle the robotic arm, and try again.
- The sdk interface checks for the activation of its internal CAN module upon instantiation. If using another CAN device, set the second argument to `False`, e.g., `piper = C_PiperInterface_V2("can0", False)`.
- **The advanced feature of controlling individual motors of the robotic arm via the MIT protocol should be used with caution, as improper use may damage the arm!**