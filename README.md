[CN](README(CN).md)

## 1 安装方法

### 1.1 安装环境

注：python版本为3.10，建议使用conda环境，python-can版本应高于4.3.1

创建并激活conda环境

```shell
conda create -n pyqt5 python=3.10
```
```shell
conda activate pyqt5
```

### 1.2 安装依赖

安装can和sdk

```shell
pip3 install python-can
```
```shell
pip3 install piper_sdk
```

查看piper_sdk细节，比如安装路径，版本等信息

```shell
pip3 show piper_sdk
```

0.0.x 为机械臂V1.5-2固件版本前的sdk支持

当前0.0.x最后一个版本号为0.0.9

若要卸载

```shell
pip3 uninstall piper_sdk
```

### 1.2 安装can工具

```shell
sudo apt update && sudo apt install can-utils ethtool
```

如果执行bash脚本出现ip: command not found，请安装ip指令，一般是sudo apt-get install iproute2

### 1.3 安装PyQt5

安装 Qt 开发工具

```shell
sudo apt install qt5-qmake qtbase5-dev
```

安装pyqt5

```shell
pip install pyqt5

```
## 2 快速使用

### 2.1 运行

#### 2.1.1 常规运行

```shell
cd ~/Piper_sdk_ui
conda activate pyqt5
```
```shell
python piper_ui.py
```

#### 2.1.2 快捷运行

配置（注意需为bash终端）

查看conda环境位置

```shell
conda env list
```
输出环境位置，例如
```
# conda environments:
#
base                   /home/tian/miniconda3
pyqt                   /home/tian/miniconda3/envs/pyqt
```
在 ./bashrc中添加快捷指令
```shell
echo "alias pui='~/miniconda3/envs/pyqt5/bin/python ~/Piper_sdk_ui/piper_ui.py'" >> ~/.bashrc && source ~/.bashrc
```
注意更改conda环境和piper_ui.py的路径为自己的路径

运行

source ~/.bashrc可以通过重启终端自动source
```shell
source ~/.bashrc
```

```shell
pui
```

### 2.2 功能

|Operation |Action|
|---|---|
|Find CAN Port按钮|寻找当前Can端口，需要输入root密码|
|（can0 / can*）选项|根据对应端口选择要操作的机械臂|
|Activate CAN Port按钮|激活端口（按照表格顺序，在此之后的所有功能激活端口后才可以使用）|
|Enable按钮|机械臂使能|
|Disable按钮|机械臂失能|
|Reset按钮|机械臂重置，需要在设定为示教模式后执行一次（注意：重置后机械臂会掉落）|
|Gripper Zero按钮|机械臂夹爪零点设定|
|Go Zero按钮|机械臂前往零点|
|（Slave / Master）选项|机械臂设置为从臂/主臂（主臂即为示教模式）|
|Config init按钮|机械臂设置全部关节限位、关节最大速度、关节加速度为默认值|
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
|Max Acc Limit按钮|打印当前关节最大加速度限制在右下角文字框|
|Installation position选项|选择机械臂安装方向（选择后confirm确认）|
| |Parallel：水平正装|
| |Left：侧装左|
| |Right：侧装右|
|Joint enable status 文本框|六位显示关节使能状态（1为使能，0为失能，底座上数第一个关节在前）|
|Cancel按钮|取消当前操作|
|Exit按钮|关闭窗口|


## 注意事项

- 需要先激活can设备，并且设置正确的波特率，才可以读取机械臂消息或者控制机械臂
- C_PiperInterface 接口类在实例化时可传入激活的can路由名称，这个名称可以通过ifconfig得到
- 有时执行can发送，终端反馈Message NOT sent，是can模块没有成功连接设备，先检查模块与机械臂的连接状态，然后将机械臂断电后上电，再尝试发送
- sdk的interface在创建实例后会检测是否激活自带的can模块，如果是其它can设备，可以将第二个形参设定为False，如：piper = C_PiperInterface_V2("can0",False)
- **机械臂的mit协议控制单关节电机为高级功能,使用时需注意,此协议的使用不当会导致机械臂损坏！！！**
