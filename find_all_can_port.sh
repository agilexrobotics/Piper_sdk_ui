#!/bin/sh
# 检查系统是否安装了 can-utils。
if ! dpkg -l | grep -q "can-utils"; then
    echo "错误: 系统未检测到 can-utils."
    echo "请使用以下命令安装 can-utils:"
    echo "sudo apt update && sudo apt install can-utils"
    exit 1
fi

# 获取所有 CAN 接口的名称。
can_interfaces=$(ip -br link show type can | awk '{print $1}')

# 如果没有找到任何 CAN 接口，输出提示信息。
if [ -z "$can_interfaces" ]; then
    echo "提示: 系统中未找到任何 CAN 接口."
    exit 0
fi

# 遍历所有 CAN 接口。
for iface in $can_interfaces; do
    # 使用 ethtool 获取 bus-info（端口号）。
    BUS_INFO=$(sudo ethtool -i "$iface" | grep "bus-info" | awk '{print $2}')
    
    # 如果 bus-info 为空，则输出错误。
    if [ -z "$BUS_INFO" ]; then
        echo "错误: 无法获取接口 $iface 的 bus-info."
        continue
    fi

    # 检查接口是否已激活。
    IS_LINK_UP=$(ip link show "$iface" | grep -q "UP" && echo "True" || echo "False")

    # 输出接口信息。
    echo "接口名称: $iface"
    echo "端口号: $BUS_INFO"
    echo "是否已激活: $IS_LINK_UP"
done
