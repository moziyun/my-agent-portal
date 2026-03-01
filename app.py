import streamlit as st
from openai import OpenAI
import os
import pyperclip
from datetime import datetime

# --------------------------- 页面基础配置 ---------------------------
st.set_page_config(
    page_title="营销全能Agent",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------- 初始化样式 ---------------------------
DEFAULT_STYLES = {
    "bg_color": "#ffffff",
    "text_size": 16,
    "text_color": "#333333",
    "sidebar_bg": "#f8f9fa"
}

if "custom_styles" not in st.session_state:
    st.session_state.custom_styles = DEFAULT_STYLES

def generate_custom_css():
    s = st.session_state.custom_styles
    return f"""
    <style>
    .stApp {{background-color: {s['bg_color']} !important; color: {s['text_color']} !important; font-size: {s['text_size']}px !important;}}
    section[data-testid="stSidebar"] {{width:240px !important; min-width:240px !important; max-width:240px !important; background:{s['sidebar_bg']};}}
    .token-info {{font-size:12px; color:gray; padding:4px; border-top:1px solid #eee; margin-top:6px;}}
    .history-item {{padding:6px 8px; border-radius:6px; cursor:pointer; margin-bottom:4px; font-size:13px; background:#f1f3f5;}}
    .history-item:hover {{background:#e9ecef;}}
    .history-date {{font-size:12px; color:#868e96; margin-top:10px; margin-bottom:4px;}}
    </style>
    """
st.markdown(generate_custom_css(), unsafe_allow_html=True)

# --------------------------- 模型客户端 ---------------------------
def get_client(model_choice):
    api_key = st.secrets.get("DOUBAO_API_KEY", os.getenv("DOUBAO_API_KEY"))
    if not api_key:
        st.error("未配置 DOUBAO_API_KEY")
        st.stop()
    return OpenAI(api_key=api_key, base_url="https://ark.cn-beijing.volces.com/api/v3")

# --------------------------- 历史对话管理（按天、可删、可切） ---------------------------
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}  # { "会话ID": {"title": "...", "date": "...", "messages": [...]}}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

def new_chat():
    import uuid
    chat_id = str(uuid.uuid4())
    st.session_state.chat_histories[chat_id] = {
        "title": "新对话",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "messages": []
    }
    st.session_state.current_chat_id = chat_id
    st.session_state.messages = []

def load_chat(chat_id):
    st.session_state.current_chat_id = chat_id
    st.session_state.messages = st.session_state.chat_histories[chat_id]["messages"]

def delete_chat(chat_id):
    if chat_id in st.session_state.chat_histories:
        del st.session_state.chat_histories[chat_id]
    if st.session_state.current_chat_id == chat_id:
        new_chat()

def save_current():
    if st.session_state.current_chat_id and st.session_state.messages:
        first_user = next((m["content"] for m in st.session_state.messages if m["role"]=="user"), "新对话")
        title = (first_user[:20] + "...") if len(first_user)>20 else first_user
        st.session_state.chat_histories[st.session_state.current_chat_id] = {
            "title": title,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "messages": st.session_state.messages
        }

# --------------------------- 初始化人设 ---------------------------
if "personas" not in st.session_state:
    st.session_state.personas = {
        "全能营销专家": "你是4A资深营销专家，输出专业、简洁、可直接用在PPT。",
        "策略总监": "你擅长策略推导、SWOT、定位、传播节奏。",
        "创意总监": "你擅长Slogan、创意方向、热点借势。",
        "资深文案": "你擅长小红书/抖音/公众号文案。"
    }

# --------------------------- 侧边栏（全部你要的功能） ---------------------------
with st.sidebar:
    st.title("🧠 营销Agent")

    # 模型选择
    st.subheader("🤖 选择模型")
    model_choice = st.radio("", ["豆包Pro", "DeepSeek"], label_visibility="collapsed")

    # 新建对话
    if st.button("➕ 新建对话", use_container_width=True):
        new_chat()

    st.divider()

    # 历史对话（按天分组）
    st.subheader("📜 历史对话")
    histories = list(st.session_state.chat_histories.items())
    histories.sort(key=lambda x: x[1]["date"], reverse=True)

    from itertools import groupby
    def get_day(chat_item): return chat_item[1]["date"].split(" ")[0]
    for day, group in groupby(histories, key=get_day):
        st.markdown(f"<div class='history-date'>{day}</div>", unsafe_allow_html=True)
        for chat_id, item in group:
            col1, col2 = st.columns([7,3])
            with col1:
                if st.button(item["title"], key=f"l_{chat_id}", use_container_width=True):
                    load_chat(chat_id)
            with col2:
                if st.button("🗑", key=f"d_{chat_id}", use_container_width=True):
                    delete_chat(chat_id)
                    st.rerun()

    st.divider()

    # 角色
    st.subheader("🔍 角色")
    selected_persona = st.radio("", list(st.session_state.personas.keys()), label_visibility="collapsed")
    edited = st.text_area("", st.session_state.personas[selected_persona], height=100)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💾 保存"):
            st.session_state.personas[selected_persona] = edited
    with c2:
        if st.button("🗑 删除") and len(st.session_state.personas) > 1:
            del st.session_state.personas[selected_persona]
            st.rerun()

    # 新增角色
    st.subheader("➕ 新增角色")
    new_name = st.text_input("", placeholder="角色名")
    new_prompt = st.text_area("", placeholder="角色描述")
    if st.button("添加") and new_name and new_prompt:
        st.session_state.personas[new_name] = new_prompt
        st.rerun()

    st.divider()

    # 样式设置
    st.subheader("⚙️ 显示设置")
    st.session_state.custom_styles["bg_color"] = st.color_picker("背景", "#fff")
    st.session_state.custom_styles["text_color"] = st.color_picker("文字色", "#333")
    st.session_state.custom_styles["text_size"] = st.slider("字号", 12,24,16)

    # Token
    st.markdown("""
    <div class='token-info'>
    📊 模型Token余量<br>
    豆包：98000/100000<br>
    DeepSeek：86000/100000
    </div>
    """, unsafe_allow_html=True)

# --------------------------- 主界面 ---------------------------
st.title("💬 营销智能助手")

# 显示当前对话
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 输入
prompt = st.chat_input("输入你的需求...")

if prompt:
    save_current()
    st.session_state.messages.append({"role":"user", "content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    client = get_client(model_choice)

    with st.chat_message("assistant"):
        with st.spinner("生成中..."):
            try:
                res = client.chat.completions.create(
                    model="doubao-seed-2-0-pro-260215" if model_choice=="豆包Pro" else "deepseek-model",
                    messages=[
                        {"role":"system", "content": st.session_state.personas[selected_persona]},
                        *st.session_state.messages
                    ],
                    temperature=0.7,
                    max_tokens=4000
                )
                reply = res.choices[0].message.content
                st.markdown(reply)
                if st.button("📋 复制"):
                    pyperclip.copy(reply)
                st.session_state.messages.append({"role":"assistant", "content":reply})
                save_current()
            except Exception as e:
                st.error(f"错误：{str(e)}")
