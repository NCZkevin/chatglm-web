FROM pytorch/pytorch:1.13.1-cuda11.6-cudnn8-runtime
# Install linux packages
ENV DEBIAN_FRONTEND noninteractive
RUN apt update
RUN TZ=Etc/UTC apt install -y tzdata
RUN apt install --no-install-recommends -y gcc git zip curl htop libgl1-mesa-glx libglib2.0-0 libpython3-dev gnupg

COPY . .
RUN pip3  install -r requirements.txt
ENV model_path="/model"
ENV Device="cpu"
ENV Quantize=16
ENV HOST="0.0.0.0"
ENV PORT=3002

EXPOSE 3002

# 修改 entrypoint.sh 的权限
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
