# ChatGLM Web

- [ChatGLM Web](#chatglm-web)
	- [介绍](#介绍)
	- [快速部署](#快速部署)
	- [开发环境搭建](#开发环境搭建)
		- [Node](#Node)
		- [PNPM](#PNPM)
		- [Python](#Python)
	- [开发环境启动项目](#开发环境启动项目)
		- [后端](#后端服务)
		- [前端](#前端网页)
	- [打包为docker容器](#打包为docker容器)
		- [前端打包](#前端资源打包(需要安装node和docker、docker-compose))
		- [后端打包](#后端服务打包)
	- [使用DockerCompose启动](#使用DockerCompose启动)
	- [常见问题](#常见问题)
	- [参与贡献](#参与贡献)
	- [赞助原作者](#赞助)
	- [License](#license)

## 介绍

这是一个可以自己在本地部署的`ChatGLM`网页，使用`ChatGLM-6B`模型来实现接近`ChatGPT`的对话效果。
源代码Fork和修改于[Chanzhaoyu/chatgpt-web](https://github.com/Chanzhaoyu/chatgpt-web/) & [WenJing95/chatgpt-web](https://github.com/WenJing95/chatgpt-web/)

与`ChatGPT`对比，`ChatGLM Web`有以下优势：

1. **独立部署**。`ChatGLM Web`只需要一个能运行`ChatGLM-6B`模型的服务器即可使用，可以使用自己微调的GLM模型。
2. **完全离线**。`ChatGLM Web`依赖于`ChatGLM-6B`模型，可以在离线环境或者内网中使用。


## 快速部署

如果你不需要自己开发，只需要部署使用，可以直接跳到 [使用最新版本docker镜像启动](#使用最新版本docker镜像启动)

## 开发环境搭建

### Node

`node` 需要 `^16 || ^18` 版本（`node >= 14`
需要安装 [fetch polyfill](https://github.com/developit/unfetch#usage-as-a-polyfill)
），使用 [nvm](https://github.com/nvm-sh/nvm) 可管理本地多个 `node` 版本

```shell
node -v
```

### PNPM

如果你没有安装过 `pnpm`

```shell
npm install pnpm -g
```

### Python

`python` 需要 `3.8` 以上版本，进入文件夹 `/service` 运行以下命令

```shell
pip install --no-cache-dir -r requirements.txt
```

## 开发环境启动项目

### 后端服务


```shell
# 进入文件夹 `/service` 运行以下命令
python main.py
```
还有以下可选参数可用：

- `device` 使用设备,cpu或者gpu
- `quantize` 量化等级。可选值：16，8，4，默认为16
- `host` HOST，默认值为 0.0.0.0
- `port` PORT，默认值为 3002

也就是说你也可以这样启动
```shell
python main.py --device='cuda:0' --quantize=16 --host='0.0.0.0' --port=3002
```

### 前端网页

根目录下运行以下命令

```shell
# 前端网页的默认端口号是1002，对接的后端服务的默认端口号是3002，可以在 .env 和 .vite.config.ts 文件中修改
pnpm bootstrap
pnpm dev
```

## 打包为docker容器

-- 待更新

## 常见问题

Q: 为什么 `Git` 提交总是报错？

A: 因为有提交信息验证，请遵循 [Commit 指南](./CONTRIBUTING.md)

Q: 如果只使用前端页面，在哪里改请求接口？

A: 根目录下 `.env` 文件中的 `VITE_GLOB_API_URL` 字段。

Q: 文件保存时全部爆红?

A: `vscode` 请安装项目推荐插件，或手动安装 `Eslint` 插件。

Q: 前端没有打字机效果？

A: 一种可能原因是经过 Nginx 反向代理，开启了 buffer，则 Nginx
会尝试从后端缓冲一定大小的数据再发送给浏览器。请尝试在反代参数后添加 `proxy_buffering off;`，然后重载 Nginx。其他 web
server 配置同理。

Q: build docker容器的时候，显示`exec entrypoint.sh: no such file or directory`？

A: 因为`entrypoint.sh`文件的换行符是`LF`，而不是`CRLF`，如果你用`CRLF`的IDE操作过这个文件，可能就会出错。可以使用`dos2unix`工具将`LF`换成`CRLF`。

## 参与贡献

贡献之前请先阅读 [贡献指南](./CONTRIBUTING.md)

感谢原作者[Chanzhaoyu](https://github.com/Chanzhaoyu/chatgpt-web/)和所有做过贡献的人，开源模型[ChatGLM](https://github.com/THUDM/ChatGLM-6B)


## 赞助

如果你觉得这个项目对你有帮助，请给我点个Star。

如果情况允许，请支持原作者[Chanzhaoyu](https://github.com/Chanzhaoyu/chatgpt-web/)

## License

MIT © [NCZkevin](./license)
