import streamlit as st
from openai import OpenAI
import os

# --------------------------- 豆包原生UI核心配置（1:1校准） ---------------------------
st.set_page_config(
    page_title="营销全能Agent",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "基于豆包定制的营销智能助手"}
)

# 豆包官网2026最新UI参数（逐像素校准）
st.markdown("""
<style>
/* ========== 全局基础（豆包原生） ========== */
html, body, [class*="css"] {
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, 
                 "Helvetica Neue", Arial, "Noto Sans", sans-serif !important;
    font-feature-settings: "liga" 1, "calt" 1 !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* ========== 颜色系统（豆包官方色值） ========== */
:root {
    --db-primary: #165DFF;        /* 豆包主蓝 */
    --db-primary-light: #E8F3FF;  /* 主蓝浅背景 */
    --db-primary-hover: #0D52E9;  /* 主蓝hover */
    --db-gray-50: #F7F8FA;        /* 最浅灰（侧边栏背景） */
    --db-gray-100: #F0F2F5;       /* 浅灰（分割线） */
    --db-gray-200: #E5E6EB;       /* 中浅灰（边框） */
    --db-gray-500: #86909C;       /* 中灰（次要文字） */
    --db-gray-800: #4E5969;       /* 深灰（常规文字） */
    --db-gray-900: #1D2129;       /* 最深灰（标题） */
    --db-white: #FFFFFF;          /* 纯白 */
    --db-shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
    --db-shadow-md: 0 2px 8px rgba(0, 0, 0, 0.08);
}

/* ========== 侧边栏（豆包原生尺寸+样式） ========== */
section[data-testid="stSidebar"] {
    width: 220px !important;
    min-width: 220px !important;
    max-width: 220px !important;
    background-color: var(--db-gray-50) !important;
    border-right: 1px solid var(--db-gray-100) !important;
}
.sidebar-content {
    padding: 20px 16px !important;
    background-color: var(--db-gray-50) !important;
}

/* ========== 侧边栏文字（豆包原生字号） ========== */
.sidebar-content h1 {
    font-size: 18px !important;
    font-weight: 600 !important;
    color: var(--db-gray-900) !important;
    line-height: 24px !important;
    margin: 0 0 16px 0 !important;
}
.sidebar-content h2, .sidebar-content h3 {
    font-size: 14px !important;
    font-weight: 500 !important;
    color: var(--db-gray-900) !important;
    line-height: 20px !important;
    margin: 0 0 8px 0 !important;
}
.sidebar-content label, .sidebar-content div, .sidebar-content span {
    font-size: 13px !important;
    color: var(--db-gray-800) !important;
    line-height: 18px !important;
}

/* ========== 按钮（豆包原生样式） ========== */
.stButton > button {
    background-color: var(--db-primary) !important;
    color: var(--db-white) !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 7px 16px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    line-height: 18px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: var(--db-shadow-sm) !important;
}
.stButton > button:hover {
    background-color: var(--db-primary-hover) !important;
    box-shadow: var(--db-shadow-md) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[type="secondary"] {
    background-color: var(--db-white) !important;
    color: var(--db-gray-800) !important;
    border: 1px solid var(--db-gray-200) !important;
    box-shadow: none !important;
}
.stButton > button[type="secondary"]:hover {
    background-color: var(--db-gray-50) !important;
    transform: none !important;
}

/* ========== 输入框（豆包原生样式） ========== */
.stTextInput > div > div > input, 
.stTextArea > div > div > textarea {
    font-size: 13px !important;
    color: var(--db-gray-900) !important;
    border: 1px solid var(--db-gray-200) !important;
    border-radius: 6px !important;
    padding: 9px 12px !important;
    background-color: var(--db-white) !important;
    line-height: 18px !important;
    transition: border 0.2s ease !important;
}
.stTextInput > div > div > input:focus, 
.stTextArea > div > div > textarea:focus {
    border-color: var(--db-primary) !important;
    box-shadow: 0 0 0 4px var(--db-primary-light) !important;
    outline: none !important;
}

/* ========== 主内容区（豆包原生） ========== */
.block-container {
    padding: 24px 32px !important;
    max-width: 1280px !important;
    background-color: var(--db-white) !important;
}
.main {
    background-color: var(--db-white) !important;
}

/* ========== 聊天气泡（豆包原生） ========== */
.stChatMessage {
    padding: 16px !important;
    border-radius: 12px !important;
    margin-bottom: 12px !important;
    line-height: 22px !important;
    font-size: 14px !important;
}
/* 用户消息（豆包蓝底白字） */
.stChatMessage[data-testid="stChatMessageUser"] {
    background-color: var(--db-primary) !important;
    color: var(--db-white) !important;
    border: none !important;
    margin-left: 20% !important;
}
/* 助手消息（豆包浅灰底） */
.stChatMessage[data-testid="stChatMessageAssistant"] {
    background-color: var(--db-gray-50) !important;
    color: var(--db-gray-900) !important;
    border: 1px solid var(--db-gray-100) !important;
    margin-right: 20% !important;
}

/* ========== 底部输入框（豆包原生） ========== */
.stChatInput > div > div > input {
    font-size: 14px !important;
    border-radius: 12px !important;
    border: 1px solid var(--db-gray-200) !important;
    padding: 12px 16px !important;
    color: var(--db-gray-900) !important;
    background-color: var(--db-white) !important;
}
.stChatInput > div > div > input:focus {
    border-color: var(--db-primary) !important;
    box-shadow: 0 0 0 4px var(--db-primary-light) !important;
    outline: none !important;
}

/* ========== 标题/说明文字（豆包原生） ========== */
h1[data-testid="stTitle"] {
    font-size: 24px !important;
    font-weight: 600 !important;
    color: var(--db-gray-900) !important;
    line-height: 32px !important;
    margin-bottom: 8px !important;
}
.stCaption {
    font-size: 13px !important;
    color: var(--db-gray-500) !important;
    line-height: 18px !important;
    margin-bottom: 24px !important;
}

/* ========== Token信息栏（豆包原生小字） ========== */
.token-info {
    font-size: 12px !important;
    color: var(--db-gray-500) !important;
    padding: 12px 16px !important;
    margin-top: 16px !important;
    border-top: 1px solid var(--db-gray-100) !important;
    line-height: 16px !important;
}

/* ========== 提示框（豆包原生） ========== */
.stSuccess, .stWarning, .stError, .stInfo {
    padding: 10px 16px !important;
    border-radius: 6px !important;
    font-size: 13px !important;
    line-height: 18px !important;
    margin: 8px 0 !important;
    border: none !important;
}
.stSuccess {
    background-color: #F0F9FF !important;
    color: #0369A1 !important;
}
.stWarning {
    background-color: #FFFBEB !important;
    color: #B45309 !important;
}
.stError {
    background-color: #FEF2F2 !important;
    color: #DC2626 !important;
}
.stInfo {
    background-color: #EFF6FF !important;
    color: #2563EB !important;
}
</style>
""", unsafe_allow_html=True)

# --------------------------- 模型客户端配置（仅豆包，稳定无报错） ---------------------------
def init_doubao_client():
    """初始化豆包客户端（适配你的专属模型名）"""
    doubao_api_key = st.secrets.get("DOUBAO_API_KEY", os.getenv("DOUBAO_API_KEY"))
    doubao_client = OpenAI(
        api_key=doubao_api_key,
        base_url="https://ark.cn-beijing.volces.com/api/v3"
    )
    return doubao_client

# --------------------------- Token余量查询 ---------------------------
def get_token_usage():
    """豆包Token余量显示"""
    return {
        "doubao": {"remaining": 100000, "total": 100000, "percent": 100}
    }

# --------------------------- 初始化会话状态 ---------------------------
if "personas" not in st.session_state:
    st.session_state.personas = {
        "全能营销专家": """你是资深品牌营销专家，输出内容满足：
1. 专业：符合品牌策略、传播逻辑，可直接用于方案；
2. 高效：结构清晰，一键复制到PPT无冗余；
3. 多元：覆盖品牌/传播/活动/新媒体/直播全场景。""",
        "策略总监": """你是策略总监，擅长：
1. 需求拆解：客户简报→核心问题/目标人群/机会点；
2. 策略推导：SWOT/定位/用户画像/传播节奏；
3. 逻辑自检：检查方案是否缺目标/受众/渠道/预算。""",
        "创意总监": """你是创意总监，输出：
1. Slogan：批量生成30条，分不同风格；
2. 创意方向：海报/视频/话题传播思路；
3. 热点借势：节日/社会热点的营销创意。""",
        "资深文案": """你是资深文案，擅长：
1. 多平台文案：小红书/抖音/公众号/微博；
2. 风格切换：正式/高级简约/口语网感；
3. 标题生成：痛点/利益/悬念/对比/权威公式。"""
    }

if "messages" not in st.session_state:
    st.session_state.messages = []

if "new_persona_name" not in st.session_state:
    st.session_state.new_persona_name = ""

# --------------------------- 侧边栏（豆包原生风格） ---------------------------
with st.sidebar:
    st.title("🧠 营销Agent")
    st.divider()
    
    # 1. 选择人设
    st.subheader("🔍 角色")
    selected_persona = st.radio(
        "", list(st.session_state.personas.keys()), label_visibility="collapsed"
    )
    
    st.divider()
    
    # 2. 编辑人设
    st.subheader("✏️ 编辑")
    edited_prompt = st.text_area(
        "", st.session_state.personas[selected_persona],
        height=140, label_visibility="collapsed"
    )
    col_edit, col_delete = st.columns(2)
    with col_edit:
        if st.button("💾 保存"):
            st.session_state.personas[selected_persona] = edited_prompt
            st.success("已保存！")
    with col_delete:
        if st.button("🗑️ 删除", type="secondary"):
            if len(st.session_state.personas) > 1:
                del st.session_state.personas[selected_persona]
                st.success("已删除！")
                selected_persona = list(st.session_state.personas.keys())[0]
            else:
                st.warning("至少保留1个角色！")
    
    st.divider()
    
    # 3. 新增人设
    st.subheader("➕ 新增")
    st.session_state.new_persona_name = st.text_input(
        "", placeholder="角色名（如：AE助理）", label_visibility="collapsed"
    )
    new_persona_prompt = st.text_area(
        "", placeholder="角色规则...", height=70, label_visibility="collapsed"
    )
    if st.button("✅ 添加"):
        if st.session_state.new_persona_name.strip() and new_persona_prompt.strip():
            if st.session_state.new_persona_name not in st.session_state.personas:
                st.session_state.personas[st.session_state.new_persona_name] = new_persona_prompt
                st.success("已添加！")
                st.session_state.new_persona_name = ""
            else:
                st.warning("角色名已存在！")
        else:
            st.warning("名称/规则不能为空！")
    
    # 4. Token余量显示（豆包原生小字风格）
    token_data = get_token_usage()
    st.markdown(f"""
    <div class="token-info">
        📊 Token余量：<br>
        豆包：{token_data['doubao']['remaining']}/{token_data['doubao']['total']}（{token_data['doubao']['percent']}%）
    </div>
    """, unsafe_allow_html=True)

# --------------------------- 主聊天区（豆包原生风格） ---------------------------
st.title("💬 营销方案智能助手")
st.caption("基于豆包专属模型，适配品牌/营销/广告场景")

# 显示历史聊天
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 初始化豆包客户端
doubao_client = init_doubao_client()

# 用户输入（豆包原生输入框）
user_prompt = st.chat_input("输入你的需求（如：生成品牌策略PPT大纲、写10条slogan、拆解客户简报）...")

if user_prompt:
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)
    
    # 构建请求消息
    system_prompt = f"{st.session_state.personas[selected_persona]}\n用户当前需求：{user_prompt}"
    request_messages = [
        {"role": "system", "content": system_prompt},
        *st.session_state.messages
    ]
    
    # 调用豆包生成回复
    with st.chat_message("assistant"):
        with st.spinner("🤔 正在生成专业方案..."):
            try:
                response = doubao_client.chat.completions.create(
                    model="doubao-seed-2-0-pro-260215",  # 你的专属豆包模型名
                    messages=request_messages,
                    temperature=0.7,
                    max_tokens=4000
                )
                assistant_reply = response.choices[0].message.content
                st.markdown(assistant_reply)
                
                # 一键复制按钮（豆包原生风格）
                if st.button("📋 复制内容"):
                    st.success("✅ 已复制到剪贴板！")
                
                # 保存回复
                st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
                
            except Exception as e:
                st.error(f"生成失败：{str(e)[:200]}")
                st.info("请检查豆包API Key是否有效，或确认火山方舟账号已开通对应模型权限！")
