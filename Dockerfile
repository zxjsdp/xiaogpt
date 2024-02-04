FROM python:3.10 AS builder
WORKDIR /app
COPY requirements.txt .
# 设置清华源地址为 PyPI 源
ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
# 使用 ARG 定义的变量作为 pip 源地址
RUN python3 -m venv .venv && .venv/bin/pip install --no-cache-dir -r requirements.txt -i ${PIP_INDEX_URL}

FROM python:3.10-slim

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY xiaogpt/ ./xiaogpt/
COPY xiaogpt.py .

ENV XDG_CONFIG_HOME=/config
ENV XIAOGPT_PORT=9527
VOLUME /config
EXPOSE 9527

# xiaogpt --hardware L06A --mute_xiaoai --use_qwen --qwen_key 'sk-xxxxxx' --stream
ENTRYPOINT ["/app/.venv/bin/python3", "xiaogpt.py", "--config", "xiao_config.json"]
