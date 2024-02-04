# xiaogpt（小爱音箱接入大语言模型 LLM & NAS Docker 部署）

[![Docker Image Version (latest by date)](https://img.shields.io/docker/v/zxjsdp/xiaogpt?color=%23086DCD&label=Docker%20镜像)](https://hub.docker.com/repository/docker/zxjsdp/xiaogpt)

## 一、简介

### 1.1 简介

小爱（小米）音箱接入通义千问、ChatGPT 等大语言模型。

本仓库由 [yihong0618/xiaogpt](https://github.com/yihong0618/xiaogpt) fork 而来，主要改动：
1. 针对国内网络环境及大部分人的情况，将阿里巴巴`通义千问`的接入作为主线，简化使用成本；
2. 对 Docker 部署进行了一些调整和细化，可以很方便的在群晖 Synology NAS 上部署并为小爱接入千问。

因为修改和优化的侧重方向不同，因此暂时先不合并回原仓库。如果希望优先接入的是 GPT系列/Gemini 等模型基座，建议直接使用原作者 [yihong0618/xiaogpt](https://github.com/yihong0618/xiaogpt) 在 PyPI 上已经上传好的包，非常方便。

https://user-images.githubusercontent.com/15976103/226803357-72f87a41-a15b-409e-94f5-e2d262eecd53.mp4


### 1.2 支持的 AI 大模型类型

- [通义千问系列](https://help.aliyun.com/zh/dashscope/developer-reference/api-details)
- GPT 系列
- ChatGPT
- New Bing
- [ChatGLM](http://open.bigmodel.cn/)
- [Gemini](https://makersuite.google.com/app/apikey)
- [Bard](https://github.com/dsdanielpark/Bard-API)

### 1.3 一点原理（by 原作者 [yihong0618](https://github.com/yihong0618)）

[不用 root 使用小爱同学和 ChatGPT 交互折腾记](https://github.com/yihong0618/gitblog/issues/258)


## 二、接入通义千问的示例

### 2.1 获取阿里云模型服务灵积 DashScope API key

API Key 用于后续调用通义千问的 `--qwen_key` 参数：
1. 若没有阿里云账号，需进行注册：<https://www.aliyun.com/>；
2. 前往 API key 管理页面，创建新的 API-Key：<https://dashscope.console.aliyun.com/apiKey>；
3. 后续 API key 使用情况，可在总览页面查看：<https://dashscope.console.aliyun.com/overview>。


### 2.2 获取小米音响DID

参考：
- MiService Fork 版：<https://github.com/yihong0618/MiService>
- 原始仓库：<https://github.com/Yonsm/MiService>

获取步骤：

第1步（若无特殊诉求，可直接安装 miservice_fork 包）：

    pip install miservice_fork -i https://pypi.tuna.tsinghua.edu.cn/simple

如果有修改诉求，可使用 virtualenv 本地创建虚拟环境并安装（避免污染全局 Python 环境）：

    git clone git@github.com:yihong0618/MiService.git
    python3 -m venv .venv
    source .venv/bin/activate
    pip3 install .

第2步（设置环境变量）：
> 注：如果遇到特殊字符等奇怪的问题，也可以直接修改 `miservice/cli.py` 中 `env.get("MI_USER")` 及 `env.get("MI_PASS")` 部分，直接替换为真实的用户名及密码。

    export MI_USER=xxxx
    export MI_PASS=xxx

第3步（获取小米设备ID，取小爱音箱设备配置的 `did` 字段）：
> 示例返回：
> {
>   "name": "小爱",
>   "model": "xiaomi.wifispeaker.l06a",
>   "did": "xxxxxx",
>   "token": "xxxxxx"
> }

    micli list

后续可将 MI_DID 设置进环境变量，供 xiaogpt 获取。

> 获取 DID 报错时，可尝试更换一下无线网络
>
> 常见问题：
> 1. 报错 `AttributeError: 'NoneType' object has no attribute 'encode'`，可以看看是否未成功设置环境变量（例如 bash 下是否未使用 export 而是使用了 set）。
> 2. 在 `self.token['userId'] = resp['userId']` 的地方报错，可以看看 MI_USER 是否用的是小米 ID 而非可以用于登录的小米邮箱或用户名。


### 2.3 安装 xiaogpt（Clone 仓库后安装及运行）

本地安装，拉取仓库：

    git clone https://github.com/zxjsdp/xiaogpt.git

创建 Python virtualenv，避免污染全局 Python 环境：

    cd xiaogpt
    python3 -m venv .venv
    source .venv/bin/activate

在 virtualenv 中安装 xiaogpt 及依赖：

    pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

    # 或如果需要对源码做一些调整
    pip3 install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple


### 2.4 使用 Python 直接运行 xiaogpt

参考 2.2 获取小爱设备 DID 后，设置 MI_DID 环境变量：

    export MI_DID=xxxxxx

获取小爱音箱设备型号，在小爱音箱底部，例如：

    L06A

本地快捷运行：

    xiaogpt --hardware L06A --mute_xiaoai --use_qwen --qwen_key 'sk-xxxxxx' --stream

> 备注：
>
> 本 fork 中将千问模型改为了 qwen_max（因为 24 年初 qwen_max 限免，暂不计算 token 费用）。若需要调整回 qwen_turbo 等其他模型，可在 `qwen_bot.py` 中搜索替换 `Generation.Models.qwen_max`
>
> 同时为了使用 qwen_max，本仓库升级了部分包版本：`dashscope==1.14.1`

也可以通过配置文件运行，复制仓库下的 `xiao_config.json.example`，修改对应字段（以运行千问的 config 为例）：

    {
      "use_qwen": true,
      "hardware": "<小爱设备型号>",
      "qwen_key": "<阿里云 API Key>",
      "mi_did": "<小爱设备DID>",
      "account": "<小米账号>",
      "password": "<小米密码>",
      "stream": false,
      "use_command": false,
      "mute_xiaoai": true,
      "verbose": false,
      "tts": "mi",
      "edge_tts_voice": "zh-CN-XiaoxiaoNeural",
      "prompt": "请用100字以内回答",
      "keyword": ["请"],
      "change_prompt_keyword": ["更改提示词"],
      "start_conversation": "开始持续对话",
      "end_conversation": "结束持续对话"
    }

然后运行：

    python3 xiaogpt.py --config xiao_config.json

    # 或直接
    xiaogpt --config xiao_config.json


接下来即可与小爱音箱对话，包含`请`关键词时，会触发查询通义千问API（例如：呼叫“小爱同学”唤起对话后，说“请问你是谁”）。
> 备注：小爱音箱默认 TTS 读 Qian Wen 存在一些问题，因此念出的名称也做了一些调整。


### 2.5 使用 Docker 运行 xiaogpt（支持在群晖 Docker 上直接运行）

从 DockerHub 拉取面向接入通义千问优化后的 image：

    docker pull zxjsdp/xiaogpt:latest

网络条件不佳的话，也可基于本 repo 直接构建 Docker 镜像：

    docker build -t xiaogpt .

运行 Docker 镜像：
> 注：xiaogpt_config.json 文件可以放到本机或 NAS 上，挂载映射到容器里作为配置使用。

    # 临时调试（挂载映射刚刚修改好的 xiaogpt_config.json 文件）
    docker run --rm -it -p 9527:9527 -v ./xiao_config.json:/app/xiao_config.json xiaogpt

    # 后台长期运行（挂载容器外的 xiaogpt_config.json 文件）
    docker run --name xiaogpt -dp 9527:9527 -v /path/to/xiao_config.json:/app/xiao_config.json xiaogpt


常见错误：

1. 如果运行报错`登录验证失败`，可以检查一下 xiaogpt_config.json 里面的小米用户名及密码是否有正确填写。



## 三、其他信息（原始仓库教程）
### 3.1 接入 GPT 等模型基座时更具体的步骤

- `pip install -U --force-reinstall xiaogpt`
- 参考我 fork 的 [MiService](https://github.com/yihong0618/MiService) 项目 README 并在本地 terminal 跑 `micli list` 拿到你音响的 DID 成功 **别忘了设置 export MI_DID=xxx** 这个 MI_DID 用
- run `xiaogpt --hardware ${your_hardware} --use_chatgpt_api` hardware 你看小爱屁股上有型号，输入进来，如果在屁股上找不到或者型号不对，可以用 `micli mina` 找到型号
- 跑起来之后就可以问小爱同学问题了，“帮我"开头的问题，会发送一份给 ChatGPT 然后小爱同学用 tts 回答
- 如果上面不可用，可以尝试用手机抓包，https://userprofile.mina.mi.com/device_profile/v2/conversation 找到 cookie 利用 `--cookie '${cookie}'` cookie 别忘了用单引号包裹
- 默认用目前 ubus, 如果你的设备不支持 ubus 可以使用 `--use_command` 来使用 command 来 tts
- 使用 `--mute_xiaoai` 选项，可以快速停掉小爱的回答
- 使用 `--account ${account} --password ${password}`
- 如果有能力可以自行替换唤醒词，也可以去掉唤醒词
- 使用 `--use_chatgpt_api` 的 api 那样可以更流畅的对话，速度特别快，达到了对话的体验, [openai api](https://platform.openai.com/account/api-keys), 命令 `--use_chatgpt_api`
- 使用 gpt-3 的 api 那样可以更流畅的对话，速度快, 请 google 如何用 [openai api](https://platform.openai.com/account/api-keys) 命令 --use_gpt3
- 如果你遇到了墙需要用 Cloudflare Workers 替换 api_base 请使用 `--api_base ${url}` 来替换。 **请注意，此处你输入的api应该是'`https://xxxx/v1`'的字样，域名需要用引号包裹**
- 可以跟小爱说 `开始持续对话` 自动进入持续对话状态，`结束持续对话` 结束持续对话状态。
- 可以使用 `--tts edge` 来获取更好的 tts 能力
- 可以使用 `--tts openai` 来获取 openai tts 能力
- 可以使用 `--use_langchain` 替代 `--use_chatgpt_api` 来调用 LangChain（默认 chatgpt）服务，实现上网检索、数学运算..

e.g.

```shell
export OPENAI_API_KEY=${your_api_key}
xiaogpt --hardware LX06 --use_chatgpt_api
# or
xiaogpt --hardware LX06 --cookie ${cookie} --use_chatgpt_api
# 如果你想直接输入账号密码
xiaogpt --hardware LX06 --account ${your_xiaomi_account} --password ${your_password} --use_chatgpt_api
# 如果你想 mute 小米的回答
xiaogpt --hardware LX06  --mute_xiaoai --use_chatgpt_api
# 使用流式响应，获得更快的响应
xiaogpt --hardware LX06  --mute_xiaoai --stream
# 如果你想使用 gpt3 ai
export OPENAI_API_KEY=${your_api_key}
xiaogpt --hardware LX06  --mute_xiaoai --use_gpt3
# 如果你想使用 google 的 gemini
xiaogpt --hardware LX06  --mute_xiaoai --use_gemini --gemini_key ${gemini_key}
# 如果你想使用阿里的通义千问
xiaogpt --hardware LX06  --mute_xiaoai --use_qwen --qen_key ${qwen_key}
# 如果你想用 edge-tts
xiaogpt --hardware LX06 --cookie ${cookie} --use_chatgpt_api --tts edge
# 如果你想使用 LangChain + SerpApi 实现上网检索或其他本地服务（目前仅支持 stream 模式）
export OPENAI_API_KEY=${your_api_key}
export SERPAPI_API_KEY=${your_serpapi_key}
xiaogpt --hardware Lx06 --use_langchain --mute_xiaoai --stream --openai_key ${your_api_key} --serpapi_api_key ${your_serpapi_key}
```

使用 git clone 运行

```shell
export OPENAI_API_KEY=${your_api_key}
python3 xiaogpt.py --hardware LX06
# or
python3 xiaogpt.py --hardware LX06 --cookie ${cookie}
# 如果你想直接输入账号密码
python3 xiaogpt.py --hardware LX06 --account ${your_xiaomi_account} --password ${your_password} --use_chatgpt_api
# 如果你想 mute 小米的回答
python3 xiaogpt.py --hardware LX06  --mute_xiaoai
# 使用流式响应，获得更快的响应
python3 xiaogpt.py --hardware LX06  --mute_xiaoai --stream
# 如果你想使用 gpt3 ai
export OPENAI_API_KEY=${your_api_key}
python3 xiaogpt.py --hardware LX06  --mute_xiaoai --use_gpt3
# 如果你想使用 ChatGLM api
python3 xiaogpt.py --hardware LX06  --mute_xiaoai --use_glm --glm_key ${glm_key}
# 如果你想使用 google 的 bard
python3 xiaogpt.py --hardware LX06  --mute_xiaoai --use_bard --bard_token ${bard_token}
# 如果你想使用 google 的 gemini
python3 xiaogpt.py --hardware LX06  --mute_xiaoai --use_gemini --gemini_key ${gemini_key}
# 如果你想使用阿里的通义千问
python3 xiaogpt.py --hardware LX06  --mute_xiaoai --use_qwen --qen_key ${qwen_key}
# 如果你想使用 LangChain+SerpApi 实现上网检索或其他本地服务（目前仅支持 stream 模式）
export OPENAI_API_KEY=${your_api_key}
export SERPAPI_API_KEY=${your_serpapi_key}
python3 xiaogpt.py --hardware Lx06 --use_langchain --mute_xiaoai --stream --openai_key ${your_api_key} --serpapi_api_key ${your_serpapi_key}
```

### 3.2 config.json

如果想通过单一配置文件启动也是可以的, 可以通过 `--config` 参数指定配置文件, config 文件必须是合法的 JSON 格式
参数优先级

- cli args > default > config

```shell
python3 xiaogpt.py --config xiao_config.json
# or
xiaogpt --config xiao_config.json
```

或者

```shell
cp xiao_config.json.example xiao_config.json
python3 xiaogpt.py
```

若要指定 OpenAI 的模型参数，如 model, temporature, top_p, 请在config.json中指定：

```json
{
    ...
    "gpt_options": {
        "temperature": 0.9,
        "top_p": 0.9,
    }
}
```

具体参数作用请参考 [Open AI API 文档](https://platform.openai.com/docs/api-reference/chat/create)。
ChatGLM [文档](http://open.bigmodel.cn/doc/api#chatglm_130b)
Bard-API [参考](https://github.com/dsdanielpark/Bard-API)

### 3.3 配置项说明

| 参数                  | 说明                                                                    | 默认值                                                                                                    |可选值            |
| --------------------- | ----------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- | --------------- |
| hardware              | 设备型号                                                                |                                                                                                           |
| account               | 小爱账户                                                                |                                                                                                           |
| password              | 小爱账户密码                                                            |                                                                                                           |
| openai_key            | openai的apikey                                                          |                                                                                                           |
| serpapi_api_key       | serpapi的key 参考 [SerpAPI](https://serpapi.com/)                       |                                                                                                           |
| glm_key               | chatglm 的 apikey                                                       |                                                                                                           |
| gemini_key            | gemini 的 apikey [参考](https://makersuite.google.com/app/apikey)                                                      |                                                                                                           |
| qwen_key              | qwen 的 apikey [参考](https://help.aliyun.com/zh/dashscope/developer-reference/api-details)                                                      |                                                                                                           |
| bard_token            | bard 的 token 参考 [Bard-API](https://github.com/dsdanielpark/Bard-API) |                                                                                                           |
| cookie                | 小爱账户cookie （如果用上面密码登录可以不填）                             |                                                                                                           |
| mi_did                | 设备did                                                                 |                                                                                                           |
| use_command           | 使用 MI command 与小爱交互                                              | `false`                                                                                                   |
| mute_xiaoai           | 快速停掉小爱自己的回答                                                  | `true`                                                                                                    |
| verbose               | 是否打印详细日志                                                        | `false`                                                                                                   |
| bot                   | 使用的 bot 类型，目前支持gpt3,chatgptapi和newbing                       | `chatgptapi`                                                                                              |
| tts                   | 使用的 TTS 类型                                                         | `mi`                                                                                                      | `edge`、 `openai` | 
| tts_voice             | TTS 的嗓音                                                              | `zh-CN-XiaoxiaoNeural`(edge), `alloy`(openai)                                                             |
| prompt                | 自定义prompt                                                            | `请用100字以内回答`                                                                                       |
| keyword               | 自定义请求词列表                                                        | `["请"]`                                                                                                  |
| change_prompt_keyword | 更改提示词触发列表                                                      | `["更改提示词"]`                                                                                          |
| start_conversation    | 开始持续对话关键词                                                      | `开始持续对话`                                                                                            |
| end_conversation      | 结束持续对话关键词                                                      | `结束持续对话`                                                                                            |
| stream                | 使用流式响应，获得更快的响应                                            | `false`                                                                                                   |
| proxy                 | 支持 HTTP 代理，传入 http proxy URL                                     | ""                                                                                                        |
| gpt_options           | OpenAI API 的参数字典                                                   | `{}`                                                                                                      |
| bing_cookie_path      | NewBing使用的cookie路径，参考[这里]获取                                 | 也可通过环境变量 `COOKIE_FILE` 设置                                                                       |
| bing_cookies          | NewBing使用的cookie字典，参考[这里]获取                                 |                                                                                                           |
| deployment_id         | Azure OpenAI 服务的 deployment ID                                       | 参考这个[如何找到deployment_id](https://github.com/yihong0618/xiaogpt/issues/347#issuecomment-1784410784) |
| api_base              | 如果需要替换默认的api,或者使用Azure OpenAI 服务                         | 例如：`https://abc-def.openai.azure.com/`                                                                 |

[这里]: https://github.com/acheong08/EdgeGPT#getting-authentication-required

### 3.4 注意

1. 请开启小爱同学的蓝牙
2. 如果要更改提示词和 PROMPT 在代码最上面自行更改
3. 目前已知 LX04、X10A 和 L05B L05C 可能需要使用 `--use_command`，否则可能会出现终端能输出GPT的回复但小爱同学不回答GPT的情况。这几个型号也只支持小爱原本的 tts.
4. 在wsl使用时, 需要设置代理为 http://wls的ip:port(vpn的代理端口), 否则会出现连接超时的情况, 详情 [报错： Error communicating with OpenAI](https://github.com/yihong0618/xiaogpt/issues/235)

### 3.5 QA

1. 用破解么？不用
2. 你做这玩意也没用啊？确实。。。但是挺好玩的，有用对你来说没用，对我们来说不一定呀
3. 想把它变得更好？PR Issue always welcome.
4. 还有问题？提 Issue 哈哈
5. Exception: Error https://api2.mina.mi.com/admin/v2/device_list?master=0&requestId=app_ios_xxx: Login failed [@KJZH001](https://github.com/KJZH001)<br>
   这是由于小米风控导致，海外地区无法登录大陆的账户，请尝试cookie登录
   无法抓包的可以在本地部署完毕项目后再用户文件夹`C:\Users\用户名`下面找到.mi.token，然后扔到你无法登录的服务器去<br>
   若是linux则请放到当前用户的home文件夹，此时你可以重新执行先前的命令，不出意外即可正常登录（但cookie可能会过一段时间失效，需要重新获取）<br>
   详情请见 [https://github.com/yihong0618/xiaogpt/issues/332](https://github.com/yihong0618/xiaogpt/issues/332)

### 3.6 视频教程

https://www.youtube.com/watch?v=K4YA8YwzOOA

### 3.7 Docker

#### 常规用法

X86/ARM Docker Image: `yihong0618/xiaogpt`

```shell
docker run -e OPENAI_API_KEY=<your-openapi-key> yihong0618/xiaogpt <命令行参数>
```

如

```shell
docker run -e OPENAI_API_KEY=<your-openapi-key> yihong0618/xiaogpt --account=<your-xiaomi-account> --password=<your-xiaomi-password> --hardware=<your-xiaomi-hardware> --use_chatgpt_api
```

#### 使用配置文件

xiaogpt的配置文件可通过指定volume /config，以及指定参数--config来处理，如

```shell
docker run -v <your-config-dir>:/config yihong0618/xiaogpt --config=/config/config.json
```

#### 本地编译Docker Image

```shell
 docker build -t xiaogpt .
```

如果在安装依赖时构建失败或安装缓慢时，可以在构建 Docker 镜像时使用 `--build-arg` 参数来指定国内源地址：

```sh
docker build --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple -t xiaogpt .
```

如果需要在Apple M1/M2上编译x86

```shell
 docker buildx build --platform=linux/amd64 -t xiaogpt-x86 .
```

#### 第三方 TTS

我们目前支持两种第三方 TTS：edge/openai

[edge-tts](https://github.com/rany2/edge-tts) 提供了类似微软tts的能力

##### Usage

你可以通过参数 `tts`, 来启用它

```json
{
  "tts": "edge",
  "tts_voice": "zh-CN-XiaoxiaoNeural"
}
```

查看更多语言支持, 从中选择一个

```shell
edge-tts --list-voices
```

##### 在容器中使用edge-tts

由于 Edge TTS 启动了一个本地的 HTTP 服务，所以需要将容器的端口映射到宿主机上，并且指定本地机器的 hostname:

```shell
docker run -v <your-config-dir>:/config -p 9527:9527 -e XIAOGPT_HOSTNAME=<your ip> yihong0618/xiaogpt --config=/config/config.json
```

注意端口必须映射为与容器内一致，XIAOGPT_HOSTNAME 需要设置为宿主机的 IP 地址，否则小爱无法正常播放语音。

### 3.8 推荐的 fork

- [XiaoBot](https://github.com/longbai/xiaobot) -> Go语言版本的Fork, 带支持不同平台的UI

### 3.9 感谢

- [xiaomi](https://www.mi.com/)
- [PDM](https://pdm.fming.dev/latest/)
- @[Yonsm](https://github.com/Yonsm) 的 [MiService](https://github.com/Yonsm/MiService)
- @[pjq](https://github.com/pjq) 给了这个项目非常多的帮助
- @[frostming](https://github.com/frostming) 重构了一些代码，支持了`持续会话功能`

### 3.10 赞赏

谢谢就够了
