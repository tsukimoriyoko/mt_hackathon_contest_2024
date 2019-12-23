# 桌面宠物 python实现

### 程序说明:
桌宠:python实现的桌面宠物 默认10秒播放一个动作, 鼠标双击左键 激活行走功能, 再次单击可以取消行走, 右键有一些简单的系统功能,后续会增加
 默认的图片是转载自 @XGBGHOST (微博)
当然, 如果你有自己的图片,可以进行替换, 也可以增加动作

### 环境及使用
基于python3.7, PyQt5

`python run.py` 即可运行 桌宠默认以守护进程来执行, 标椎输入输出在 stderr, stdin, stdout 文件里
`--no-daemon`  用非守护进程方式启动
`--tray` 启动托盘功能

### 文件说明
`core/action.py` 文件下是 桌宠每一个动作(真正的文件在`img`文件夹下), 
可以加动作,也可以减少动作
如果加动作,可以把一帧帧的图片放在`img`文件夹下, 然后再`action.py`里配置好地址,程序自动读取

`core/setting.py` 文件 是配置,说明如下

```Yaml
MOVIE_TIME_INTERVAL: 每个动画的播放间隔, 单位 秒
INIT_PICTURE: 桌宠静止时默认的图片
TRAY_ICON: 系统托盘的图标
ICON: 程序的图片
MOUSE_TO_LEFT_*: 鼠标左滑时的动作, 一共三帧
MOUSE_TO_RIGHT_*: 鼠标右滑时的动作, 一共三帧
WALK: 行走的动作, 一共2 帧, 多余的不会播放
```

### 联系方式
QQ: 469554659  
email: 469554659@qq.com  
如果有新的想法,或者运行有问题,可联系我  
