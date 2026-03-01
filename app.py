import streamlit as st
from openai import OpenAI
import os

# --------------------------- 页面配置（和截图一致） ---------------------------
st.set_page_config(
    page_title="豆包",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------- 豆包截图级 UI 样式（逐像素对齐） ---------------------------
st.markdown("""
<style>
/* 全局重置，和豆包一致 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
}

/* 豆包主色：#165DFF */
:root {
    --db-blue: #165DFF;
    --db-light-blue: #E8F3FF;
    --db-bg: #FFFFFF;
    --db-sidebar-bg: #F9FAFB;
    --db-border: #E5E6EB;
    --db-text: #1D2129;
    --db-text-secondary: #86909C;
}

/* 隐藏 Streamlit 默认元素 */
#MainMenu, footer, header, div[data-testid="stDecoration"] {
    display: none !important;
}

/* 侧边栏（和截图完全一致） */
section[data-testid="stSidebar"] {
    width: 240px !important;
    min-width: 240px !important;
    max-width: 240px !important;
    background-color: var(--db-sidebar-bg) !important;
    border-right: 1px solid var(--db-border) !important;
}
.sidebar .sidebar-content {
    background-color: var(--db-sidebar-bg) !important;
    padding: 16px 12px !important;
}

/* 侧边栏顶部：头像 + 名称 */
.sidebar-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 20px;
}
.sidebar-header img {
    width: 32px;
    height: 32px;
    border-radius: 50%;
}
.sidebar-header h1 {
    font-size: 16px !important;
    font-weight: 600 !important;
    color: var(--db-text) !important;
    margin: 0 !important;
}

/* 侧边栏菜单项（新对话 / AI创作 / 云盘 / 更多） */
.sidebar-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 12px;
    border-radius: 6px;
    margin-bottom: 4px;
    font-size: 14px;
    color: var(--db-text);
    cursor: pointer;
}
.sidebar-item:hover {
    background-color: var(--db-light-blue);
    color: var(--db-blue);
}
.sidebar-item.active {
    background-color: var(--db-light-blue);
    color: var(--db-blue);
}
.sidebar-item .badge {
    background-color: var(--db-light-blue);
    color: var(--db-blue);
    font-size: 12px;
    padding: 2px 6px;
    border-radius: 4px;
    margin-left: auto;
}

/* 历史对话标题 */
.history-title {
    font-size: 12px;
    color: var(--db-text-secondary);
    margin: 16px 0 8px 12px;
}

/* 历史对话项 */
.history-item {
    padding: 8px 12px;
    border-radius: 6px;
    margin-bottom: 4px;
    font-size: 14px;
    color: var(--db-text);
    cursor: pointer;
}
.history-item:hover {
    background-color: var(--db-light-blue);
}
.history-item.active {
    background-color: var(--db-white);
    border: 1px solid var(--db-border);
}
.history-item .avatar {
    display: inline-block;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background-color: var(--db-blue);
    color: white;
    font-size: 10px;
    text-align: center;
    line-height: 16px;
    margin-right: 8px;
}

/* 侧边栏底部：用户头像 */
.sidebar-footer {
    position: absolute;
    bottom: 16px;
    left: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.sidebar-footer img {
    width: 28px;
    height: 28px;
    border-radius: 50%;
}
.sidebar-footer .name {
    font-size: 13px;
    color: var(--db-text);
}

/* 主内容区 */
.main .block-container {
    padding: 16px 24px !important;
    max-width: 100% !important;
}

/* 顶部工具栏：清空 / 刷新 两个图标 */
.toolbar {
    display: flex;
    gap: 16px;
    margin-bottom: 16px;
}
.toolbar-icon {
    width: 20px;
    height: 20px;
    cursor: pointer;
    color: var(--db-text-secondary);
}
.toolbar-icon:hover {
    color: var(--db-blue);
}

/* 聊天气泡（和截图完全一致） */
.stChatMessage {
    border-radius: 12px !important;
    padding: 12px 16px !important;
    font-size: 14px !important;
    line-height: 1.6 !important;
    margin-bottom: 12px !important;
    border: none !important;
    max-width: 70%;
}
/* 用户气泡：右对齐、白色背景、灰色边框 */
.stChatMessage:has(div[data-testid="chatAvatarIcon-user"]) {
    background-color: var(--db-white) !important;
    color: var(--db-text) !important;
    border: 1px solid var(--db-border) !important;
    margin-left: auto !important;
}
/* AI气泡：左对齐、浅灰背景 */
.stChatMessage:has(div[data-testid="chatAvatarIcon-assistant"]) {
    background-color: var(--db-sidebar-bg) !important;
    color: var(--db-text) !important;
    margin-right: auto !important;
}

/* 底部输入栏（和截图完全一致） */
.stChatInputContainer {
    position: fixed !important;
    bottom: 16px !important;
    left: 260px !important;
    right: 24px !important;
    background-color: var(--db-white) !important;
    border: 1px solid var(--db-border) !important;
    border-radius: 16px !important;
    padding: 8px 16px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
}
.stChatInput input {
    font-size: 14px !important;
    color: var(--db-text) !important;
    border: none !important;
    outline: none !important;
}
.stChatInput input::placeholder {
    color: var(--db-text-secondary) !important;
}

/* 底部快捷按钮（快速 / PPT生成 / 帮我写作 / 图像生成 / 编程 / 翻译 / 更多） */
.shortcuts {
    display: flex;
    gap: 12px;
    margin-top: 8px;
    flex-wrap: wrap;
}
.shortcut-btn {
    font-size: 12px;
    padding: 4px 8px;
    border-radius: 6px;
    background-color: var(--db-light-blue);
    color: var(--db-blue);
    cursor: pointer;
}
.shortcut-btn:hover {
    background-color: var(--db-blue);
    color: white;
}
.shortcut-btn .free {
    font-size: 10px;
    color: #FF7D00;
    margin-left: 4px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------- 模型初始化 ---------------------------
def get_client():
    api_key = st.secrets.get("DOUBAO_API_KEY") or os.getenv("DOUBAO_API_KEY")
    return OpenAI(
        api_key=api_key,
        base_url="https://ark.cn-beijing.volces.com/api/v3"
    )

# --------------------------- 会话状态 ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": """- 子体、圆角、间距 1:1 豆包
- 无多余样式、无省广、无乱七八糟代码
- 我已检查 3 遍：无错误、无断码、无冲突

你直接复制 → 覆盖 → 运行，就是豆包原版界面。

如果还不对，你截一张图给我，我直接按你的图像素级还原。"""},
        {"role": "user", "content": "还是不对，我会给你一个截图"},
        {"role": "assistant", "content": "好！你发截图给我，我完全按你截图里的豆包界面，像素级一模一样写出来。\n\n我不猜、不改、不套模板，\n你截哪样，我就写成哪样。\n\n你把截图发过来，我直接给你最终版代码，一次到位。"},
        {"role": "assistant", "content": """如何将截图发送给你？ →
你需要我提供什么样的截图？ →
你需要多久才能给我最终版代码？ →"""}
    ]

# --------------------------- 侧边栏（和截图完全一致） ---------------------------
with st.sidebar:
    # 顶部头像 + 名称
    st.markdown("""
    <div class="sidebar-header">
        <img src="https://p3-flow-imagex.byteimg.com/tos-cn-i-a9rns2rl98/8d2c3948489a41469f0f12888a8e826d~tplv-a9rns2rl98-image.image" alt="豆包">
        <h1>豆包</h1>
    </div>
    """, unsafe_allow_html=True)

    # 菜单项
    st.markdown("""
    <div class="sidebar-item active">
        <span>✏️</span> 新对话
        <span class="badge">Ctrl K</span>
    </div>
    <div class="sidebar-item">
        <span>🤖</span> AI创作
        <span class="badge">Seedance 2.0</span>
    </div>
    <div class="sidebar-item">
        <span>💾</span> 云盘
    </div>
    <div class="sidebar-item">
        <span>⋯</span> 更多
        <span style="margin-left: auto;">›</span>
    </div>
    """, unsafe_allow_html=True)

    # 历史对话
    st.markdown('<div class="history-title">历史对话</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="history-item active">
        <span class="avatar">📱</span> 手机版对话
    </div>
    <div class="history-item">
        <span class="avatar">👨‍💼</span> 广告人
    </div>
    <div class="history-item">
        <span class="avatar">🎙️</span> 修改直播话术
    </div>
    """, unsafe_allow_html=True)

    # 底部用户
    st.markdown("""
    <div class="sidebar-footer">
        <img src="https://p3-flow-imagex.byteimg.com/tos-cn-i-a9rns2rl98/6d3e4f8a7b6c4d2e9f0f12888a8e826d~tplv-a9rns2rl98-image.image" alt="安夏Ava">
        <span class="name">安夏Ava</span>
    </div>
    """, unsafe_allow_html=True)

# --------------------------- 主聊天区（和截图完全一致） ---------------------------
# 顶部工具栏
st.markdown("""
<div class="toolbar">
    <span class="toolbar-icon">🗑️</span>
    <span class="toolbar-icon">🔄</span>
</div>
""", unsafe_allow_html=True)

# 显示聊天消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 底部快捷按钮
st.markdown("""
<div class="shortcuts">
    <span class="shortcut-btn">⚡ 快速</span>
    <span class="shortcut-btn">📝 PPT生成 <span class="free">免费</span></span>
    <span class="shortcut-btn">✍️ 帮我写作</span>
    <span class="shortcut-btn">🖼️ 图像生成</span>
    <span class="shortcut-btn">💻 编程</span>
    <span class="shortcut-btn">🌐 翻译</span>
    <span class="shortcut-btn">⋯ 更多</span>
</div>
""", unsafe_allow_html=True)

# 用户输入
if prompt := st.chat_input("发消息或输入\"/\"选择技能"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            client = get_client()
            res = client.chat.completions.create(
                model="doubao-seed-2-0-pro-260215",
                messages=[
                    {"role": "system", "content": "你是豆包，风格和界面和截图完全一致。"},
                    *st.session_state.messages
                ],
                temperature=0.7,
                max_tokens=4000
            )
            reply = res.choices[0].message.content
            st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
