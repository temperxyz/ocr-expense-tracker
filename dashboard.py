import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_all_expenses

def show_dashboard():
    st.header("Spending Dashboard")

    rows = get_all_expenses()
    if not rows:
        st.info("No expenses logged yet. Add some receipts first!")
        return
    df = pd.DataFrame([dict(row) for row in rows]) 
    df["date"]=pd.to_datetime(df["date"],errors="coerce")#anydate pandas cant parse is converted to Nat instead of crashing
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Spend",f"${df['total'].sum():.2f}")# gets the total
    top_cat=df.groupby("category")['total'].sum().idxmax() #group by category and takes the sum in each category

    col2.metric("Top Category",top_cat)
    top_merchant=df.groupby("merchant")["total"].sum().idxmax()

    col3.metric("Top Merchant",top_merchant)
    st.subheader("Spend by Category")
    cat_df = df.groupby("category", as_index=False)["total"].sum()
    fig_pie = px.pie(cat_df, names="category", values="total", hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)
 
    st.subheader("Spending Over Time")
    df_valid = df.dropna(subset=["date"])#Drop null vals
    trend_df = (
        df_valid.set_index("date")
        .resample("W")["total"]#Buckets into weekly group
        .sum()#compute total per weekly bucket
        .reset_index()
    )
    fig_line = px.line(trend_df, x="date", y="total", markers=True)
    st.plotly_chart(fig_line, use_container_width=True)
 
    with st.expander("See all expenses"):
        st.dataframe(df[["date", "merchant", "total", "category"]])
