import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. 页面配置 ---
st.set_page_config(page_title="GeoInsight Pro", layout="wide", page_icon="🌍")

# 侧边栏
st.sidebar.title("🌍 GeoInsight 控制台")


# --- 2. 缓存数据读取 (核心优化) ---
@st.cache_data
def load_data(file):
    try:
        # 使用 openpyxl 引擎处理 Excel
        df = pd.read_excel(file, engine='openpyxl')
        return df
    except Exception as e:
        st.error(f"读取失败: {e}")
        return None


uploaded_file = st.sidebar.file_uploader("上传 Excel 文件 (.xlsx)", type=["xlsx"])

# 主界面
st.title("🗺️ 地理空间数据可视化平台")
st.markdown("---")

if uploaded_file:
    df = load_data(uploaded_file)

    if df is not None:
        st.success("✅ 数据加载成功 (已进入缓存)！")

        # 使用列布局节省空间
        cols = df.columns.tolist()

        tab1, tab2 = st.tabs(["📊 统计图表", "🗺️ 极速地图"])

        with tab1:
            # 统计分析逻辑保持不变，但因为有了 cache，切换极其丝滑
            c1, c2, c3 = st.columns(3)
            with c1: x_axis = st.selectbox("X 轴", cols, index=0)
            with c2: y_axis = st.selectbox("Y 轴", cols, index=1 if len(cols) > 1 else 0)
            with c3: chart_type = st.selectbox("类型", ["散点", "折线", "柱状"])

            fig = px.scatter(df, x=x_axis, y=y_axis) if chart_type == "散点" else \
                px.line(df, x=x_axis, y=y_axis) if chart_type == "折线" else \
                    px.bar(df, x=x_axis, y=y_axis)
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.subheader("地理空间可视化")


            # 自动识别经纬度列名
            def find_col(keywords, options):
                for k in keywords:
                    for opt in options:
                        if k in opt: return options.index(opt)
                return 0


            g1, g2, g3 = st.columns(3)
            with g1:
                lat_col = st.selectbox("纬度 (Lat)", cols, index=find_col(['纬', 'lat'], cols))
            with g2:
                lon_col = st.selectbox("经度 (Lon)", cols, index=find_col(['经', 'lon'], cols))
            with g3:
                size_col = st.selectbox("数值映射", [None] + cols)

            # 渲染优化：使用 Mapbox 的快速渲染模式
            map_fig = px.scatter_mapbox(
                df,
                lat=lat_col,
                lon=lon_col,
                size=size_col if size_col else None,
                color=size_col if size_col else None,
                color_continuous_scale=px.colors.cyclical.IceFire,
                zoom=3,
                height=650,
                mapbox_style="carto-positron"  # 这种底图通常比 open-street-map 加载稍快
            )
            map_fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
            st.plotly_chart(map_fig, use_container_width=True)
else:
    st.info("👈 请在左侧上传 Excel 文件。")