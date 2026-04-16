import streamlit as st
import streamlit.components.v1 as components
from agno.agent import Agent
from agno.run.agent import RunOutput
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.models.google import Gemini
from agno.tools.newspaper4k import Newspaper4kTools

# ─── 页面配置 ─────────────────────────────────────────────
st.set_page_config(
    page_title="趋势雷达 | Trend Radar",
    page_icon="📡",
    layout="wide",
)

# ─── 样式注入 ─────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background: #0d1117; }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #161b22 !important;
        color: #e6edf3 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
    }
    h1, h2, h3 { color: #58a6ff !important; }
    .stButton > button {
        background: linear-gradient(135deg, #238636, #2ea043) !important;
        color: white !important;
        border: none !important;
        font-size: 16px !important;
        padding: 0.6rem 2rem !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    .stButton > button:hover { opacity: 0.85 !important; }
    .reportview-container .main .block-container { padding-top: 2rem; }
    .info-box {
        background: #161b22;
        border-left: 4px solid #58a6ff;
        padding: 1rem 1.2rem;
        border-radius: 0 8px 8px 0;
        color: #8b949e;
        margin-bottom: 1.5rem;
    }
    .agent-step {
        display: flex; align-items: center; gap: 10px;
        color: #7ee787; font-size: 14px; margin: 4px 0;
    }
    .stMarkdown { color: #e6edf3; }
</style>
""", unsafe_allow_html=True)

# ─── 侧边栏：密码 + API Key ──────────────────────────────
st.sidebar.markdown("## 🔐 访问设置")
APP_PASSWORD = st.sidebar.text_input("访问密码", type="password", value="")
GOOGLE_API_KEY = st.sidebar.text_input("Google Gemini API Key", type="password")
st.sidebar.markdown("---")
st.sidebar.markdown("""
**📌 使用说明**

1. 输入上方访问密码
2. 填入你的 Gemini API Key  
3. 输入要分析的主题
4. 点击「🚀 开始分析」

> API Key 获取：  
> [aistudio.google.com](https://aistudio.google.com/app/apikey)  
> 免费额度每天 1500 次请求
""")
st.sidebar.markdown("---")
st.sidebar.caption("📡 趋势雷达 · 免费部署版")

# ─── 密码校验 ─────────────────────────────────────────────
CORRECT_PASSWORD = APP_PASSWORD.strip()

if CORRECT_PASSWORD != "trend2025":
    st.markdown("# 📡 趋势雷达")
    st.markdown("### AI 创业趋势分析智能体")
    st.markdown("")
    st.info("👈 请在左侧边栏输入访问密码后使用")
    st.stop()

# ─── 主界面 ──────────────────────────────────────────────
st.markdown("# 📡 趋势雷达")
st.markdown("### AI 创业趋势分析智能体")

col1, col2, col3, col4 = st.columns(4)
with col1: st.markdown("🔍 **新闻采集**\nDuckDuckGo 实时搜索")
with col2: st.markdown("📝 **摘要生成**\nNewspaper4k 文章解析")
with col3: st.markdown("📊 **趋势分析**\nGemini 深度推理")
with col4: st.markdown("💡 **机会识别**\n创业方向洞察")

st.markdown("---")

# ─── 输入区 ───────────────────────────────────────────────
topic = st.text_input(
    "🎯 输入你想分析的领域或主题",
    placeholder="例如：AI教育、低空经济、具身智能……",
    help="输入越具体，分析越精准"
)

col_btn, col_status = st.columns([1, 3])
with col_btn:
    run_analysis = st.button("🚀 开始分析", use_container_width=True)

if run_analysis:
    if not GOOGLE_API_KEY:
        st.warning("⚠️ 请先在左侧填入 Google Gemini API Key")
        st.stop()

    if not topic.strip():
        st.warning("⚠️ 请输入要分析的主题")
        st.stop()

    with st.spinner("🔄 正在分析，请稍候……"):
        try:
            gemini_model = Gemini(id="gemini-2.5-flash", api_key=GOOGLE_API_KEY)

            # Step 1: 采集新闻
            news_collector = Agent(
                name="News Collector",
                role="收集最新行业新闻和创业动态",
                tools=[DuckDuckGoTools()],
                model=gemini_model,
                instructions=["用中文搜索并收集关于该领域最新的新闻、融资事件、行业动态"],
                markdown=True,
            )
            st.info("📡 Step 1：正在联网搜索……")
            news_response: RunOutput = news_collector.run(f"搜索并收集：{topic} 相关的最新行业新闻、融资动态和技术趋势（近3个月内）")

            articles = news_response.content

            # Step 2: 摘要生成
            summary_writer = Agent(
                name="Summary Writer",
                role="对收集的文章进行摘要和提炼",
                tools=[Newspaper4kTools(enable_read_article=True, include_summary=True)],
                model=gemini_model,
                instructions=["对文章进行结构化摘要，提取关键信息和数据"],
                markdown=True,
            )
            st.info("📝 Step 2：正在生成摘要……")
            summary_response: RunOutput = summary_writer.run(
                f"对以下文章进行摘要和关键信息提取（用中文）：\n{articles}"
            )
            summaries = summary_response.content

            # Step 3: 趋势分析
            trend_analyzer = Agent(
                name="Trend Analyzer",
                role="深度分析行业趋势和创业机会",
                model=gemini_model,
                instructions=[
                    "从摘要中识别3-5个核心趋势",
                    "分析每个趋势的：市场规模、增长逻辑、代表公司/产品",
                    "给出2-3个具体的创业切入点建议",
                    "用中文输出，结构清晰，有数据支撑",
                ],
                markdown=True,
            )
            st.info("📊 Step 3：正在深度分析……")
            trend_response: RunOutput = trend_analyzer.run(
                f"基于以下摘要，分析「{topic}」领域的创业趋势与机会（中文输出）：\n{summaries}"
            )
            analysis = trend_response.content

            st.success("✅ 分析完成！")
            st.markdown("---")
            st.markdown("## 📊 趋势分析结果")
            st.markdown(analysis)

            # 可选：显示原始摘要
            with st.expander("📋 查看原始摘要（可复制使用）"):
                st.markdown(summaries)

        except Exception as e:
            st.error(f"❌ 分析出错：{e}")
else:
    st.markdown("""
    <div class="info-box">
    输入分析主题后点击「🚀 开始分析」，系统将自动完成：<br>
    🔍 实时搜索 → 📝 摘要提炼 → 📊 趋势洞察
    </div>
    """, unsafe_allow_html=True)
    st.markdown("**💡 试试这些主题：**")
    suggestions = ["AI教育 2025", "具身智能", "低空经济", "AI陪伴", "合成数据"]
    for s in suggestions:
        st.code(s)
