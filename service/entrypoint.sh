#!/bin/bash

# 将环境变量传递给 Python 脚本
export Device="$Device"
export Quantize="$Quantize"
export HOST="$HOST"
export PORT="$PORT"

# 启动 Python 脚本
# python main.py --device="$Device" --quantize=$Quantize --host='$HOST' --port=$PORT
python main.py --device='cpu' --quantize=16 --host='0.0.0.0' --port=3002
