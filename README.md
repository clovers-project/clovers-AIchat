<div align="center">

# Clovers AIChat

AI 群聊机器人群聊

_✨ clovers 接入 AI api✨_

[![python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![license](https://img.shields.io/github/license/clovers-project/clovers-AIchat.svg)](./LICENSE)
[![pypi](https://img.shields.io/pypi/v/clovers_aichat.svg)](https://pypi.python.org/pypi/clovers_aichat)
[![pypi download](https://img.shields.io/pypi/dm/clovers_aichat)](https://pypi.python.org/pypi/clovers_aichat)
<br />

[![机器人 bug 研究中心](https://img.shields.io/badge/QQ%E7%BE%A4-744751179-maroon?)](https://qm.qq.com/q/3vpD9Ypb0c)

</div>

目前支持的 AI 平台有：

- [x] [ChatGPT](https://openai.com/)
- [x] [腾讯混元大模型](https://hunyuan.tencent.com/)
- [x] [通义千问](https://tongyi.aliyun.com/)
- [x] [Gemini](https://ai.google.dev/)
- [x] [DeepSeek](https://www.deepseek.com/)

# 安装

```shell
pip install clovers_AIchat
```

# 配置

基本上所有配置都在 config.py 中举例。请参考源代码。

下面是 config.py 文件对应的 clovers.toml 配置文件示例。

```toml
[clovers_AIchat]
timeout = 600
memory = 20
prompt_system = "\n你是有着二次元可爱少女形象的AI助手 名为小叶子"
[[clovers_AIchat.config_list]]
key = "qwen"
model = "qwen-plus"
url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
api_key = ""
whitelist = []
blacklist = []

[[clovers_AIchat.config_list]]
key = "hunyuan"
model = "hunyuan-lite"
url = "https://hunyuan.tencentcloudapi.com"
secret_id = ""
secret_key = ""
whitelist = []
blacklist = []

[clovers_AIchat.config_list.proxies]
"https://" = "http://127.0.0.1:7897"
[[clovers_AIchat.config_list]]
key = "mix"
whitelist = []
blacklist = []

[clovers_AIchat.config_list.text]
key = "qwen"
model = "qwen-plus"
url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
api_key = ""
[clovers_AIchat.config_list.image]
key = "qwen"
model = "qwen-vl-plus"
url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
api_key = ""
```

`timeout` 记忆保留时间，单位秒

`memory` 记忆条数

`prompt_system` 系统提示词

建议在提示词中保留如下文本，否则可能会导致模型带格式回复。

```
"你收到的消息格式为 "昵称 (日期 时间):消息" 例如 "小明 (2024-5-31 12:00):你好" 你的回复不应该有昵称，时间和日期。"
```

`config_list` 模型配置列表，模型配置列表内的每个元素都会单独创建一个模型类型，启用一个单独的客户端。

# 模型配置

模型配置也就是 config_list 内的元素，包含以下参数：

`key` 模型标识，目前支持

`chatgpt` ChatGPT

`hunyuan` 腾讯混元大模型

`qwen` 通义千问

`gemini` 谷歌 Gemini

`deepseek` DeepSeek 等

`mix` 图文混合模型（简单的用两个模型模拟图文多模态）。

`model` 模型名称，例如：`hunyuan-lite` `gemini-1.5-flash` `qwen-vl-plus` 等等

`whitelist` 白名单，只有白名单内的群可以使用此模型，默认为空，即所有用户都可以使用。

`blacklist` 黑名单，黑名单内的用户不可使用此模型，默认为空，即所有用户都可使用。

黑白名单为列表，里面的元素都是字符串。

注意：如果你配置了在一个群启用多个模型，那么多个模型都会响应。没人希望这样，所以请检查黑白名单。

`proxy` 此模型客户端使用的代理，配置参照 [httpx](https://www.python-httpx.org/) client 的 proxy 参数

`timeout` 为模型单独配置的记忆保留时间。

`memory` 为模型单独配置的记忆条数。

`prompt_system` 为模型单独配置系统提示词

以上三个的参数优先使用，如果没有配置就使用全局配置。

## ChatGPT

如果你的模型配置的 key 是 `chatgpt`,那么你还需要填写以下参数：

`url` 模型 api 接入点，例如 `https://api.openai.com/v1`

`api_key` OpenAI api key

## 腾讯混元大模型

如果你的模型配置的 key 是 `hunyuan`,那么你还需要填写以下参数：

`url` 模型 api 接入点，例如 `https://hunyuan.tencentcloudapi.com`

`secret_id` 腾讯云 api 密钥 id

`secret_key` 腾讯云 api 密钥 key

~~我想吐槽一下腾讯的加密方法看起来像是没事闲的~~

## 通义千问

如果你的模型配置的 key 是 `qwen`,那么你还需要填写以下参数：

`url` 模型 api 接入点，例如 `https://dashscope.aliyuncs.com/compatible-mode/v1`

`api_key` 阿里云 api key

## Gemini

如果你的模型配置的 key 是 `gemini`,那么你还需要填写以下参数：

`url` 模型 api 接入点，例如 `https://generativelanguage.googleapis.com/v1beta/models`,使用的方法为 generateContent 暂时不能修改。

`api_key` 谷歌云 api key

## DeepSeek

如果你的模型配置的 key 是 `deepseek`,那么你还需要填写以下参数：

`url` 模型 api 接入点，例如 `https://api.deepseek.com/`

`api_key` DeepSeek api key

## 图文混合模型

模型配置的 key 是 `mix`，那么你需要填写以下参数：

`text` 文本模型配置。

`image` 图像模型配置，注意这个模型要支持图像分析。

关于模型配置请跳转到 [模型配置](#模型配置) 查看。

注意不能在上面两个模型配置中配置 key = `mix`
