import streamlit as st
from openai import OpenAI
import os

# --------------------------- 页面基础配置 ---------------------------
st.set_page_config(
    page_title="营销全能Agent",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------- 侧边栏直接缩小 50%（你要的效果）-------------------
st.markdown("""
<style>
/* 整体样式 */
.block-container { padding-top: 1.5rem; max-width: 90rem; }
.main { background-color: #ffffff; }

/* 🔥 侧边栏缩小 50% 核心 */
section[data-testid="stSidebar"] { 
    width: 220px !important; 
    min-width: 220px !important;
    max-width: 220px !important;
}
.sidebar .sidebar-content { 
    background-color: #f8f9fa; 
    padding: 0.6rem 0.4rem;
    border-right: 1px solid #e5e7eb;
    font-size: 0.8rem;
}

/* 标题变小 */
.sidebar h1 {
    font-size: 1.1rem !important;
    margin: 0.3rem 0 !important;
}
.sidebar h2, .sidebar h3, .sidebar h4 {
    font-size: 0.85rem !important;
    margin: 0.3rem 0 !important;
}

/* 聊天框 */
.stChatMessage { 
    padding: 1rem; 
    border-radius: 8px;
    margin-bottom: 0.8rem;
}
/* 按钮统一风格 */
.stButton>button { 
    background-color: #007bff; 
    color: white;
    border: none;
    border-radius: 6px;
    padding: 0.3rem 0.6rem;
    font-size: 0.75rem;
}
.stButton>button:hover { background-color: #0056b3; }
/* 输入框变小 */
.stTextInput>div>div>input, 
.stTextArea>div>div>textarea {
    font-size: 0.75rem !important;
    padding: 0.3rem 0.4rem !important;
}
.stChatInput>div>div>input { 
    font-size: 0.9rem;
    border-radius: 6px; 
}

/* Token 小字 */
.token-info {
    font-size: 0.7rem;
    color: #6c757d;
    padding: 0.4rem;
    margin-top: 0.5rem;
    border-top: 1px solid #e5e7eb;
    line-height: 1.2;
}
</style>
""", unsafe_allow_html=True)

# --------------------------- 模型客户端配置 ---------------------------
def init_clients():
    doubao_api_key = st.secrets.get("DOUBAO_API_KEY", os.getenv("DOUBAO_API_KEY"))
    deepseek_api_key = st.secrets.get("DEEPSEEK_API_KEY", os.getenv("DEEPSEEK_API_KEY"))
    
    doubao_client = OpenAI(
        api_key=doubao_api_key,
        base_url="https://ark.cn-beijing.volces.com/api/v3"
    )
    deepseek_client = OpenAI(
        api_key=deepseek_api_key,
        base_url="https://api.deepseek.com/v1"
    )
    return doubao_client, deepseek_client

# --------------------------- Token 余量显示 ---------------------------
def get_token_usage():
    return {
        "doubao": {"remaining": 100000, "total": 100000, "percent": 100},
        "deepseek": {"remaining": 85000, "total": 100000, "percent": 85}
    }

# --------------------------- 初始化 ---------------------------
if "personas" not in st.session_state:
    st.session_state.personas = {
        "全能营销专家": """你是4A广告公司资深品牌营销专家，专业、高效、可直接用于方案。""",
        "策略总监": """你擅长策略推导、SWOT、定位、传播节奏、逻辑严谨。""",
        "创意总监": """你输出slogan、创意、海报、视频、热点借势。""",
        "资深文案": """你擅长多平台文案、标题、风格切换。"""
    }

if "messages" not in st.session_state:
    st.session_state.messages = []

if "new_persona_name" not in st.session_state:
    st.session_state.new_persona_name = ""

# --------------------------- 侧边栏 ---------------------------
with st.sidebar:
    st.title("🧠 营销Agent")
    st.divider()

    st.subheader("🔍 角色")
    selected_persona = st.radio(
        "", list(st.session_state.personas.keys()), label_visibility="collapsed"
    )
    st.divider()

    st.subheader("✏️ 编辑")
    edited_prompt = st.text_area(
        "", st.session_state.personas[selected_persona],
        height=140, label_visibility="collapsed"
    )
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 保存"):
            st.session_state.personas[selected_persona] = edited_prompt
            st.success("已保存")
    with col2:
        if st.button("🗑️ 删除"):
            if len(st.session_state.personas) > 1:
                del st.session_state.personas[selected_persona]
                st.success("已删除")
            else:
                st.warning("至少保留1个")
    st.divider()

    st.subheader("➕ 新增")
    st.session_state.new_persona_name = st.text_input(
        "", placeholder="角色名", label_visibility="collapsed"
    )
    new_prompt = st.text_area(
        "", placeholder="规则", height=70, label_visibility="collapsed"
    )
    if st.button("✅ 添加"):
        if st.session_state.new_persona_name.strip() and new_prompt.strip():
            if st.session_state.new_persona_name not in st.session_state.personas:
                st.session_state.personas[st.session_state.new_persona_name] = new_prompt
                st.success("已添加")
                st.session_state.new_persona_name = ""
            else:
                st.warning("已存在")
        else:
            st.warning("不能为空")

    # Token 显示
    token = get_token_usage()
    st.markdown(f"""
    <div class="token-info">
        豆包 {token['doubao']['remaining']}（{token['doubao']['percent']}%）<br>
        DeepSeek {token['deepseek']['remaining']}（{token['deepseek']['percent']}%）
    </div>
    """, unsafe_allow_html=True)

# --------------------------- 主界面 ---------------------------
st.title("💬 营销智能助手")
st.caption("豆包 + DeepSeek 双模")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

doubao_client, deepseek_client = init_clients()

user_prompt = st.chat_input("输入需求...")

if user_prompt:
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    strategy_words = ["策略","分析","简报","拆解","SWOT","定位","预算","KPI","竞品","全案","框架"]
    use_deepseek = any(w in user_prompt for w in strategy_words)

    system = f"{st.session_state.personas[selected_persona]}\n需求：{user_prompt}"
    messages = [{"role":"system","content":system}, *st.session_state.messages]

    with st.chat_message("assistant"):
        with st.spinner("生成中..."):
            try:
                if use_deepseek:
                    res = deepseek_client.chat.completions.create(
                        model="deepseek-chat", messages=messages, temperature=0.7, max_tokens=4000
                    )
                else:
                    res = doubao_client.chat.completions.create(
                        model="doubao", messages=messages, temperature=0.7, max_tokens=4000
                    )
                reply = res.choices[0].message.content
                st.markdown(reply)
                st.session_state.messages.append({"role":"assistant","content":reply})
            except Exception as e:
                st.error(f"错误：{str(e)[:200]}")
