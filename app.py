import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="AgriPulse", page_icon="🌾", layout="wide")

st.markdown("""
<style>
.main {background:#f7f9fc}
.block-container {padding-top:1.5rem}
[data-testid="stMetric"] {background:white;border:1px solid #e5e9f0;border-radius:14px;padding:14px}
.hero {background:linear-gradient(135deg,#eef5ff,#f7f1ff);padding:22px 26px;border-radius:18px;border:1px solid #e3e8f2;margin-bottom:18px}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("seasonal_agriculture_performance_dataset.csv")
    for c in ["Rainfall_mm", "Soil_Moisture_pct", "Yield_Tonnes_Ha"]:
        df[c] = df[c].fillna(df[c].median())
    return df

df = load_data()

st.sidebar.markdown("## 🌾 AgriPulse")
st.sidebar.caption("Seasonal Agriculture Intelligence")
page = st.sidebar.radio("Navigate", ["Dashboard","Seasonal Performance","Crop Analysis","Water & Irrigation","Profitability","Regional Insights"])

st.sidebar.divider()
season = st.sidebar.selectbox("Season", ["All"] + sorted(df.Season.unique()))
state = st.sidebar.selectbox("State", ["All"] + sorted(df.State.unique()))
crop = st.sidebar.selectbox("Crop", ["All"] + sorted(df.Crop.unique()))
irrigation = st.sidebar.selectbox("Irrigation Method", ["All"] + sorted(df.Irrigation_Method.unique()))

f = df.copy()
for col, val in [("Season",season),("State",state),("Crop",crop),("Irrigation_Method",irrigation)]:
    if val != "All": f = f[f[col] == val]

def money(x):
    if abs(x) >= 100000: return f"₹{x/100000:.2f} L"
    if abs(x) >= 1000: return f"₹{x/1000:.1f}K"
    return f"₹{x:,.0f}"

def chart(fig):
    fig.update_layout(height=370, margin=dict(l=20,r=20,t=55,b=20), paper_bgcolor="white", plot_bgcolor="white")
    fig.update_yaxes(gridcolor="#edf0f5")
    fig.update_xaxes(showgrid=False)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("""
<div class="hero">
<h1>🌾 AgriPulse</h1>
<p>Seasonal Agriculture Intelligence Dashboard</p>
</div>
""", unsafe_allow_html=True)
st.caption(f"Showing {len(f):,} of {len(df):,} agricultural records")

if page == "Dashboard":
    a,b,c,d,e = st.columns(5)
    a.metric("Total Farms", f"{len(f):,}")
    b.metric("Avg Yield", f"{f.Yield_Tonnes_Ha.mean():.2f} t/ha")
    c.metric("Avg Production", f"{f.Production_Tonnes.mean():.2f} t")
    d.metric("Avg Profit", money(f.Profit_INR.mean()))
    e.metric("Water Efficiency", f"{f.Water_Efficiency_t_per_1000m3.mean():.2f}")

    x,y = st.columns(2)
    with x:
        s = f.groupby("Season",as_index=False).Yield_Tonnes_Ha.mean()
        chart(px.bar(s,x="Season",y="Yield_Tonnes_Ha",title="Average Yield by Season",
                     labels={"Yield_Tonnes_Ha":"Yield (Tonnes/Ha)"}))
    with y:
        c = f.groupby("Crop",as_index=False).Profit_INR.mean().sort_values("Profit_INR")
        chart(px.bar(c,x="Profit_INR",y="Crop",orientation="h",title="Average Profit by Crop",
                     labels={"Profit_INR":"Profit (INR)"}))

    x,y = st.columns(2)
    with x:
        chart(px.scatter(f,x="Water_Used_m3",y="Water_Efficiency_t_per_1000m3",color="Season",
                         hover_data=["State","Crop","Profit_INR"],title="Water Usage vs Water Efficiency",
                         labels={"Water_Used_m3":"Water Used (m³)","Water_Efficiency_t_per_1000m3":"Efficiency"}))
    with y:
        chart(px.scatter(f,x="Yield_Tonnes_Ha",y="Profit_INR",color="Crop",
                         hover_data=["State","Season"],title="Yield vs Profitability",
                         labels={"Yield_Tonnes_Ha":"Yield (Tonnes/Ha)","Profit_INR":"Profit (INR)"}))

elif page == "Seasonal Performance":
    st.header("Seasonal Performance")
    s = f.groupby("Season",as_index=False).agg(
        Yield=("Yield_Tonnes_Ha","mean"), Production=("Production_Tonnes","mean"),
        Water=("Water_Used_m3","mean"), Efficiency=("Water_Efficiency_t_per_1000m3","mean"),
        Profit=("Profit_INR","mean"))
    st.dataframe(s.style.format({"Yield":"{:.2f}","Production":"{:.2f}","Water":"{:,.0f}","Efficiency":"{:.2f}","Profit":"₹{:,.0f}"}),
                 use_container_width=True, hide_index=True)
    x,y = st.columns(2)
    with x: chart(px.bar(s,x="Season",y="Yield",title="Average Yield Across Seasons"))
    with y: chart(px.bar(s,x="Season",y="Profit",title="Average Profit Across Seasons"))

elif page == "Crop Analysis":
    st.header("Crop Analysis")
    c = f.groupby("Crop",as_index=False).agg(Yield=("Yield_Tonnes_Ha","mean"),Water=("Water_Used_m3","mean"),
        Efficiency=("Water_Efficiency_t_per_1000m3","mean"),Profit=("Profit_INR","mean")).sort_values("Profit",ascending=False)
    st.dataframe(c.style.format({"Yield":"{:.2f}","Water":"{:,.0f}","Efficiency":"{:.2f}","Profit":"₹{:,.0f}"}),
                 use_container_width=True, hide_index=True)
    x,y = st.columns(2)
    with x: chart(px.bar(c.sort_values("Yield"),x="Yield",y="Crop",orientation="h",title="Average Yield by Crop"))
    with y: chart(px.bar(c,x="Profit",y="Crop",orientation="h",title="Average Profit by Crop"))

elif page == "Water & Irrigation":
    st.header("Water & Irrigation")
    i = f.groupby("Irrigation_Method",as_index=False).agg(Water=("Water_Used_m3","mean"),
        Efficiency=("Water_Efficiency_t_per_1000m3","mean"),Yield=("Yield_Tonnes_Ha","mean"))
    x,y = st.columns(2)
    with x: chart(px.bar(i,x="Irrigation_Method",y="Efficiency",title="Water Efficiency by Irrigation Method"))
    with y: chart(px.bar(i,x="Irrigation_Method",y="Water",title="Average Water Usage by Irrigation Method"))
    chart(px.scatter(f,x="Water_Used_m3",y="Yield_Tonnes_Ha",color="Irrigation_Method",
                     hover_data=["Crop","Season","State"],title="Water Usage vs Yield"))

elif page == "Profitability":
    st.header("Profitability")
    x,y = st.columns(2)
    with x:
        s=f.groupby("Season",as_index=False).Profit_INR.mean()
        chart(px.bar(s,x="Season",y="Profit_INR",title="Average Profit by Season"))
    with y:
        c=f.groupby("Crop",as_index=False).Profit_INR.mean().sort_values("Profit_INR")
        chart(px.bar(c,x="Profit_INR",y="Crop",orientation="h",title="Average Profit by Crop"))
    chart(px.scatter(f,x="Production_Tonnes",y="Profit_INR",color="Season",
                     hover_data=["Crop","State"],title="Production vs Profitability"))

else:
    st.header("Regional Insights")
    s=f.groupby("State",as_index=False).agg(Yield=("Yield_Tonnes_Ha","mean"),
        Production=("Production_Tonnes","mean"),Profit=("Profit_INR","mean")).sort_values("Profit",ascending=False)
    st.dataframe(s.style.format({"Yield":"{:.2f}","Production":"{:.2f}","Profit":"₹{:,.0f}"}),
                 use_container_width=True, hide_index=True)
    x,y=st.columns(2)
    with x: chart(px.bar(s,x="State",y="Yield",title="Average Yield by State"))
    with y: chart(px.bar(s,x="State",y="Profit",title="Average Profit by State"))

st.divider()
st.caption("AgriPulse • Seasonal Agriculture Performance Analysis • Python + Streamlit")
