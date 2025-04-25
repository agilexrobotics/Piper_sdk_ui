# Piper_sdk_ui

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

Clone the Project

```shell
cd $HOME
git clone https://github.com/agilexrobotics/Piper_sdk_ui.git
```

Note: Python version 3.10 is required, and a conda environment is needed.

Install System Dependencies

```bash
sudo apt update -y
sudo apt install -y can-utils ethtool
sudo apt install -y qt5-qmake qtbase5-dev
```

Set Up Python Environment

```bash
conda create -n piper_sdk_ui python=3.10 -y
conda activate piper_sdk_ui
pip3 install python-can
pip3 install piper_sdk
pip3 install pyqt5
```

## 2 Quick Start

Activate the Conda Environment

```bash
conda activate piper_sdk_ui
```

Run the UI File

```bash
cd $HOME/Piper_sdk_ui
python3 ./piper_ui.py
```

### 2.1 You can also add the command to your system environment variables

Check the Path of the Virtual Environment

```shell
conda env list | grep piper_sdk_ui
```

Typical output might look like:

```shell
piper_sdk_ui                    /home/agilex/miniconda3/envs/piper_sdk_ui
```

Then proceed as follows. Note that bash is used here. If other shells are needed, there may be slight differences. I will not go into details here.

```shell
echo "alias pui='$HOME/miniconda3/envs/piper_sdk_ui/bin/python ~/Piper_sdk_ui/piper_ui.py'" >> ~/.bashrc
source ~/.bashrc
```

Then you can use the global command to open the ui

```shell
pui
```

### 2.2 Features

|Operation |Action|
|---|---|
|Find CAN Port Button|Search for the current CAN port (root password required)|
|(can0 / can*) Option|Select the robotic arm to operate based on the corresponding port; displays whether the port is activated|
|CAN Port Rename Input Box|Enter or modify the port name, applied after activation|
|Activate CAN Port Button|Activate the port (must be activated before using subsequent features)|
|Enable Button|Enable the robotic arm|
|Disable Button|Disable the robotic arm|
|Reset Button|Reset the robotic arm; must be executed once in teach mode (Note: The robotic arm will drop after resetting)|
|Gripper Zero Button|Set the gripper zero position|
|Go Zero Button|Move the robotic arm to the zero position|
|Joint Ctrl Button|Pop up a joint control window to control the robotic arm's joint movement and set joint zero positions|
|Control Window|Slider: Move a single joint of the robotic arm|
| |Set Zero Button: Set the zero position for a single joint (note: the joint will be disabled during this process)|
| |Center Button: Move all joints to zero positions|
| |Random Button: Move all joints to random positions within a certain range|
| |All Set Zero Button: Set zero positions for all six joints, causing the robotic arm to disable|
|(Slave / Master) Option|Set the robotic arm as a slave or master (Master = Teach Mode)|
|Config Init Button|Set all joint limits, maximum joint speed, and joint acceleration to default values|
|Stop Button|The robotic arm will slowly lower; after using this, you need to reset and re-enable twice|
|Hardware Version Button|Displays (updates) the firmware version of the robotic arm’s main control in the upper-right text box|
|Teach Pendant Stroke Slider|Magnify the teaching gripper percentage between 100%-200% (Set as Master, value displayed in the right text box)|
|Gripper Stroke Option|Set the stroke of the current gripper (default is 70; confirm after selection)|
|Gripper Control Slider|Enable and control the gripper's opening and closing; value displayed in the right text box|
|Gripper Disable and Clear Error|Disable the gripper and clear errors (use in case of overheat protection error)|
|Status Information Reading Option|Start/Stop button (prints in the lower-right text box and continuously updates)|
| |Angle Speed Limit: Read the maximum angle and speed limits of all robotic arm motors|
| |Joint Status: Read joint angle data|
| |Gripper Status: Read the gripper's status|
| |Piper Status: Read the robotic arm’s operational status (various mode states)|
| |FK: Read the forward kinematics information for control and feedback of all joints|
|Max Acc Limit Button|Prints the current maximum acceleration limits of joints in the lower-right text box|
|Installation Position Option|Select the robotic arm's installation direction (confirm after selection)|
| |Parallel: Horizontal mounting|
| |Left: Side mounting (left)|
| |Right: Side mounting (right)|
|Joint Enable Status Text Box|Displays six joint enable statuses (1 = enabled, 0 = disabled, numbered from base upwards)|
|Cancel Button|Cancel the current operation|
|Exit Button|Close the window|

## Q&A

- **Error**:  
  ```  
  libGL error: MESA-LOADER: failed to open iris: /usr/lib/dri/iris_dri.so: cannot open shared object file: No such file or directory  
  (search paths /usr/lib/x86_64-linux-gnu/dri:\$${ORIGIN}/dri:/usr/lib/dri, suffix _dri)  
  ```  
- **Solution**:  
  ```bash
  conda activate pyqt5
  conda install -c conda-forge gcc
  ```

## Notes

- The CAN device must be activated, and the correct baud rate must be set before reading robotic arm messages or controlling the robotic arm.
- The `C_PiperInterface` interface class can take the activated CAN route name as an argument when instantiated. This name can be obtained via `ifconfig`.
- If CAN messages fail to send and the terminal outputs `Message NOT sent`, it indicates that the CAN module has not successfully connected to the device. Check the connection between the module and the robotic arm, power off the robotic arm, power it back on, and then try sending again.
- When creating an instance of the SDK interface, it checks if the built-in CAN module is activated. If using another CAN device, set the second parameter to `False`, for example:
  ```python
  piper = C_PiperInterface_V2("can0", False)
  ```

---

Let me know if you need any modifications! 😊