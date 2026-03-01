import streamlit as st
from openai import OpenAI
import os

# --------------------------- 页面配置 ---------------------------
st.set_page_config(
    page_title="Agent",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化外观设置
if "app_settings" not in st.session_state:
    st.session_state.app_settings = {
        "bg_color": "#ffffff",
        "font_size": 14,
        "font_color": "#1D2129"
    }

# 初始化会话列表
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {"默认会话": []}
if "current_session" not in st.session_state:
    st.session_state.current_session = "默认会话"

# 初始化人设
if "personas" not in st.session_state:
    st.session_state.personas = {
        "全能营销专家": """你是资深品牌营销专家，输出专业、可直接用于方案、PPT。""",
        "策略总监": """你擅长策略拆解、SWOT、用户分析、传播节奏。""",
        "创意总监": """擅长Slogan、创意方向、热点借势。""",
        "资深文案": """擅长小红书/抖音/公众号标题与文案。"""
    }

if "new_persona_name" not in st.session_state:
    st.session_state.new_persona_name = ""

# 应用样式
st.markdown(f"""
<style>
.stApp {{
    background-color: {st.session_state.app_settings['bg_color']} !important;
}}
html, body, [class*="css"] {{
    font-size: {st.session_state.app_settings['font_size']}px !important;
    color: {st.session_state.app_settings['font_color']} !important;
}}

/* 超窄侧边栏 */
section[data-testid="stSidebar"] {{ 
    width: 220px !important; 
    min-width: 220px !important;
    max-width: 220px !important;
}}
.sidebar .sidebar-content {{ 
    background-color: #f8f9fa; 
    padding: 0.6rem 0.4rem;
    border-right: 1px solid #e5e7eb;
    font-size: 0.8rem;
}}
.sidebar h1 {{ font-size: 1.1rem !important; margin: 0.3rem 0 !important; }}
.sidebar h2 {{ font-size: 0.85rem !important; margin: 0.3rem 0 !important; }}

.stButton>button {{ 
    padding: 0.3rem 0.6rem;
    font-size: 0.75rem;
}}
.stTextInput>div>div>input, .stTextArea>div>div>textarea {{
    font-size: 0.75rem !important;
    padding: 0.3rem 0.4rem !important;
}}

/* 会话样式 */
.session-item {{
    padding: 4px 6px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.75rem;
}}
.session-item:hover {{
    background: #e9ecef;
}}

/* Token样式 */
.token-info {{
    font-size: 0.7rem;
    color: #6c757d;
    padding: 0.4rem;
    border-top: 1px solid #e5e7eb;
    line-height: 1.2;
}}

.block-container {{ padding-top: 1.5rem; max-width: 90rem; }}
.stChatMessage {{ padding: 1rem; border-radius: 8px; margin-bottom: 0.8rem; }}
</style>
""", unsafe_allow_html=True)

# --------------------------- 双模型客户端 ---------------------------
def get_client(model_name):
    if model_name == "豆包":
        api_key = st.secrets.get("DOUBAO_API_KEY") or os.getenv("DOUBAO_API_KEY")
        return OpenAI(api_key=api_key, base_url="https://ark.cn-beijing.volces.com/api/v3"), "doubao-seed-2-0-pro-260215"
    elif model_name == "DeepSeek":
        api_key = st.secrets.get("DEEPSEEK_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
        return OpenAI(api_key=api_key, base_url="https://api.deepseek.com"), "deepseek-chat"

# --------------------------- 侧边栏 ---------------------------
with st.sidebar:
    st.title("🧠 营销Agent")
    st.divider()

    # 模型选择
    st.subheader("🤖 模型")
    model_choice = st.radio("", ["豆包", "DeepSeek"], label_visibility="collapsed")
    st.divider()

    # 历史会话
    st.subheader("💬 历史会话")
    session_names = list(st.session_state.chat_sessions.keys())
    for name in session_names:
        if st.button(f"📝 {name}", key=f"ses_{name}", use_container_width=True):
            st.session_state.current_session = name
            st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ 新建"):
            new_name = f"会话_{len(session_names)+1}"
            st.session_state.chat_sessions[new_name] = []
            st.session_state.current_session = new_name
            st.rerun()
    with col2:
        if st.button("🗑 删除"):
            if len(st.session_state.chat_sessions) > 1:
                del st.session_state.chat_sessions[st.session_state.current_session]
                st.session_state.current_session = list(st.session_state.chat_sessions.keys())[0]
                st.rerun()
    st.divider()

    # 设置
    with st.expander("⚙️ 设置", expanded=False):
        st.subheader("角色人设")
        selected_persona = st.radio("", list(st.session_state.personas.keys()), label_visibility="collapsed")

        st.subheader("编辑角色")
        edited = st.text_area("", st.session_state.personas[selected_persona], height=100, label_visibility="collapsed")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("💾 保存"):
                st.session_state.personas[selected_persona] = edited
                st.success("已保存")
        with c2:
            if st.button("🗑 删角色"):
                if len(st.session_state.personas) > 1:
                    del st.session_state.personas[selected_persona]
                    st.rerun()

        st.subheader("新增角色")
        pname = st.text_input("", placeholder="角色名", label_visibility="collapsed")
        pprompt = st.text_area("", placeholder="规则", height=60, label_visibility="collapsed")
        if st.button("✅ 添加"):
            if pname.strip() and pprompt.strip():
                st.session_state.personas[pname] = pprompt
                st.rerun()

        st.divider()
        st.subheader("外观")
        bg = st.color_picker("背景", st.session_state.app_settings["bg_color"])
        fs = st.slider("字号", 12, 22, st.session_state.app_settings["font_size"])
        fc = st.color_picker("字体颜色", st.session_state.app_settings["font_color"])
        if st.button("✅ 应用外观"):
            st.session_state.app_settings["bg_color"] = bg
            st.session_state.app_settings["font_size"] = fs
            st.session_state.app_settings["font_color"] = fc
            st.rerun()

    st.divider()

    # 双TOKEN显示
    st.markdown("""<div class="token-info">
📊 豆包: 100000/100000 (100%)<br>
📊 DeepSeek: 100000/100000 (100%)
</div>""", unsafe_allow_html=True)

# --------------------------- 主聊天区 ---------------------------
st.title(f"💬 {st.session_state.current_session}")
st.caption(f"模型：{model_choice}｜角色：{selected_persona}")

messages = st.session_state.chat_sessions[st.session_state.current_session]
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("输入需求...")

if prompt:
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    client, model = get_client(model_choice)
    system_prompt = st.session_state.personas[selected_persona]

    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            res = client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": system_prompt}, *messages],
                temperature=0.7
            )
            reply = res.choices[0].message.content
            st.markdown(reply)

    messages.append({"role": "assistant", "content": reply})
