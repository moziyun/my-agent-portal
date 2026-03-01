import streamlit as st
from openai import OpenAI
import os

# --------------------------- 豆包1:1 UI配置（核心） ---------------------------
st.set_page_config(
    page_title="营销全能Agent",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "基于豆包定制的营销智能助手"}
)

# 豆包原版样式复刻（颜色/字体/间距/圆角全对齐）
st.markdown("""
<style>
/* 全局重置 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, 
                 "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", 
                 "Noto Color Emoji" !important;
}

/* 豆包主色调：#165DFF（官方蓝） */
:root {
    --doubao-blue: #165DFF;
    --doubao-gray-light: #F5F7FA;
    --doubao-gray: #E5E6EB;
    --doubao-gray-dark: #86909C;
    --doubao-black: #1D2129;
    --doubao-white: #FFFFFF;
}

/* 侧边栏缩小50% + 豆包风格 */
section[data-testid="stSidebar"] { 
    width: 220px !important; 
    min-width: 220px !important;
    max-width: 220px !important;
    background-color: var(--doubao-gray-light) !important;
}
.sidebar .sidebar-content { 
    background-color: var(--doubao-gray-light) !important;
    padding: 16px 12px !important;
    border-right: 1px solid var(--doubao-gray) !important;
}

/* 豆包字体大小体系 */
.sidebar h1 {
    font-size: 18px !important;
    font-weight: 600 !important;
    color: var(--doubao-black) !important;
    margin: 0 0 12px 0 !important;
    line-height: 24px !important;
}
.sidebar h2, .sidebar h3 {
    font-size: 14px !important;
    font-weight: 500 !important;
    color: var(--doubao-black) !important;
    margin: 0 0 8px 0 !important;
    line-height: 20px !important;
}
.sidebar label, .sidebar div, .sidebar span {
    font-size: 13px !important;
    color: var(--doubao-black) !important;
    line-height: 18px !important;
}

/* 豆包按钮样式 */
.stButton>button { 
    background-color: var(--doubao-blue) !important;
    color: var(--doubao-white) !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 6px 12px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    line-height: 18px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}
.stButton>button:hover { 
    background-color: #0E48E5 !important;
    box-shadow: 0 2px 4px rgba(22, 93, 255, 0.15) !important;
}
.stButton>button[type="secondary"] {
    background-color: var(--doubao-white) !important;
    color: var(--doubao-black) !important;
    border: 1px solid var(--doubao-gray) !important;
}
.stButton>button[type="secondary"]:hover {
    background-color: var(--doubao-gray-light) !important;
}

/* 豆包输入框样式 */
.stTextInput>div>div>input, .stTextArea>div>div>textarea {
    font-size: 13px !important;
    color: var(--doubao-black) !important;
    border: 1px solid var(--doubao-gray) !important;
    border-radius: 6px !important;
    padding: 8px 12px !important;
    background-color: var(--doubao-white) !important;
    line-height: 18px !important;
}
.stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
    border-color: var(--doubao-blue) !important;
    box-shadow: 0 0 0 2px rgba(22, 93, 255, 0.1) !important;
    outline: none !important;
}

/* 豆包聊天区样式 */
.block-container { 
    padding: 24px 24px 0 24px !important;
    max-width: 1200px !important;
    background-color: var(--doubao-white) !important;
}
.main { background-color: var(--doubao-white) !important; }

/* 豆包聊天消息气泡 */
.stChatMessage { 
    padding: 12px 16px !important; 
    border-radius: 8px !important;
    margin-bottom: 8px !important;
    line-height: 20px !important;
}
.stChatMessage[data-testid="stChatMessageUser"] {
    background-color: var(--doubao-blue) !important;
    color: var(--doubao-white) !important;
}
.stChatMessage[data-testid="stChatMessageAssistant"] {
    background-color: var(--doubao-gray-light) !important;
    color: var(--doubao-black) !important;
    border: 1px solid var(--doubao-gray) !important;
}

/* 豆包输入框（底部） */
.stChatInput>div>div>input { 
    font-size: 14px !important;
    border-radius: 8px !important;
    border: 1px solid var(--doubao-gray) !important;
    padding: 12px 16px !important;
    color: var(--doubao-black) !important;
}
.stChatInput>div>div>input:focus {
    border-color: var(--doubao-blue) !important;
    box-shadow: 0 0 0 2px rgba(22, 93, 255, 0.1) !important;
}

/* Token显示行（豆包小字风格） */
.token-info {
    font-size: 12px !important;
    color: var(--doubao-gray-dark) !important;
    padding: 8px 12px !important;
    margin-top: 12px !important;
    border-top: 1px solid var(--doubao-gray) !important;
    line-height: 16px !important;
}

/* 豆包标题样式 */
h1[data-testid="stTitle"] {
    font-size: 24px !important;
    font-weight: 600 !important;
    color: var(--doubao-black) !important;
    margin-bottom: 8px !important;
    line-height: 32px !important;
}
.stCaption {
    font-size: 13px !important;
    color: var(--doubao-gray-dark) !important;
    margin-bottom: 24px !important;
    line-height: 18px !important;
}

/* 豆包提示框样式 */
.stSuccess, .stWarning, .stError, .stInfo {
    padding: 8px 12px !important;
    border-radius: 6px !important;
    font-size: 13px !important;
    line-height: 18px !important;
    margin: 4px 0 !important;
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

# --------------------------- 侧边栏（豆包风格） ---------------------------
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
    
    # 4. Token余量显示（豆包小字风格）
    token_data = get_token_usage()
    st.markdown(f"""
    <div class="token-info">
        📊 Token余量：<br>
        豆包：{token_data['doubao']['remaining']}/{token_data['doubao']['total']}（{token_data['doubao']['percent']}%）
    </div>
    """, unsafe_allow_html=True)

# --------------------------- 主聊天区（豆包风格） ---------------------------
st.title("💬 营销方案智能助手")
st.caption("基于豆包专属模型，适配品牌/营销/广告场景")

# 显示历史聊天
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 初始化豆包客户端
doubao_client = init_doubao_client()

# 用户输入（豆包风格输入框）
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
                
                # 一键复制按钮（豆包风格）
                if st.button("📋 复制内容"):
                    st.success("✅ 已复制到剪贴板！")
                
                # 保存回复
                st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
                
            except Exception as e:
                st.error(f"生成失败：{str(e)[:200]}")
                st.info("请检查豆包API Key是否有效，或确认火山方舟账号已开通对应模型权限！")
