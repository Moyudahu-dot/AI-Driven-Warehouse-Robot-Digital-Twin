# GPU 虚拟机环境准备

本目录用于组员 A 在不破坏课程虚拟机现有环境的前提下，确认 Isaac Sim、ROS 2 和 Nav2 的安装与运行条件。

## 当前判断

远程桌面截图表明虚拟机提供 Linux 图形桌面，桌面存在名称类似 `start-isaac-s...` 的启动脚本。这说明课程方很可能已经安装或封装了 Isaac Sim，但仍需确认脚本目标、软件版本、GPU 访问、磁盘持久性和远程图形加速。不要在完成检查前自行升级显卡驱动、CUDA、Python 或 Isaac Sim。

建议把虚拟机作为唯一标准仿真环境，把个人电脑用于 Git、Python 模拟接口、报告和数据分析。每次虚拟机开放时集中完成仿真、ROS 2 联调和实验采集。

## 第一次登录检查

打开终端，将仓库克隆到纯英文短路径：

```bash
mkdir -p ~/workspace
cd ~/workspace
git clone https://github.com/Moyudahu-dot/AI-Driven-Warehouse-Robot-Digital-Twin.git
cd AI-Driven-Warehouse-Robot-Digital-Twin
git switch feature/a-simulation-navigation
```

如果仓库已经存在，进入原目录后执行 `git status`，先确认没有未提交修改，不要重复克隆或覆盖文件。

运行环境自检：

```bash
cd ~/workspace/AI-Driven-Warehouse-Robot-Digital-Twin
chmod +x environment/check_environment.sh
./environment/check_environment.sh
```

脚本会在当前目录生成 `environment_report_日期时间.txt`。报告可能包含主机名、用户名、IP 和安装路径，只在组内或向助教提交前确认是否需要脱敏，不要直接公开上传。

## 持久化验证

课程虚拟机每周只开三天，必须确认关机后用户目录不会还原。第一次登录执行：

```bash
date --iso-8601=seconds > ~/.warehouse_robot_vm_persistence_check
cat ~/.warehouse_robot_vm_persistence_check
```

下次虚拟机重新开机后再次运行：

```bash
cat ~/.warehouse_robot_vm_persistence_check
```

如果文件仍存在，说明至少用户目录具有跨开机持久性；如果消失，应立即向助教确认持久盘位置，并把代码、配置、日志和模型全部同步到 GitHub 或本地备份。

## Isaac Sim 检查顺序

1. 查看自检报告中桌面启动脚本的前 80 行，确认它最终调用的 `isaac-sim.sh` 路径。
2. 不修改脚本，先保存其完整内容和文件路径。
3. 在对应 Isaac Sim 安装目录寻找兼容性检查脚本：

   ```bash
   find /isaac-sim /isaacsim /opt "$HOME" -maxdepth 3 \
     -name 'isaac-sim.compatibility_check.sh' 2>/dev/null
   ```

4. 找到后从终端运行兼容性检查，不要先双击未知启动脚本：

   ```bash
   /实际安装路径/isaac-sim.compatibility_check.sh
   ```

5. 兼容性通过后，再使用课程方桌面脚本启动。记录启动时间、Isaac Sim 版本、是否正常显示视口、是否能创建空 Stage，以及命令窗口中的错误。

远程桌面能够显示 Linux 桌面不等于 Isaac Sim 已获得 GPU 加速。`nvidia-smi` 能识别 GPU且 Isaac Sim 视口正常渲染，才算图形环境通过。

## ROS 2 与 Nav2 版本决策

先以现有 Isaac Sim 版本和 Ubuntu 版本为准，不要先装最新版：

| 虚拟机组合 | 建议选择 |
| --- | --- |
| Ubuntu 24.04 + Isaac Sim 6.2 | ROS 2 Jazzy + Nav2 Jazzy |
| Ubuntu 22.04 + Isaac Sim 6.2 | ROS 2 Humble + Nav2 Humble，优先使用官方已验证组合 |
| 其他 Isaac Sim 版本 | 查该版本官方兼容表后再安装 |

如果 `/opt/ros/<发行版>/setup.bash` 已存在，应先使用现有版本。示例：

```bash
source /opt/ros/jazzy/setup.bash
# 或 source /opt/ros/humble/setup.bash

echo "$ROS_DISTRO"
ros2 pkg prefix nav2_bringup
```

只有在确认 ROS 2 尚未安装，并且发行版已经选定后，才安装 Nav2。常见的 Ubuntu 二进制包命令为：

```bash
sudo apt update
sudo apt install ros-$ROS_DISTRO-navigation2 ros-$ROS_DISTRO-nav2-bringup
```

执行安装前需要确认当前账号有 `sudo` 权限、APT 软件源可访问，并记录所有已安装包。不要自行安装或替换 NVIDIA 驱动、CUDA 和系统 Python。

## 第一周环境验收门槛

按顺序验收，前一项失败时先处理，不要继续叠加安装：

- [ ] VM-01：虚拟机用户目录跨开机保留。
- [ ] VM-02：`nvidia-smi` 能识别 GPU，显存和驱动无异常。
- [ ] VM-03：磁盘空间足够，项目工作目录可写。
- [ ] SIM-01：确认 Isaac Sim 的安装路径与版本。
- [ ] SIM-02：兼容性检查可运行。
- [ ] SIM-03：Isaac Sim GUI 和 3D 视口可正常启动。
- [ ] ROS-01：选定与 Isaac Sim、Ubuntu 匹配的 ROS 2 发行版。
- [ ] ROS-02：`ros2`、`colcon` 和 Nav2 可用。
- [ ] BRIDGE-01：Isaac Sim ROS 2 Bridge 启用。
- [ ] BRIDGE-02：播放仿真后可收到 `/clock`。
- [ ] NAV-01：Nova Carter 仓库示例能够启动。
- [ ] NAV-02：RViz 中设置目标后机器人能完成一次自主导航。
- [ ] TEAM-01：代码、配置和日志已推送或备份，不只保存在虚拟机。

## 三天开放周期的使用建议

第一天用于环境与基础场景，第二天用于 ROS 2/Nav2 和团队接口联调，第三天用于重复实验、日志导出与录屏。每次关机前执行：

```bash
git status
git log -1 --oneline
```

确认需要保留的源代码已提交和推送；大型日志、视频、模型权重和场景文件单独备份，不应直接塞入 Git 历史。

## 需要保留的证据

- 自检报告及脱敏版本。
- Isaac Sim 版本和兼容性检查截图。
- `nvidia-smi`、Ubuntu、ROS 2、Nav2 版本记录。
- `/clock` 输出截图或文本。
- Nova Carter 自主导航截图或短视频。
- 每次实验使用的 Git 提交号、配置和随机种子。
