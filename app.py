import streamlit as st
from openai import OpenAI

# --------------------------- 模型配置 ---------------------------
def get_doubao_client():
    return OpenAI(
        api_key=st.secrets["DOUBAO_API_KEY"],
        base_url="https://ark.cn-beijing.volces.com/api/v3"
    )

def get_deepseek_client():
    return OpenAI(
        api_key=st.secrets["DEEPSEEK_API_KEY"],
        base_url="https://api.deepseek.com"
    )

# --------------------------- 页面样式 ---------------------------
st.set_page_config(
    page_title="营销全能Agent",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 清爽样式
st.markdown("""
<style>
.block-container { padding-top: 2rem; max-width: 80rem; }
.sidebar .sidebar-content { background-color: #f8f9fa; }
</style>
""", unsafe_allow_html=True)

# --------------------------- 人设 ---------------------------
if "personas" not in st.session_state:
    st.session_state.personas = {
        "全能营销": "你是专业品牌营销专家，输出专业、简洁、可直接用于方案。",
        "策略总监": "你擅长策略推导、SWOT、定位、传播路径，输出严谨有逻辑。",
        "创意总监": "你输出slogan、海报创意、视频创意、年轻化表达。",
        "资深文案": "你擅长标题、软文、小红书、抖音文案、精炼表达。"
    }

# --------------------------- 侧边栏 ---------------------------
with st.sidebar:
    st.title("🧠 营销Agent")
    selected = st.radio("选择人设", list(st.session_state.personas.keys()))
    st.divider()
    st.subheader("编辑当前人设")
    new_prompt = st.text_area("人设内容", st.session_state.personas[selected], height=200)
    if st.button("✅ 保存人设"):
        st.session_state.personas[selected] = new_prompt
        st.success("已保存！")

# --------------------------- 主界面 ---------------------------
st.title("💬 聊天区")
system_prompt = st.session_state.personas[selected]

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("输入你的需求...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 自动选模型
    model_keywords = ["策略", "分析", "方案", "SWOT", "简报", "拆解", "总结", "全案", "框架"]
    use_deepseek = any(k in user_input for k in model_keywords)

    client = get_deepseek_client() if use_deepseek else get_doubao_client()
    model = "deepseek-chat" if use_deepseek else "doubao-100k-pro"

    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *st.session_state.messages
                ],
                temperature=0.7,
            )
            res = completion.choices[0].message.content
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
