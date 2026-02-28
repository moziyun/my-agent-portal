import streamlit as st
from openai import OpenAI

# 配置蚂蚁 Ling Studio（国内可访问，无地域限制）
client = OpenAI(
    api_key=st.secrets["LING_API_KEY"],  # 读取 Streamlit 配置的密钥
    base_url="https://lingstudio.antgroup.com/v1"  # 蚂蚁 Ling 的固定接口地址
)

# 页面标题
st.title("我的全能 Agent 入口")

# 聊天输入框
user_input = st.chat_input("请输入需求（如抖音选题、UI 设计灵感、知识整理...）")

if user_input:
    # 根据关键词匹配 Agent 角色
    if "抖音" in user_input or "自媒体" in user_input:
        prompt = f"你是抖音自媒体运营专家，专注 UI 设计垂类，帮我处理需求：{user_input}。要求输出3个具体选题+每个选题的文案框架+适合的UI设计风格参考。"
    elif "UI" in user_input or "设计" in user_input:
        prompt = f"你是资深 UI 设计师，帮我处理需求：{user_input}。要求给出具体的设计思路、配色方案、图标/字体资源链接、落地步骤。"
    elif "知识" in user_input or "学习" in user_input:
        prompt = f"你是知识管理教练，帮我处理需求：{user_input}。要求生成结构化的学习计划（含每日任务）、优质学习资源（课程/书籍/网站）、复盘方法。"
    else:
        prompt = user_input

    # 调用 AI 生成回答（兼容 OpenAI 格式）
    with st.spinner("AI 思考中..."):
        response = client.chat.completions.create(
            model="antgpt-4o",  # 蚂蚁 Ling 的免费模型，效果对标 GPT-4o
            messages=[{"role": "user", "content": prompt}]
        )
    # 展示结果
    st.write(response.choices[0].message.content)
