import streamlit as st
from openai import OpenAI
import os

# ------------------- 页面配置 -------------------
st.set_page_config(
    page_title="AI助手",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------- 豆包官方极简UI -------------------
st.markdown("""
<style>
/* 全局字体 */
* {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

/* 主色：豆包蓝 */
:root {
    --db-blue: #165DFF;
    --db-bg: #FFFFFF;
    --db-gray: #F5F7FA;
    --db-border: #E5E6EB;
    --db-text: #1D2129;
}

/* 整体背景 */
.stApp {
    background-color: white !important;
}

/* 侧边栏 */
section[data-testid="stSidebar"] {
    background-color: var(--db-gray) !important;
    width: 240px !important;
    border-right: 1px solid var(--db-border);
}

/* 聊天气泡 */
.stChatMessage {
    border-radius: 12px !important;
    padding: 14px 16px !important;
    font-size: 15px !important;
    line-height: 1.6 !important;
    margin-bottom: 12px !important;
    border: none !important;
}

/* 用户气泡：右对齐、蓝色 */
.stChatMessage:has(div[data-testid="chatAvatarIcon-user"]) {
    background-color: var(--db-blue) !important;
    color: white !important;
    margin-left: 60px !important;
}

/* AI气泡：左对齐、浅灰 */
.stChatMessage:has(div[data-testid="chatAvatarIcon-assistant"]) {
    background-color: var(--db-gray) !important;
    color: var(--db-text) !important;
    margin-right: 60px !important;
}

/* 输入框 */
.stChatInput div[data-baseweb="input"] {
    border-radius: 16px !important;
    border: 1px solid var(--db-border) !important;
}
.stChatInput input {
    font-size: 15px !important;
}

/* 按钮 */
.stButton button {
    background-color: var(--db-blue) !important;
    color: white !important;
    border-radius: 8px !important;
    border: none !important;
}

/* 隐藏streamlit自带多余样式 */
div[data-testid="stDecoration"],
#MainMenu, footer, header {
    display: none !important;
}

</style>
""", unsafe_allow_html=True)

# ------------------- 模型初始化 -------------------
def get_client():
    api_key = st.secrets.get("DOUBAO_API_KEY") or os.getenv("DOUBAO_API_KEY")
    return OpenAI(
        api_key=api_key,
        base_url="https://ark.cn-beijing.volces.com/api/v3"
    )

# ------------------- 角色人设 -------------------
if "personas" not in st.session_state:
    st.session_state.personas = {
        "营销专家": "你是专业营销助手，输出清晰、专业、可直接使用。",
        "文案写作": "你是资深文案，擅长标题、短文、推广语。",
        "策略规划": "你擅长策略梳理、逻辑清晰。",
    }

# ------------------- 侧边栏 -------------------
with st.sidebar:
    st.title("🧠 AI 助手")
    st.divider()

    st.subheader("选择角色")
    role = st.radio(
        "角色",
        list(st.session_state.personas.keys()),
        label_visibility="collapsed"
    )

    st.divider()
    st.caption("✅ 豆包原生界面")

# ------------------- 聊天主界面 -------------------
st.title("💬 智能对话")

# 初始化消息
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 输入
prompt = st.chat_input("输入你的问题...")

if prompt:
    # 显示用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 系统提示
    system_prompt = st.session_state.personas[role]

    # 调用
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            client = get_client()
            res = client.chat.completions.create(
                model="doubao-seed-2-0-pro-260215",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *st.session_state.messages
                ],
                temperature=0.7,
                max_tokens=4000
            )
            reply = res.choices[0].message.content
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
