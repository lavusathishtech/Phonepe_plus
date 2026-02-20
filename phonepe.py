import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import json

# ================= PAGE CONFIG =================
st.set_page_config(page_title="PhonePe Pulse | THE BEAT OF PROGRESS", layout="wide")

# ================= DATABASE LOAD =================
@st.cache_data
def load_txn():
    conn = psycopg2.connect(
        host="localhost", database="phonepe_data",
        user="postgres", password="root", port="5432"
    )
    df = pd.read_sql("SELECT * FROM Agg_Transaction", conn)
    conn.close()
    return df

@st.cache_data
def load_user():
    conn = psycopg2.connect(
        host="localhost", database="phonepe_data",
        user="postgres", password="root", port="5432"
    )
    df = pd.read_sql("SELECT * FROM Agg_user", conn)
    conn.close()
    return df

@st.cache_data
def load_ins():
    conn = psycopg2.connect(
        host="localhost", database="phonepe_data",
        user="postgres", password="root", port="5432"
    )
    df = pd.read_sql("SELECT * FROM aggregated_Insurance", conn)
    conn.close()
    return df

txn_df = load_txn()
user_df = load_user()
ins_df = load_ins()



# ================= SIDEBAR =================
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
   ["Home","💰 Transactions", "📱 Users & Devices", "📈 Market Expansion",
     "🛡 Insurance", "👥 User Growth"]
)

st.sidebar.header("Filters")
state = st.sidebar.selectbox("State", ["All"] + sorted(txn_df["state"].unique()))
year = st.sidebar.selectbox("Year", ["All"] + sorted(txn_df["year"].unique()))
quarter = st.sidebar.selectbox("Quarter", ["All"] + sorted(txn_df["quarter"].unique()))



# ================= FILTER =================
def filter_df(df):
    f = df.copy()
    if state != "All": f = f[f["state"] == state]
    if year != "All": f = f[f["year"] == year]
    if quarter != "All": f = f[f["quarter"] == quarter]
    return f

filtered = txn_df[
    (txn_df["year"] == year) &
    (txn_df["quarter"] == quarter)
]


# =====================================================
# 💰 CASE 1 — TRANSACTION
# =====================================================
# =====================================================
# 🏠 HOME — INDIA HEATMAP
# =====================================================

# =====================================================
# 🏠 HOME — FULL INDIA MAP
# =====================================================
if page == "Home":

    st.title("📱 PhonePe Pulse Analytics")
    st.subheader("In State Wise Transaction Map")

    df = filter_df(txn_df)

    # Aggregate state-wise
    df = df.groupby("state")["transaction_amount"].sum().reset_index()

    # Clean names
    df["state"] = (
        df["state"]
        .str.replace("_", " ")
        .str.title()
        .str.strip()
    )

    # 👉 IMPORTANT: ensure ALL states appear (even if no data)
    all_states = [
        "Andaman & Nicobar Island","Andhra Pradesh","Arunachal Pradesh","Assam",
        "Bihar","Chandigarh","Chhattisgarh","Dadra & Nagar Haveli & Daman & Diu",
        "Delhi","Goa","Gujarat","Haryana","Himachal Pradesh","Jammu & Kashmir",
        "Jharkhand","Karnataka","Kerala","Ladakh","Lakshadweep","Madhya Pradesh",
        "Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland","Odisha",
        "Puducherry","Punjab","Rajasthan","Sikkim","Tamil Nadu","Telangana",
        "Tripura","Uttar Pradesh","Uttarakhand","West Bengal"
    ]

    full_df = pd.DataFrame({"state": all_states})
    df = full_df.merge(df, on="state", how="left")
    df["transaction_amount"] = df["transaction_amount"].fillna(0)

    # Map
    fig = px.choropleth(
        df,
        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
        featureidkey="properties.ST_NM",
        locations="state",
        color="transaction_amount",
        hover_name="state",
        color_continuous_scale="Viridis",
        height=900
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False,
        showcountries=False,
        showcoastlines=False,
        projection_type="mercator"
    )

    st.plotly_chart(fig, use_container_width=True)
# ======
    
if page == "💰 Transactions":

    df = filter_df(txn_df)

    st.subheader("Top States")
    fig = px.bar(df.groupby("state")["transaction_amount"].sum().reset_index(),
                 x="state", y="transaction_amount", color="transaction_amount")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Quarter Contribution")
    q = df.groupby("quarter")["transaction_amount"].sum().reset_index()
    fig = px.pie(q, values="transaction_amount", names="quarter", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Transaction Type")
    tt = df.groupby("transaction_type")["transaction_amount"].sum().reset_index()
    fig = px.bar(tt, x="transaction_type", y="transaction_amount", color="transaction_amount")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Year Growth")
    yg = txn_df.groupby("year")["transaction_amount"].sum().reset_index()
    fig = px.line(yg, x="year", y="transaction_amount", markers=True)
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# 📱 CASE 2 — USER & DEVICE
# =====================================================
elif page == "📱 Users & Devices":

    df = filter_df(user_df)

    # Ensure numeric
    df["registered_users"] = pd.to_numeric(df["registered_users"], errors="coerce")
    df["app_opens"] = pd.to_numeric(df["app_opens"], errors="coerce")

    # =================================================
    # TOP DEVICE BRANDS
    # =================================================
    st.subheader("🏆 Top Device Brands")

    top_brand = (
        df.groupby("brand")["registered_users"]
        .sum()
        .reset_index()
        .sort_values("registered_users", ascending=False)
    )

    fig1 = px.bar(
        top_brand,
        x="brand",
        y="registered_users",
        color="registered_users",
        color_continuous_scale="Purples",
        title="Top Device Brands by Users"
    )

    st.plotly_chart(fig1, use_container_width=True)

    # =================================================
    # ENGAGEMENT RATE
    # =================================================
    st.subheader("📊 Engagement Rate")

    eng = (
        df.groupby("brand")[["registered_users","app_opens"]]
        .sum()
        .reset_index()
    )

    eng["Engagement_Rate"] = eng["app_opens"] / eng["registered_users"]

    fig2 = px.bar(
        eng,
        x="brand",
        y="Engagement_Rate",
        color="Engagement_Rate",
        color_continuous_scale="Turbo",
        title="User Engagement Rate"
    )

    st.plotly_chart(fig2, use_container_width=True)


# =====================================================
# 📈 CASE 3 — MARKET EXPANSIONlif page == "📱 Users & Devices":

# =====================================================
elif page == "📈 Market Expansion":

    df = filter_df(txn_df)

    st.subheader("Top Performing States")
    fig = px.bar(df.groupby("state")["transaction_amount"].sum().reset_index(),
                 x="state", y="transaction_amount", color="transaction_amount")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 5 Growth Trend")
    sy = txn_df.groupby(["state","year"])["transaction_amount"].sum().reset_index()
    top5 = txn_df.groupby("state")["transaction_amount"].sum().nlargest(5).index
    sy5 = sy[sy["state"].isin(top5)]
    fig = px.line(sy5, x="year", y="transaction_amount", color="state", markers=True)
    st.plotly_chart(fig, use_container_width=True)

# 🛡 CASE 4 — INSURANCE
# =====================================================
elif page == "🛡 Insurance":

    df = filter_df(ins_df)

    st.subheader("Top Insurance States")
    fig = px.bar(df.groupby("state")["insurance_amount"].sum().reset_index(),
                 x="state", y="insurance_amount", color="insurance_amount")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Insurance Growth")
    yg = ins_df.groupby("year")["insurance_amount"].sum().reset_index()
    fig = px.line(yg, x="year", y="insurance_amount", markers=True)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Insurance Type Performance")
    tp = df.groupby("insurance_type")["insurance_amount"].sum().reset_index()
    fig = px.bar(tp, x="insurance_type", y="insurance_amount", color="insurance_amount")
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# 👥 CASE 5 — USER GROWTH
# =====================================================
elif page == "👥 User Growth":

    df = filter_df(user_df)

    st.subheader("Top States by Users")
    fig = px.bar(df.groupby("state")["registered_users"].sum().reset_index(),
                 x="state", y="registered_users", color="registered_users")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("App Opens")
    fig = px.bar(df.groupby("state")["app_opens"].sum().reset_index(),
                 x="state", y="app_opens", color="app_opens")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("User Growth")
    ug = user_df.groupby("year")["registered_users"].sum().reset_index()
    fig = px.line(ug, x="year", y="registered_users", markers=True)
    st.plotly_chart(fig, use_container_width=True)

# ================= FOOTER =================
st.markdown("---")
st.caption("💜 PhonePe Pulse Clone | Streamlit • Plotly • PostgreSQL")