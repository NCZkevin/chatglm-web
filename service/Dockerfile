# 使用 Python 3.10 作为基础镜像
FROM python:3.10

# 设置工作目录
WORKDIR /app

# 复制项目文件到容器中
COPY . .

# ==rust是tiktoken依赖的环境==
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:$PATH"

# 安装依赖
RUN pip install --upgrade pip && pip install --upgrade --no-cache-dir -r requirements.txt

# 设置环境变量
ENV OPENAI_API_KEY=""
ENV OPENAI_TIMEOUT_MS="100000"
ENV API_MODEL="gpt-3.5-turbo"
ENV SOCKS_PROXY=""
ENV HOST="127.0.0.1"
ENV PORT=3002

# 复制 entrypoint.sh 脚本到容器中
COPY entrypoint.sh .

# 修改 entrypoint.sh 的权限
RUN chmod +x entrypoint.sh

# 启动命令
ENTRYPOINT ["./entrypoint.sh"]
