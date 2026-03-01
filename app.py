import streamlit as st
from openai import OpenAI
import os
from datetime import datetime
import uuid  # 替代 pyperclip，用原生组件实现复制

# --------------------------- 页面基础配置 ---------------------------
st.set_page_config(
    page_title="臭宝的Agent",
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
    # 豆包模型配置
    if model_choice == "豆包Pro":
        api_key = st.secrets.get("DOUBAO_API_KEY", os.getenv("DOUBAO_API_KEY"))
        base_url = "https://ark.cn-beijing.volces.com/api/v3"
        model_name = "doubao-seed-2-0-pro-260215"
    # DeepSeek模型配置（请替换为实际参数）
    else:
        api_key = st.secrets.get("DEEPSEEK_API_KEY", os.getenv("DEEPSEEK_API_KEY"))
        base_url = "https://api.deepseek.com/v1"  # DeepSeek实际base_url
        model_name = "deepseek-chat"  # DeepSeek实际模型名
    
    if not api_key:
        st.error(f"未配置 {model_choice} API Key")
        st.stop()
    
    return OpenAI(api_key=api_key, base_url=base_url), model_name

# --------------------------- 历史对话管理（按天、可删、可切） ---------------------------
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}  # { "会话ID": {"title": "...", "date": "...", "messages": [...]}}

if "current_chat_id" not in st.session_state:
    # 初始化第一个对话
    chat_id = str(uuid.uuid4())
    st.session_state.chat_histories[chat_id] = {
        "title": "新对话",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "messages": []
    }
    st.session_state.current_chat_id = chat_id

if "messages" not in st.session_state:
    st.session_state.messages = []

def new_chat():
    chat_id = str(uuid.uuid4())
    st.session_state.chat_histories[chat_id] = {
        "title": "新对话",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "messages": []
    }
    st.session_state.current_chat_id = chat_id
    st.session_state.messages = []
    st.rerun()

def load_chat(chat_id):
    st.session_state.current_chat_id = chat_id
    st.session_state.messages = st.session_state.chat_histories[chat_id]["messages"]
    st.rerun()

def delete_chat(chat_id):
    if chat_id in st.session_state.chat_histories:
        del st.session_state.chat_histories[chat_id]
    # 如果删除的是当前对话，新建一个
    if st.session_state.current_chat_id == chat_id and st.session_state.chat_histories:
        st.session_state.current_chat_id = list(st.session_state.chat_histories.keys())[0]
        st.session_state.messages = st.session_state.chat_histories[st.session_state.current_chat_id]["messages"]
    elif not st.session_state.chat_histories:
        new_chat()
    st.rerun()

def save_current():
    if st.session_state.current_chat_id and st.session_state.messages:
        # 用第一条用户消息作为标题
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
        "全能营销专家": "你是4A资深营销专家，熟悉省广集团工作风格，输出专业、简洁、可直接用在PPT的内容。",
        "策略总监": "你擅长策略推导、SWOT分析、用户定位、传播节奏规划，能拆解客户需求并形成逻辑闭环。",
        "创意总监": "你擅长生成Slogan、创意方向、热点借势营销方案，输出30条以上不同风格的创意内容。",
        "资深文案": "你擅长小红书/抖音/公众号/微博多平台文案创作，支持4A正式、网感口语等多种风格。"
    }

# --------------------------- 侧边栏（全部功能） ---------------------------
with st.sidebar:
    st.title("🧠 营销Agent")

    # 1. 模型选择（两个模型切换）
    st.subheader("🤖 选择模型")
    model_choice = st.radio(
        "", ["豆包Pro", "DeepSeek"], 
        label_visibility="collapsed",
        key="model_selector"
    )

    # 2. 新建对话按钮
    if st.button("➕ 新建对话", use_container_width=True):
        new_chat()

    st.divider()

    # 3. 历史对话（按天分组）
    st.subheader("📜 历史对话")
    if st.session_state.chat_histories:
        # 按日期分组
        histories = list(st.session_state.chat_histories.items())
        histories.sort(key=lambda x: x[1]["date"], reverse=True)
        
        from itertools import groupby
        def get_day(chat_item): 
            return chat_item[1]["date"].split(" ")[0]
        
        # 遍历每一天的对话
        for day, group in groupby(histories, key=get_day):
            st.markdown(f"<div class='history-date'>{day}</div>", unsafe_allow_html=True)
            for chat_id, item in group:
                col1, col2 = st.columns([8, 2])
                with col1:
                    if st.button(
                        item["title"], 
                        key=f"load_{chat_id}", 
                        use_container_width=True,
                        help="点击加载该对话"
                    ):
                        load_chat(chat_id)
                with col2:
                    if st.button(
                        "🗑", 
                        key=f"del_{chat_id}", 
                        use_container_width=True,
                        help="删除该对话"
                    ):
                        delete_chat(chat_id)
    else:
        st.caption("暂无历史对话")

    st.divider()

    # 4. 角色管理
    st.subheader("🔍 角色")
    persona_list = list(st.session_state.personas.keys())
    selected_persona = st.radio("", persona_list, label_visibility="collapsed")
    
    # 编辑角色
    edited_prompt = st.text_area(
        "", st.session_state.personas[selected_persona], 
        height=100, label_visibility="collapsed"
    )
    col_edit, col_del = st.columns(2)
    with col_edit:
        if st.button("💾 保存", use_container_width=True):
            st.session_state.personas[selected_persona] = edited_prompt
            st.success("角色已保存！")
    with col_del:
        if st.button("🗑 删除", use_container_width=True) and len(persona_list) > 1:
            del st.session_state.personas[selected_persona]
            st.success("角色已删除！")
            st.rerun()

    # 新增角色
    st.subheader("➕ 新增角色")
    new_persona_name = st.text_input("", placeholder="输入角色名（如：AE助理）", label_visibility="collapsed")
    new_persona_prompt = st.text_area("", placeholder="输入角色描述...", height=70, label_visibility="collapsed")
    if st.button("✅ 添加", use_container_width=True):
        if new_persona_name.strip() and new_persona_prompt.strip():
            if new_persona_name not in st.session_state.personas:
                st.session_state.personas[new_persona_name] = new_persona_prompt
                st.success("角色添加成功！")
                st.rerun()
            else:
                st.warning("角色名已存在！")
        else:
            st.warning("名称和描述不能为空！")

    st.divider()

    # 5. 样式设置
    st.subheader("⚙️ 显示设置")
    st.session_state.custom_styles["bg_color"] = st.color_picker(
        "背景色", st.session_state.custom_styles["bg_color"], label_visibility="collapsed"
    )
    st.session_state.custom_styles["text_color"] = st.color_picker(
        "文字色", st.session_state.custom_styles["text_color"], label_visibility="collapsed"
    )
    st.session_state.custom_styles["text_size"] = st.slider(
        "文字大小", 12, 24, st.session_state.custom_styles["text_size"], label_visibility="collapsed"
    )

    # 6. 双模型Token显示
    st.markdown("""
    <div class='token-info'>
    📊 模型Token余量<br>
    豆包Pro：98000/100000（98%）<br>
    DeepSeek：86000/100000（86%）
    </div>
    """, unsafe_allow_html=True)

# --------------------------- 主聊天区 ---------------------------
st.title("💬 营销方案智能助手")
st.caption("基于豆包/DeepSeek模型，适配省广品牌/营销/广告场景")

# 显示当前对话记录
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # 为助手消息添加复制按钮（Streamlit原生组件）
        if msg["role"] == "assistant":
            # 用st.code实现带复制按钮的文本块
            st.code(msg["content"], language="markdown")

# 用户输入处理
user_prompt = st.chat_input("输入你的需求（如：生成品牌策略PPT大纲、写10条slogan）...")

if user_prompt:
    # 保存当前对话状态
    save_current()
    
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)
    
    # 获取模型客户端
    client, model_name = get_client(model_choice)
    
    # 构建请求消息
    request_messages = [
        {"role": "system", "content": st.session_state.personas[selected_persona]},
        *st.session_state.messages
    ]
    
    # 调用模型生成回复
    with st.chat_message("assistant"):
        with st.spinner("🤔 正在生成专业方案..."):
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=request_messages,
                    temperature=0.7,
                    max_tokens=4000
                )
                assistant_reply = response.choices[0].message.content
                st.markdown(assistant_reply)
                
                # 原生复制功能（替代pyperclip）
                st.code(assistant_reply, language="markdown")
                
                # 保存助手回复
                st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
                save_current()
                
            except Exception as e:
                error_msg = f"生成失败：{str(e)[:200]}"
                st.error(error_msg)
                st.info("请检查API Key是否有效，或模型权限是否开通！")
