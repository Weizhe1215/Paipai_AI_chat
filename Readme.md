# 基于开源大模型Baichuan-13B 对尽调文本进行分析 Demo

## 1. 开始之前

### 硬件配置
GPU推理：支持cuda，且显存>=16G \
CPU推理：内存频率越高越好，内存>=32G

### 环境配置

在终端中输入该命令以安装依赖，我本地测试使用的是python 3.11

```
pip install -r requirements.txt
```
\
torch 需要额外安装，如果你本地有支持cuda的英伟达显卡，则输入以下命令安装：
```
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```
若使用CPU推理，则输入以下命令进行安装：
```
pip install torch torchvision torchaudio
```

安装windows版本下的bitsandbytes参考这个，有别人编译好的版本，pip 直接下载的话与win不兼容
https://github.com/jllllll/bitsandbytes-windows-webui

### 模型下载

chatglm6b:
```
git clone https://www.modelscope.cn/ZhipuAI/chatglm3-6b.git
```

Baichuan2-13B-4bit:
```
git clone https://www.modelscope.cn/baichuan-inc/Baichuan2-13B-Chat-4bits.git
```


## 2. Demo 使用
本demo是使用开源模型，Baichuan-13B，对尽调报告进行分析后，提取所使用的因子的应用。在开始前需要检查以下几项：
1. 所有尽调报告在根目录的"尽调报告"目录下储存
2. 把下载好的模型，放在根目录下，模型文件夹为chatglm6b
3. functions.py 为运行项目所必须的函数
4. 运行Demo.ipynb, 查看运行结果


