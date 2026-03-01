import streamlit as st
from openai import OpenAI
import os
from datetime import datetime
import uuid

# ===================== 页面配置 =====================
st.set_page_config(
    page_title="臭宝的Agent",
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
    st.caption("📊 模型额度")
    st.caption("豆包：98000/100000")
    st.caption("DeepSeek：86000/100000")

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
