import streamlit as st
from openai import OpenAI
import os
from datetime import datetime
import uuid

# ===================== 页面配置 =====================
st.set_page_config(
    page_title="营销全能Agent",
    layout="wide",
    initial_sidebar_state="auto"
)

# ===================== 初始化会话 =====================
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}

if "current_chat_id" not in st.session_state:
    cid = str(uuid.uuid4())
    st.session_state.chat_histories[cid] = {
        "title": "新对话",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "messages": []
    }
    st.session_state.current_chat_id = cid

if "messages" not in st.session_state:
    st.session_state.messages = []

if "personas" not in st.session_state:
    st.session_state.personas = {
        "全能营销专家": "你是4A资深营销专家，输出专业、简洁、可直接用于PPT。",
        "策略总监": "你擅长策略推导、SWOT、定位、传播节奏。",
        "创意总监": "你擅长Slogan、创意方向、热点借势。",
        "资深文案": "你擅长小红书/抖音/公众号文案。"
    }

# ===================== 界面样式设置 =====================
if "style_settings" not in st.session_state:
    st.session_state.style_settings = {
        "user_font_size": 14,
        "assistant_font_size": 14,
        "user_bg_color": "#e3f2fd",
        "assistant_bg_color": "#f5f5f5",
        "user_text_color": "#000000",
        "assistant_text_color": "#000000",
        "assistant_h1_size": 16,
        "assistant_h2_size": 14,
        "assistant_h3_size": 12
    }

# ===================== 应用自定义样式 =====================
style = st.session_state.style_settings
custom_css = f"""
<style>
/* 主标题字号调整为 18px，符合日常使用规范 */
h1[data-testid="stHeadingWithActionElements"] {{
    font-size: 18px !important;
    font-weight: 600 !important;
}}

/* 副标题字号调整 */
h2[data-testid="stHeadingWithActionElements"] {{
    font-size: 16px !important;
    font-weight: 500 !important;
}}

/* 侧边栏标题调整 */
.css-1d391kg {{
    font-size: 14px !important;
}}

/* 按钮文字大小调整 */
.stButton button {{
    font-size: 14px !important;
}}

/* 输入框文字大小调整 */
.stTextInput input, .stTextArea textarea {{
    font-size: 14px !important;
}}

/* 用户消息样式 */
[data-testid="stChatMessage"]:has([data-testid="chat-message-avatar-user"]) .stMarkdown {{
    font-size: {style['user_font_size']}px !important;
    color: {style['user_text_color']} !important;
}}

[data-testid="stChatMessage"]:has([data-testid="chat-message-avatar-user"]) {{
    background-color: {style['user_bg_color']} !important;
    border-radius: 8px !important;
}}

/* AI回答样式 */
[data-testid="stChatMessage"]:has([data-testid="chat-message-avatar-assistant"]) .stMarkdown {{
    font-size: {style['assistant_font_size']}px !important;
    color: {style['assistant_text_color']} !important;
}}

[data-testid="stChatMessage"]:has([data-testid="chat-message-avatar-assistant"]) {{
    background-color: {style['assistant_bg_color']} !important;
    border-radius: 8px !important;
}}

/* AI回答中的标题样式 */
[data-testid="stChatMessage"]:has([data-testid="chat-message-avatar-assistant"]) h1 {{
    font-size: {style['assistant_h1_size']}px !important;
    font-weight: 600 !important;
    margin: 10px 0 5px 0 !important;
}}

[data-testid="stChatMessage"]:has([data-testid="chat-message-avatar-assistant"]) h2 {{
    font-size: {style['assistant_h2_size']}px !important;
    font-weight: 500 !important;
    margin: 8px 0 4px 0 !important;
}}

[data-testid="stChatMessage"]:has([data-testid="chat-message-avatar-assistant"]) h3 {{
    font-size: {style['assistant_h3_size']}px !important;
    font-weight: 500 !important;
    margin: 6px 0 3px 0 !important;
}}

/* 侧边栏 radio 选项文字大小 */
div[data-testid="stRadio"] > label > div[data-testid="stMarkdownContainer"] > p {{
    font-size: 14px !important;
}}

/* caption 字号调整 */
.stCaption {{
    font-size: 12px !important;
}}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ===================== 对话操作 =====================
def new_chat():
    cid = str(uuid.uuid4())
    st.session_state.chat_histories[cid] = {
        "title": "新对话", "date": datetime.now().strftime("%Y-%m-%d %H:%M"), "messages": []
    }
    st.session_state.current_chat_id = cid
    st.session_state.messages = []
    st.rerun()

def load_chat(cid):
    st.session_state.current_chat_id = cid
    st.session_state.messages = st.session_state.chat_histories[cid]["messages"]
    st.rerun()

def delete_chat(cid):
    if cid in st.session_state.chat_histories:
        del st.session_state.chat_histories[cid]
    if st.session_state.current_chat_id == cid and st.session_state.chat_histories:
        st.session_state.current_chat_id = list(st.session_state.chat_histories.keys())[0]
        st.session_state.messages = st.session_state.chat_histories[st.session_state.current_chat_id]["messages"]
    else:
        new_chat()
    st.rerun()

def save_current():
    if not st.session_state.current_chat_id:
        return
    first_user = next((m["content"] for m in st.session_state.messages if m["role"] == "user"), "新对话")
    title = first_user[:20] + "..." if len(first_user) > 20 else first_user
    st.session_state.chat_histories[st.session_state.current_chat_id] = {
        "title": title,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "messages": st.session_state.messages
    }

# ===================== 模型客户端 =====================
def get_client(model):
    if model == "豆包Pro":
        api_key = st.secrets.get("DOUBAO_API_KEY", os.getenv("DOUBAO_API_KEY"))
        base_url = "https://ark.cn-beijing.volces.com/api/v3"
        model_name = "doubao-seed-2-0-pro-260215"
    else:
        api_key = st.secrets.get("DEEPSEEK_API_KEY", os.getenv("DEEPSEEK_API_KEY"))
        base_url = "https://api.deepseek.com/v1"
        model_name = "deepseek-chat"

    if not api_key:
        st.error(f"请配置 {model} API Key")
        st.stop()
    return OpenAI(api_key=api_key, base_url=base_url), model_name

# ===================== 侧边栏 =====================
with st.sidebar:
    st.title("🧠 营销Agent")

    # 模型选择
    st.subheader("模型选择")
    model_choice = st.radio("", ["豆包Pro", "DeepSeek"], label_visibility="collapsed")

    # 新建对话
    if st.button("➕ 新建对话", use_container_width=True):
        new_chat()

    st.divider()

    # 历史对话（按天）
    st.subheader("历史对话")
    histories = sorted(st.session_state.chat_histories.items(), key=lambda x: x[1]["date"], reverse=True)
    from itertools import groupby
    for day, group in groupby(histories, key=lambda x: x[1]["date"].split(" ")[0]):
        st.caption(day)
        for cid, item in group:
            col1, col2 = st.columns([7, 2])
            with col1:
                if st.button(item["title"], key=f"l_{cid}", use_container_width=True):
                    load_chat(cid)
            with col2:
                if st.button("🗑", key=f"d_{cid}", type="primary", use_container_width=True):
                    delete_chat(cid)

    st.divider()

    # 角色
    st.subheader("角色设定")
    selected = st.radio("", st.session_state.personas.keys(), label_visibility="collapsed")
    edited = st.text_area("角色提示词", st.session_state.personas[selected], height=120)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("💾 保存角色"):
            st.session_state.personas[selected] = edited
            st.success("已保存")
    with col_b:
        if st.button("🗑 删除角色") and len(st.session_state.personas) > 1:
            del st.session_state.personas[selected]
            st.rerun()

    # 新增角色
    new_name = st.text_input("角色名")
    new_prompt = st.text_area("角色描述", height=80)
    if st.button("➕ 添加角色") and new_name and new_prompt:
        st.session_state.personas[new_name] = new_prompt
        st.rerun()

    st.divider()

    # ===================== 界面设置 =====================
    st.subheader("🎨 界面设置")

    # 展开界面设置
    with st.expander("样式设置", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**用户消息样式**")
            user_font = st.slider("文字大小", 10, 24, st.session_state.style_settings["user_font_size"], key="user_font_size")
            user_bg = st.color_picker("背景色", st.session_state.style_settings["user_bg_color"], key="user_bg_color")
            user_text = st.color_picker("文字颜色", st.session_state.style_settings["user_text_color"], key="user_text_color")

        with col2:
            st.markdown("**AI回答样式**")
            assistant_font = st.slider("文字大小", 10, 24, st.session_state.style_settings["assistant_font_size"], key="assistant_font_size")
            assistant_bg = st.color_picker("背景色", st.session_state.style_settings["assistant_bg_color"], key="assistant_bg_color")
            assistant_text = st.color_picker("文字颜色", st.session_state.style_settings["assistant_text_color"], key="assistant_text_color")
            
            st.divider()
            st.markdown("**AI回答标题大小**")
            h1_size = st.slider("一级标题 (H1)", 12, 28, st.session_state.style_settings["assistant_h1_size"], key="h1_size")
            h2_size = st.slider("二级标题 (H2)", 10, 24, st.session_state.style_settings["assistant_h2_size"], key="h2_size")
            h3_size = st.slider("三级标题 (H3)", 10, 20, st.session_state.style_settings["assistant_h3_size"], key="h3_size")

        # 保存按钮
        if st.button("💾 应用设置", use_container_width=True):
            st.session_state.style_settings = {
                "user_font_size": user_font,
                "assistant_font_size": assistant_font,
                "user_bg_color": user_bg,
                "assistant_bg_color": assistant_bg,
                "user_text_color": user_text,
                "assistant_text_color": assistant_text,
                "assistant_h1_size": h1_size,
                "assistant_h2_size": h2_size,
                "assistant_h3_size": h3_size
            }
            st.success("样式已更新！")
            st.rerun()

    st.divider()
    # Token显示：增加百分比，格式更清晰
    st.caption("📊 模型额度")
    st.caption("豆包Pro：98000/100000（98%）")
    st.caption("DeepSeek：86000/100000（86%）")

# ===================== 主聊天区 =====================
st.title("💬 营销智能助手")

# 显示消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 输入
prompt = st.chat_input("请输入需求...")

if prompt:
    save_current()
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    client, model_name = get_client(model_choice)

    with st.chat_message("assistant"):
        with st.spinner("生成中..."):
            try:
                res = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": st.session_state.personas[selected]},
                        *st.session_state.messages
                    ],
                    temperature=0.7,
                    max_tokens=4000
                )
                reply = res.choices[0].message.content
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                save_current()
            except Exception as e:
                st.error(f"错误：{str(e)}")
