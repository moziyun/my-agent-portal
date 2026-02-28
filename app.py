import streamlit as st
import openai

# 配置 OpenAI API 密钥
openai.api_key = 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  # 替换成你自己的密钥

# 页面标题
st.title("我的全能 Agent 入口")

# 聊天输入框
user_input = st.chat_input("请输入需求（如抖音选题、UI 设计灵感、知识整理...）")

if user_input:
    # 根据关键词判断需求类型，调用不同的 Agent 逻辑
    if "抖音" in user_input or "自媒体" in user_input:
        prompt = f"你是抖音自媒体运营专家，帮我处理需求：{user_input}。要求结合 UI 设计领域，输出清晰的执行方案。"
    elif "UI" in user_input or "设计" in user_input:
        prompt = f"你是资深 UI 设计师，帮我处理需求：{user_input}。要求给出具体的设计思路、资源推荐或优化建议。"
    elif "知识" in user_input or "学习" in user_input:
        prompt = f"你是知识管理教练，帮我处理需求：{user_input}。要求制定学习计划、整理知识或推荐资源。"
    else:
        prompt = user_input  # 通用需求，直接让 GPT 处理

    # 调用 GPT 模型生成回答
    response = openai.ChatCompletion.create(
        model="gpt-4o",  # 也可以用 gpt-3.5-turbo，前者效果更好
        messages=[{"role": "user", "content": prompt}]
    )

    # 展示回答
    st.write(response.choices[0].message.content)
