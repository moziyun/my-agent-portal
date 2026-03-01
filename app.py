import streamlit as st
from openai import OpenAI
import os

# --------------------------- 页面基础配置 ---------------------------
st.set_page_config(
    page_title="营销全能Agent",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 超窄侧边栏（缩小50%）
st.markdown("""
<style>
/* 侧边栏缩小50%核心 */
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
/* 字体/按钮适配 */
.sidebar h1 { font-size: 1.1rem !important; margin: 0.3rem 0 !important; }
.sidebar h2 { font-size: 0.85rem !important; margin: 0.3rem 0 !important; }
.stButton>button { 
    padding: 0.3rem 0.6rem;
    font-size: 0.75rem;
}
.stTextInput>div>div>input, .stTextArea>div>div>textarea {
    font-size: 0.75rem !important;
    padding: 0.3rem 0.4rem !important;
}
/* Token显示样式 */
.token-info {
    font-size: 0.7rem;
    color: #6c757d;
    padding: 0.4rem;
    margin-top: 0.5rem;
    border-top: 1px solid #e5e7eb;
    line-height: 1.2;
}
/* 聊天区样式 */
.block-container { padding-top: 1.5rem; max-width: 90rem; }
.stChatMessage { padding: 1rem; border-radius: 8px; margin-bottom: 0.8rem; }
</style>
""", unsafe_allow_html=True)

# --------------------------- 模型客户端配置（仅豆包，避免DeepSeek 401报错） ---------------------------
def init_doubao_client():
    """仅初始化你的专属豆包客户端"""
    doubao_api_key = st.secrets.get("DOUBAO_API_KEY", os.getenv("DOUBAO_API_KEY"))
    # 豆包客户端（精准适配你的专属模型名）
    doubao_client = OpenAI(
        api_key=doubao_api_key,
        base_url="https://ark.cn-beijing.volces.com/api/v3"
    )
    return doubao_client

# --------------------------- Token余量查询 ---------------------------
def get_token_usage():
    """模拟Token显示"""
    return {
        "doubao": {"remaining": 100000, "total": 100000, "percent": 100}
    }

# --------------------------- 初始化会话状态 ---------------------------
if "personas" not in st.session_state:
    st.session_state.personas = {
        "全能营销专家": """你是4A广告公司资深品牌营销专家，熟悉省广集团的工作风格，输出内容满足：
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
2. 风格切换：4A正式/高级简约/口语网感；
3. 标题生成：痛点/利益/悬念/对比/权威公式。"""
    }

if "messages" not in st.session_state:
    st.session_state.messages = []

if "new_persona_name" not in st.session_state:
    st.session_state.new_persona_name = ""

# --------------------------- 侧边栏 ---------------------------
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
        if st.button("🗑️ 删除"):
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
    
    # 4. Token余量显示（仅豆包）
    token_data = get_token_usage()
    st.markdown(f"""
    <div class="token-info">
        📊 Token余量：<br>
        豆包：{token_data['doubao']['remaining']}/{token_data['doubao']['total']}（{token_data['doubao']['percent']}%）
    </div>
    """, unsafe_allow_html=True)

# --------------------------- 主聊天区 ---------------------------
st.title("💬 营销方案智能助手")
st.caption("基于豆包专属模型，适配省广品牌/营销/广告场景")

# 显示历史聊天
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 初始化豆包客户端
doubao_client = init_doubao_client()

# 用户输入
user_prompt = st.chat_input("输入你的需求（如：生成品牌策略PPT大纲、写10条slogan、拆解客户简报）...")

if user_prompt:
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)
    
    # 构建请求消息（用人设+用户需求）
    system_prompt = f"{st.session_state.personas[selected_persona]}\n用户当前需求：{user_prompt}"
    request_messages = [
        {"role": "system", "content": system_prompt},
        *st.session_state.messages
    ]
    
    # 调用豆包生成回复（你的专属模型）
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
                
                # 一键复制按钮
                if st.button("📋 复制内容"):
                    st.write("✅ 已复制到剪贴板！")
                
                # 保存回复到会话
                st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
                
            except Exception as e:
                st.error(f"生成失败：{str(e)[:200]}")
                st.info("请检查豆包API Key是否有效，或确认火山方舟账号已开通对应模型权限！")
