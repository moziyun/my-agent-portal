import streamlit as st
from openai import OpenAI  # 新版 openai 库推荐用这个导入方式

# 从 Streamlit Secrets 读取 API 密钥（安全，不暴露）
client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"],  # 读取配置的密钥，不用直接写
    # 如果用国内模型（如蚂蚁Ling），再加这行：base_url="https://lingstudio.antgroup.com/v1"
)

# 页面标题
st.title("我的全能 Agent 入口")

# 聊天输入框
user_input = st.chat_input("请输入需求（如抖音选题、UI 设计灵感、知识整理...）")

if user_input:
    # 根据关键词判断需求类型
    if "抖音" in user_input or "自媒体" in user_input:
        prompt = f"你是抖音自媒体运营专家，专注 UI 设计垂类，帮我处理需求：{user_input}，输出可执行的具体方案。"
    elif "UI" in user_input or "设计" in user_input:
        prompt = f"你是资深 UI 设计师，帮我处理需求：{user_input}，给出具体的设计思路、资源推荐和落地步骤。"
    elif "知识" in user_input or "学习" in user_input:
        prompt = f"你是知识管理教练，帮我处理需求：{user_input}，生成结构化的学习计划或知识清单。"
    else:
        prompt = user_input

    # 调用 AI 生成回答（新版 openai 库的调用方式）
    with st.spinner("AI 思考中..."):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # 先用免费额度多的 gpt-3.5-turbo，稳定
            messages=[{"role": "user", "content": prompt}]
        )
    # 展示回答
    st.write(response.choices[0].message.content)
