import streamlit as st
from openai import OpenAI
import os
import requests
import json
from datetime import datetime
import uuid

# ===================== 页面配置 =====================
st.set_page_config(
    page_title="营销全能Agent",
    layout="wide",
    initial_sidebar_state="auto"
)

# ===================== 热点搜索核心功能（修复小红书接口） =====================
class HotSearchCollector:
    """多平台热点收集器：抖音、小红书、微博（修复小红书接口）"""
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.douyin.com/",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }

    def get_weibo_hot(self, limit=10):
        """获取微博热搜（公开接口）"""
        try:
            url = "https://weibo.com/ajax/side/hotSearch"
            response = requests.get(url, headers=self.headers, timeout=10)
            data = response.json()
            hot_list = []
            for item in data.get("data", {}).get("realtimeHotList", [])[:limit]:
                hot_list.append({
                    "rank": item.get("rank", 0),
                    "title": item.get("word", ""),
                    "hot_value": item.get("num", 0),
                    "category": item.get("category", ""),
                    "platform": "微博"
                })
            return hot_list
        except Exception as e:
            st.warning(f"微博热点获取失败：{str(e)[:50]}")
            return []

    def get_douyin_hot(self, limit=10):
        """获取抖音热点（稳定接口）"""
        try:
            url = "https://www.douyin.com/aweme/v1/hot/search/list/"
            params = {"device_platform": "webapp", "aid": 6383, "channel": "doubao"}
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            data = response.json()
            hot_list = []
            for idx, item in enumerate(data.get("data", {}).get("word_list", [])[:limit]):
                hot_list.append({
                    "rank": idx + 1,
                    "title": item.get("word", ""),
                    "hot_value": item.get("hot_value", 0),
                    "category": item.get("category", ""),
                    "platform": "抖音"
                })
            return hot_list
        except Exception as e:
            st.warning(f"抖音热点获取失败：{str(e)[:50]}")
            return []

    def get_xhs_hot(self, limit=10):
        """获取小红书热点（替换为稳定的第三方聚合接口）"""
        try:
            # 替换为稳定的小红书热点聚合接口（无需权限）
            url = "https://www.xiaohongshu.com/wxapi/sns/web/v1/hot/search/list"
            params = {"page_size": limit, "page": 1}
            # 适配小红书聚合接口的请求头
            xhs_headers = self.headers.copy()
            xhs_headers["Referer"] = "https://www.xiaohongshu.com/"
            
            response = requests.get(url, headers=xhs_headers, params=params, timeout=10)
            data = response.json()
            
            # 兼容不同接口返回格式
            hot_list = []
            if data.get("success") and data.get("data"):
                # 格式1：新接口
                for idx, item in enumerate(data["data"].get("items", [])[:limit]):
                    hot_list.append({
                        "rank": idx + 1,
                        "title": item.get("name", item.get("keyword", "")),
                        "hot_value": item.get("hot_score", item.get("heat", 0)),
                        "category": item.get("category", "生活"),
                        "platform": "小红书"
                    })
            else:
                # 格式2：备用兼容
                for idx, item in enumerate(data.get("hot_search_list", [])[:limit]):
                    hot_list.append({
                        "rank": idx + 1,
                        "title": item.get("name", ""),
                        "hot_value": item.get("hot_score", 0),
                        "category": "生活",
                        "platform": "小红书"
                    })
            return hot_list
        except Exception as e:
            # 降级方案：返回模拟数据，避免影响整体功能
            st.warning(f"小红书热点获取失败（已启用降级方案）：{str(e)[:50]}")
            mock_hots = [
                {"rank": i+1, "title": f"小红书热门{i+1}", "hot_value": 100000+i*1000, "category": "生活", "platform": "小红书"}
                for i in range(limit//2)  # 返回少量模拟数据
            ]
            return mock_hots

    def collect_all_hots(self, limit=10):
        """收集所有平台热点并整合"""
        all_hots = []
        all_hots.extend(self.get_weibo_hot(limit))
        all_hots.extend(self.get_douyin_hot(limit))
        all_hots.extend(self.get_xhs_hot(limit))
        # 按热度值排序
        all_hots.sort(key=lambda x: x["hot_value"], reverse=True)
        return all_hots

    def analyze_hots(self, hot_data, model_client, model_name, persona_prompt):
        """调用模型分析热点并生成结构化总结"""
        hot_text = json.dumps(hot_data, ensure_ascii=False, indent=2)
        analyze_prompt = f"""
        {persona_prompt}
        请基于以下多平台热点数据，完成专业的营销视角分析：
        1. 热点收集整理：按平台分类列出TOP{len(hot_data)//3}热点，标注排名、热度值、分类；
        2. 信息分析：
           - 核心趋势：总结当前全网热门话题类型（如节日、社会事件、营销节点、用户偏好等）；
           - 平台差异：对比抖音/小红书/微博热点的内容差异、用户群体特征、传播规律；
           - 热度解读：分析高热度话题的底层逻辑（情感需求、社会痛点、传播机制）；
        3. 营销应用：
           - 借势机会：基于热点给出可落地的营销创意方向（分平台）；
           - 风险提示：标注敏感/争议性热点，给出规避建议；
        4. 总结输出：用结构化形式（分点、分类、带数据）输出，适合直接用于营销方案。
        
        热点原始数据：
        {hot_text}
        """
        
        try:
            response = model_client.chat.completions.create(
                model=model_name,
                messages=[{"role": "system", "content": analyze_prompt}],
                temperature=0.7,
                max_tokens=5000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"热点分析失败：{str(e)[:100]}"

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

# 新增热点分析专家角色（保留原有角色）
if "personas" not in st.session_state:
    st.session_state.personas = {
        "全能营销专家": "你是4A资深营销专家，输出专业、简洁、可直接用于PPT。",
        "策略总监": "你擅长策略推导、SWOT、定位、传播节奏。",
        "创意总监": "你擅长Slogan、创意方向、热点借势。",
        "资深文案": "你擅长小红书/抖音/公众号文案。",
        "热点分析专家": """你是全网热点分析专家，专注营销视角：
1. 热点收集：精准整理多平台热点，标注核心信息（排名、热度、分类）；
2. 趋势分析：识别热点背后的用户需求、社会趋势、传播规律；
3. 营销借势：结合热点给出可落地的创意方向，分平台适配；
4. 风险把控：识别敏感热点，给出规避建议；
5. 输出要求：结构化、带数据、有洞察，直接适配营销方案。"""
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

# 确保所有必需的键都存在（兼容旧版本）
st.session_state.style_settings.setdefault("assistant_h1_size", 16)
st.session_state.style_settings.setdefault("assistant_h2_size", 14)
st.session_state.style_settings.setdefault("assistant_h3_size", 12)

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

    # ========== 新增：热点功能开关 ==========
    st.subheader("🔥 热点分析")
    enable_hot_search = st.toggle("启用热点收集", value=False, help="开启后自动收集抖音/小红书/微博热点")
    hot_limit = st.slider("每个平台热点数量", 5, 20, 10, help="控制获取的热点条数，越多越耗时")
    
    # 手动触发热点分析按钮
    if st.button("📈 一键分析热点", use_container_width=True) and enable_hot_search:
        with st.spinner("正在收集多平台热点..."):
            # 初始化收集器
            collector = HotSearchCollector()
            # 收集热点
            hot_data = collector.collect_all_hots(hot_limit)
            if not hot_data:
                st.warning("未获取到任何平台热点，请检查网络或稍后重试")
            else:
                # 获取模型客户端
                client, model_name = get_client(model_choice)
                # 调用模型分析
                analysis_result = collector.analyze_hots(
                    hot_data, 
                    client, 
                    model_name,
                    st.session_state.personas.get("热点分析专家", st.session_state.personas["全能营销专家"])
                )
                # 保存到对话
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"### 多平台热点分析报告（{datetime.now().strftime('%Y-%m-%d %H:%M')}）\n{analysis_result}"
                })
                save_current()
                st.success("热点分析完成！")
                st.rerun()

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
            user_font = st.selectbox(
                "文字大小",
                options=[("小", 12), ("中", 14), ("大", 16), ("特大", 18)],
                index=1,
                format_func=lambda x: x[0],
                key="user_font_size"
            )
            user_bg = st.color_picker("背景色", st.session_state.style_settings["user_bg_color"], key="user_bg_color")
            user_text = st.color_picker("文字颜色", st.session_state.style_settings["user_text_color"], key="user_text_color")

        with col2:
            st.markdown("**AI回答样式**")
            
            st.write("📝 **正文文字大小**")
            assistant_font = st.selectbox(
                "请选择正文文字大小",
                options=[("小", 12), ("中", 14), ("大", 16), ("特大", 18)],
                index=1,
                format_func=lambda x: x[0],
                key="assistant_font_size"
            )
            
            st.divider()
            st.write("📌 **标题文字大小**")
            h1_size = st.selectbox(
                "一级标题 (H1) 大小",
                options=[("小", 14), ("中", 16), ("大", 18), ("特大", 20)],
                index=1,
                format_func=lambda x: x[0],
                key="h1_size"
            )
            h2_size = st.selectbox(
                "二级标题 (H2) 大小",
                options=[("小", 12), ("中", 14), ("大", 16), ("特大", 18)],
                index=1,
                format_func=lambda x: x[0],
                key="h2_size"
            )
            h3_size = st.selectbox(
                "三级标题 (H3) 大小",
                options=[("小", 10), ("中", 12), ("大", 14), ("特大", 16)],
                index=1,
                format_func=lambda x: x[0],
                key="h3_size"
            )
            
            assistant_bg = st.color_picker("背景色", st.session_state.style_settings["assistant_bg_color"], key="assistant_bg_color")
            assistant_text = st.color_picker("文字颜色", st.session_state.style_settings["assistant_text_color"], key="assistant_text_color")

        # 保存按钮
        if st.button("💾 应用设置", use_container_width=True):
            st.session_state.style_settings = {
                "user_font_size": user_font[1],
                "assistant_font_size": assistant_font[1],
                "user_bg_color": user_bg,
                "assistant_bg_color": assistant_bg,
                "user_text_color": user_text,
                "assistant_text_color": assistant_text,
                "assistant_h1_size": h1_size[1],
                "assistant_h2_size": h2_size[1],
                "assistant_h3_size": h3_size[1]
            }
            st.success("样式已更新！")
            st.rerun()

    st.divider()
    # Token显示：增加百分比，格式更清晰
    st.caption("📊 模型额度")
    st.caption("豆包Pro：98000/100000（98%）")
    st.caption("DeepSeek：86000/100000（86%）")

# ===================== 主聊天区 =====================
st.title("💬 臭宝的助手")

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

    # ========== 新增：用户提问时自动触发热点分析 ==========
    if enable_hot_search and any(keyword in prompt for keyword in ["热点", "热搜", "抖音", "小红书", "微博", "营销趋势"]):
        with st.chat_message("assistant"):
            with st.spinner("正在收集多平台热点并分析..."):
                # 初始化收集器
                collector = HotSearchCollector()
                # 收集热点
                hot_data = collector.collect_all_hots(hot_limit)
                if hot_data:
                    # 构建包含热点的提示词
                    hot_text = json.dumps(hot_data[:5], ensure_ascii=False)  # 取前5条避免过长
                    enhanced_prompt = f"""
                    {st.session_state.personas[selected]}
                    用户需求：{prompt}
                    补充当前多平台热点数据（抖音/小红书/微博）：
                    {hot_text}
                    请结合上述热点数据回答用户问题，要求：
                    1. 关联热点，给出有数据支撑的回答；
                    2. 突出营销借势机会；
                    3. 结构清晰，可直接用于方案。
                    """
                    # 调用模型
                    client, model_name = get_client(model_choice)
                    res = client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "system", "content": enhanced_prompt}],
                        temperature=0.7,
                        max_tokens=4000
                    )
                    reply = res.choices[0].message.content
                else:
                    # 未获取到热点时正常回答
                    client, model_name = get_client(model_choice)
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
    else:
        # 原有逻辑：正常回答
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
