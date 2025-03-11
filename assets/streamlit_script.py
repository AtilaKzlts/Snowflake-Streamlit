import streamlit as st
import pandas as pd
import altair as alt
from snowflake.snowpark.context import get_active_session

# Page config
st.set_page_config(
    page_title="DIGITAL AD CAMPAIGN DASHBOARD",
    page_icon="📊",
    layout="wide"
)

st.title("DIGITAL AD CAMPAIGN DASHBOARD")

@st.cache_data
def load_data():
    try:
        session = get_active_session()
        sql = "SELECT * FROM DIGITAL_AD_CAMPAIGNS"
        result = session.sql(sql).collect()
        df = pd.DataFrame(result)
        return df
    except Exception as e:
        st.error(f"ERROR CONNECTING TO SNOWFLAKE: {e}")
        return pd.read_csv('DIGITAL_AD_CAMPAIGN_DATA.CSV')

df = load_data()
df.columns = df.columns.str.upper()

# Sidebar filters
st.sidebar.header("FILTER DATA")

platforms = ["ALL"] + sorted(df["PLATFORM"].unique().tolist())
selected_platform = st.sidebar.selectbox("SELECT PLATFORM", platforms)

date_min = pd.to_datetime(df["START_DATE"]).min().date()
date_max = pd.to_datetime(df["END_DATE"]).max().date()
selected_date_range = st.sidebar.date_input("SELECT DATE RANGE", [date_min, date_max], date_min, date_max)

formats = ["ALL"] + sorted(df["AD_FORMAT"].unique().tolist())
selected_format = st.sidebar.selectbox("SELECT AD FORMAT", formats)

filtered_df = df.copy()

if selected_platform != "ALL":
    filtered_df = filtered_df[filtered_df["PLATFORM"] == selected_platform]

if selected_format != "ALL":
    filtered_df = filtered_df[filtered_df["AD_FORMAT"] == selected_format]

if len(selected_date_range) == 2:
    start_date, end_date = selected_date_range
    filtered_df = filtered_df[
        (pd.to_datetime(filtered_df["END_DATE"]) >= pd.to_datetime(start_date)) & 
        (pd.to_datetime(filtered_df["START_DATE"]) <= pd.to_datetime(end_date))
    ]

# KPIs
col1, col2, col3, col4 = st.columns(4)

# Subscribers, Views, Watch Hours, Likes KPI Metrics
with col1:
    total_ad_spend = filtered_df['AD_SPEND'].sum()
    st.metric("TOTAL AD SPEND", f"{total_ad_spend:,.0f}")
    # st.bar_chart(filtered_df.groupby("START_DATE")['AD_SPEND'].sum(), height=100,color='#ffaa00')
    st.area_chart(filtered_df.groupby("START_DATE")['AD_SPEND'].mean(), height=100,color='#ffaa00')
    
with col2:
    total_revenue = filtered_df['REVENUE'].sum()
    st.metric("TOTAL REVENUE", f"{total_revenue:,.0f}")
    #st.bar_chart(filtered_df.groupby("START_DATE")['REVENUE'].sum(), height=100,color='#A5158C')
    st.area_chart(filtered_df.groupby("START_DATE")['REVENUE'].mean(), height=100,color='#A5158C')
    
with col3:
    roas = total_revenue / total_ad_spend if total_ad_spend != 0 else 0
    st.metric("OVERALL ROAS", f"{roas:.2f}")
    st.area_chart(filtered_df.groupby("START_DATE")['ROAS'].mean(), height=100,color='#80CBC4')

with col4:
    total_conversions = filtered_df['CONVERSIONS'].sum()
    st.metric("TOTAL CONVERSIONS", f"{total_conversions:,.0f}")
    st.area_chart(filtered_df.groupby("START_DATE")['CONVERSIONS'].sum(), height=100,color='#41644A')

# PLATFORM PERFORMANCE - Altair usage
st.header("PLATFORM PERFORMANCE")
platform_stats = filtered_df.groupby('PLATFORM').agg({
    'AD_SPEND': 'sum',
    'REVENUE': 'sum',
    'CONVERSIONS': 'sum',
    'ROAS': 'mean'
}).reset_index()

platform_comparison = st.radio("SELECT METRIC FOR PLATFORM COMPARISON:", ["ROAS", "CONVERSIONS", "AD SPEND", "REVENUE"])

chart = alt.Chart(platform_stats).mark_bar().encode(
    x=alt.X("PLATFORM:N", title="Platform"),
    y=alt.Y(platform_comparison + ":Q", title=platform_comparison),
    color=alt.Color("PLATFORM:N", scale=alt.Scale(scheme="category10")),
    tooltip=["PLATFORM", platform_comparison]
).properties(width=700, height=400)

st.altair_chart(chart, use_container_width=True)

# AD FORMAT ANALYSIS - Altair usage
st.header("AD FORMAT ANALYSIS")
format_stats = filtered_df.groupby('AD_FORMAT').agg({
    'AD_SPEND': 'sum',
    'REVENUE': 'sum',
    'CONVERSIONS': 'sum',
    'ROAS': 'mean'
}).reset_index()

ad_format_metric = st.radio("SELECT METRIC FOR AD FORMAT ANALYSIS:", ["ROAS", "CONVERSIONS", "AD SPEND TO REVENUE RATIO"])

if ad_format_metric == "AD SPEND TO REVENUE RATIO":
    format_stats["SPEND_TO_REVENUE"] = format_stats["AD_SPEND"] / format_stats["REVENUE"]
    ad_format_metric = "SPEND_TO_REVENUE"

format_chart = alt.Chart(format_stats).mark_bar().encode(
    x=alt.X("AD_FORMAT:N", title="Ad Format"),
    y=alt.Y(ad_format_metric + ":Q", title=ad_format_metric),
    color=alt.Color("AD_FORMAT:N", scale=alt.Scale(scheme="set2")),
    tooltip=["AD_FORMAT", ad_format_metric]
).properties(width=700, height=400)

st.altair_chart(format_chart, use_container_width=True)

# DEVICE DISTRIBUTION - Altair usage
st.header("DEVICE DISTRIBUTION")
device_data = filtered_df[["MOBILE_PERCENTAGE", "DESKTOP_PERCENTAGE", "TABLET_PERCENTAGE"]].mean()

device_chart_data = pd.DataFrame({
    'DEVICE': ['MOBILE', 'DESKTOP', 'TABLET'],
    'PERCENTAGE': [
        device_data["MOBILE_PERCENTAGE"],
        device_data["DESKTOP_PERCENTAGE"],
        device_data["TABLET_PERCENTAGE"]
    ]
})

device_chart = alt.Chart(device_chart_data).mark_bar().encode(
    x=alt.X("DEVICE:N", title="Device Type"),
    y=alt.Y("PERCENTAGE:Q", title="Usage Percentage"),
    color=alt.Color("DEVICE:N", scale=alt.Scale(scheme="accent")),
    tooltip=["DEVICE", "PERCENTAGE"]
).properties(width=700, height=400)

st.altair_chart(device_chart, use_container_width=True)

#Camp X avg_order_value

df['START_DATE'] = pd.to_datetime(df['START_DATE'])


df["Month"] = df["START_DATE"].dt.strftime("%Y-%m")  # YYYY-MM formatı


monthly_campaigns = df.groupby("Month")["CAMPAIGN_ID"].count().reset_index()
monthly_campaigns.rename(columns={"CAMPAIGN_ID": "Campaign Count"}, inplace=True)


monthly_avg_order_value = df.groupby("Month")["AVG_ORDER_VALUE"].mean().reset_index()
monthly_avg_order_value["Scaled Avg Order Value"] = monthly_avg_order_value["AVG_ORDER_VALUE"] / 1000


final_data = pd.merge(monthly_campaigns, monthly_avg_order_value, on="Month")


final_data_melted = final_data.melt(id_vars=["Month"], 
                                    value_vars=["Campaign Count", "Scaled Avg Order Value"], 
                                    var_name="Metric", value_name="Value")



st.header("Number of Campaigns vs. Average Order Value")


chart = alt.Chart(final_data_melted).mark_line(point=True,size=4).encode(
    x="Month",
    y="Value",
    color=alt.Color("Metric:N", legend=alt.Legend(title="Metrik")),  # Legend eklendi
    tooltip=["Month", "Metric", "Value"]
).properties(title="Visualized as Average Order Value / 1000")

# Streamlit'te göster
st.altair_chart(chart, use_container_width=True)


st.markdown("---")
st.caption("DIGITAL AD CAMPAIGN DASHBOARD CREATED WITH STREAMLIT / ATILLA KIZILTAS")
