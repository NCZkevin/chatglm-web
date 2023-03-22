#!/bin/bash

# 将环境变量传递给 Python 脚本
export OPENAI_API_KEY="$OPENAI_API_KEY"
export OPENAI_TIMEOUT_MS="$OPENAI_TIMEOUT_MS"
export API_MODEL="$API_MODEL"
export SOCKS_PROXY="$SOCKS_PROXY"
export HOST="$HOST"
export PORT="$PORT"

# 启动 Python 脚本
python main.py --openai_api_key="$OPENAI_API_KEY" --openai_timeout_ms="$OPENAI_TIMEOUT_MS" --api_model="$API_MODEL" --socks_proxy="$SOCKS_PROXY" --host="$HOST" --port="$PORT"
