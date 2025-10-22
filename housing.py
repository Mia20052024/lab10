import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 设置页面标题和布局
st.set_page_config(page_title="加州住房数据应用", layout="wide")

# 侧边栏标题（包含作者名）
st.sidebar.title("加州住房数据（1990年）—— 作者：你的姓名")

# 1. 加载数据（假设数据文件与代码同目录，需提前解压housing.csv.zip）
@st.cache_data  # 缓存数据加载，提高性能
def load_data():
    try:
        df = pd.read_csv("housing.csv")
        # 处理可能的缺失值
        df = df.dropna()
        return df
    except FileNotFoundError:
        st.error("未找到housing.csv文件，请确保文件在代码目录下并已解压")
        return None

df = load_data()
if df is None:
    st.stop()  # 数据加载失败则停止运行

# 2. 交互式组件 - 房屋价格滑块（主页面）
st.header("加州住房数据（1990年）")
min_price, max_price = 0, 500001  # 价格范围
price_threshold = st.slider(
    "最低房屋中位数价格",
    min_value=min_price,
    max_value=max_price,
    value=200000,  # 默认值
    step=10000,
    format="%d"  # 整数格式显示
)

# 3. 侧边栏筛选组件
# 3.1 地点类型筛选（多选框）
# 假设数据集中有"ocean_proximity"字段表示地点类型（如原数据集）
location_types = df["ocean_proximity"].unique()
selected_locations = st.sidebar.multiselect(
    "选择地点类型",
    options=location_types,
    default=location_types  # 默认全选
)

# 3.2 收入水平筛选（单选按钮）
income_level = st.sidebar.radio(
    "选择收入水平（以中位数收入为基准）",
    options=["低（≤2.5）", "中（>2.5 且 <4.5）", "高（>4.5）"]
)

# 4. 数据筛选逻辑
# 4.1 价格筛选
filtered_df = df[df["median_house_value"] >= price_threshold]

# 4.2 地点类型筛选
filtered_df = filtered_df[filtered_df["ocean_proximity"].isin(selected_locations)]

# 4.3 收入水平筛选（根据单选按钮结果）
if income_level == "低（≤2.5）":
    filtered_df = filtered_df[filtered_df["median_income"] <= 2.5]
elif income_level == "中（>2.5 且 <4.5）":
    filtered_df = filtered_df[(filtered_df["median_income"] > 2.5) & 
                             (filtered_df["median_income"] < 4.5)]
else:  # 高（>4.5）
    filtered_df = filtered_df[filtered_df["median_income"] > 4.5]

# 5. 展示筛选后的数据量
st.write(f"筛选后的数据量：{len(filtered_df)} 条")

# 6. 地图展示（使用Streamlit内置地图）
st.subheader("房屋位置分布")
# 原数据集通常包含"latitude"（纬度）和"longitude"（经度）字段
st.map(filtered_df[["latitude", "longitude", "median_house_value"]], 
       zoom=6)  # 加州地区适当缩放

# 7. 房屋中位数价格直方图（分箱数30）
st.subheader("房屋中位数价格分布")
fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(filtered_df["median_house_value"], bins=30, edgecolor="black")
ax.set_xlabel("房屋中位数价格")
ax.set_ylabel("数量")
ax.set_title("房屋中位数价格直方图")
st.pyplot(fig)

# 8. 额外补充两个图表（满足"三个图表"要求）
# 8.1 收入与房价关系散点图
st.subheader("收入水平与房屋价格关系")
fig2, ax2 = plt.subplots(figsize=(10, 6))
ax2.scatter(filtered_df["median_income"], filtered_df["median_house_value"], 
           alpha=0.5)
ax2.set_xlabel("中位数收入")
ax2.set_ylabel("房屋中位数价格")
ax2.set_title("收入与房价关系")
st.pyplot(fig2)

# 8.2 不同地点类型的房价箱线图
st.subheader("不同地点类型的房价分布")
fig3, ax3 = plt.subplots(figsize=(10, 6))
filtered_df.boxplot(column="median_house_value", by="ocean_proximity", ax=ax3)
ax3.set_ylabel("房屋中位数价格")
plt.suptitle("")  # 去除pandas自动添加的标题
ax3.set_title("不同地点类型的房价箱线图")
st.pyplot(fig3)