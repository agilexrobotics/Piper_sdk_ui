# Piper_sdk_ui

[EN](README(EN).md)

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

## 1 安装方法

注：python版本为3.10，需要conda环境

```bash
cd ~/Piper_sdk_ui
bash env.sh
```

## 2 快速使用

```bash
pui
```

### 2.2 功能

|Operation |Action|
|---|---|
|Find CAN Port按钮|寻找当前Can端口，需要输入root密码|
|（can0 / can*）选项|根据对应端口选择要操作的机械臂，显示端口是否被激活|
|can口重命名输入框|输入或更改端口名字，激活后应用|
|Activate CAN Port按钮|激活端口（按照表格顺序，在此之后的所有功能激活端口后才可以使用）|
|Enable按钮|机械臂使能|
|Disable按钮|机械臂失能|
|Reset按钮|机械臂重置，需要在设定为示教模式后执行一次（注意：重置后机械臂会掉落）|
|Gripper Zero按钮|机械臂夹爪零点设定|
|Go Zero按钮|机械臂前往零点|
|Joint Ctrl按钮|弹出关节控制窗口,控制机械臂关节运动,设置关节零点|
|控制窗口|控制滑块：滑动控制机械臂单关节运动|
| |Set Zero按钮：设置单关节零点，注意使用时会单关节失能|
| |Center按钮：所有关节回零点|
| |Random按钮：所有关节移动到一定范围内的随机位置|
| |All Set Zero按钮：设置6个关节的零点，机械臂会失能|
|（Slave / Master）选项|机械臂设置为从臂/主臂（主臂即为示教模式）|
|Config init按钮|机械臂设置全部关节限位、关节最大速度、关节加速度为默认值|
|Stop按钮|机械臂缓慢下落，使用后需要reset，并重新使能两次|
|hardware version按钮|输出（更新）机械臂主控固件版本在右上方文字框|
|Teach pendant stroke滑块|示教夹抓百分比放大100%-200%（设置主臂，值显示在右侧文字框）|
|Gripper stroke选项|设定正在使用夹爪的行程（默认为70，选择后confirm确认）|
|Gripper control滑块|夹爪使能并控制张合，值显示在右侧文字框|
|Gripper disable and clear err|夹爪失能清错（当夹爪过热保护报错时使用）|
|Status information reading选项|Start按钮开始/Stop停止（打印在右下文字框，并不断更新）|
| |Angle Speed Limit：读取机械臂的所有电机的最大角度和速度限制|
| |Joint Status：读取关节角消息|
| |Gripper Status：读取机械臂夹爪状态|
| |Piper Status：机械臂状态读取(不同模式状态)|
| |FK：读取机械臂控制及反馈信息各关节正解|
|Max Acc Limit按钮|打印当前关节最大加速度限制在右下角文字框|
|Installation position选项|选择机械臂安装方向（选择后confirm确认）|
| |Parallel：水平正装|
| |Left：侧装左|
| |Right：侧装右|
|Joint enable status 文本框|六位显示关节使能状态（1为使能，0为失能，底座上数第一个关节在前）|
|Cancel按钮|取消当前操作|
|Exit按钮|关闭窗口|

## Q$A

- **报错** ：libGL error: MESA-LOADER: failed to open iris: /usr/lib/dri/iris_dri.so: 无法打开共享目标文件: 没有那个文件或目录 (search paths /usr/lib/x86_64-linux-gnu/dri:\$${ORIGIN}/dri:/usr/lib/dri, suffix _dri)

- **解决** ：

    ```bash
    conda activate pyqt5
    conda install -c conda-forge gcc
    ```

## 注意事项

- 需要先激活can设备，并且设置正确的波特率，才可以读取机械臂消息或者控制机械臂
- C_PiperInterface 接口类在实例化时可传入激活的can路由名称，这个名称可以通过ifconfig得到
- 有时执行can发送，终端反馈Message NOT sent，是can模块没有成功连接设备，先检查模块与机械臂的连接状态，然后将机械臂断电后上电，再尝试发送
- sdk的interface在创建实例后会检测是否激活自带的can模块，如果是其它can设备，可以将第二个形参设定为False，如：piper = C_PiperInterface_V2("can0",False)
