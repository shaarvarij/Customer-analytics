import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

DB_PATH = "data/analytics.db"

st.set_page_config(
    page_title="Customer Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_data():
    con = duckdb.connect(DB_PATH, read_only=True)
    customers  = con.execute("SELECT * FROM customer_order_summary").df()
    segments   = con.execute("SELECT * FROM customer_segments").df()
    churn      = con.execute("SELECT * FROM churn_predictions").df()
    forecast   = con.execute("SELECT * FROM revenue_forecast").df()
    daily_rev  = con.execute("SELECT * FROM daily_revenue ORDER BY order_date").df()
    con.close()
    return customers, segments, churn, forecast, daily_rev

customers, segments, churn, forecast, daily_rev = load_data()

# ── Sidebar ──────────────────────────────────────────
st.sidebar.title("📊 Customer Analytics")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate", [
    "🏠 Overview",
    "👥 Segments",
    "⚠️ Churn Risk",
    "📈 Revenue Forecast"
])

# ── Overview ─────────────────────────────────────────
if page == "🏠 Overview":
    st.title("🏠 Business Overview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Customers",  f"{len(customers):,}")
    col2.metric("Total Revenue",    f"${customers['total_spent'].sum():,.0f}")
    col3.metric("Avg Order Value",  f"${customers['total_spent'].mean():,.0f}")
    col4.metric("High Risk Customers", f"{len(churn[churn['churn_risk']=='High']):,}")

    st.markdown("---")

    # Daily revenue chart
    st.subheader("Daily Revenue (Last 90 Days)")
    daily_rev['order_date'] = pd.to_datetime(daily_rev['order_date'])
    last_90 = daily_rev.tail(90)
    fig = px.line(last_90, x='order_date', y='revenue',
                  labels={'order_date': 'Date', 'revenue': 'Revenue ($)'},
                  color_discrete_sequence=['#636EFA'])
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

    # Top customers
    st.subheader("Top 10 Customers by Revenue")
    top10 = customers.nlargest(10, 'total_spent')[['name','email','total_orders','total_spent']]
    top10.columns = ['Name', 'Email', 'Orders', 'Total Spent ($)']
    top10['Total Spent ($)'] = top10['Total Spent ($)'].round(2)
    st.dataframe(top10, use_container_width=True)

# ── Segments ─────────────────────────────────────────
elif page == "👥 Segments":
    st.title("👥 Customer Segments")

    col1, col2 = st.columns(2)

    with col1:
        seg_counts = segments['segment'].value_counts().reset_index()
        seg_counts.columns = ['Segment', 'Count']
        fig = px.pie(seg_counts, names='Segment', values='Count',
                     title='Customer Distribution',
                     color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(seg_counts, x='Segment', y='Count',
                     title='Segment Sizes',
                     color='Segment',
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Segment RFM Analysis")
    rfm = segments.groupby('segment').agg(
        avg_recency=('recency','mean'),
        avg_frequency=('frequency','mean'),
        avg_monetary=('monetary','mean'),
        count=('customer_id','count')
    ).round(1).reset_index()
    rfm.columns = ['Segment','Avg Recency (days)','Avg Frequency','Avg Monetary ($)','Count']
    st.dataframe(rfm, use_container_width=True)

# ── Churn ─────────────────────────────────────────────
elif page == "⚠️ Churn Risk":
    st.title("⚠️ Churn Risk Analysis")

    col1, col2, col3 = st.columns(3)
    col1.metric("High Risk",   f"{len(churn[churn['churn_risk']=='High']):,}",   delta="Needs attention", delta_color="inverse")
    col2.metric("Medium Risk", f"{len(churn[churn['churn_risk']=='Medium']):,}")
    col3.metric("Low Risk",    f"{len(churn[churn['churn_risk']=='Low']):,}",    delta="Healthy", delta_color="normal")

    col1, col2 = st.columns(2)

    with col1:
        risk_counts = churn['churn_risk'].value_counts().reset_index()
        risk_counts.columns = ['Risk Level', 'Count']
        fig = px.pie(risk_counts, names='Risk Level', values='Count',
                     title='Churn Risk Distribution',
                     color='Risk Level',
                     color_discrete_map={'High':'#EF553B','Medium':'#FFA15A','Low':'#00CC96'})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.histogram(churn, x='churn_probability', nbins=30,
                           title='Churn Probability Distribution',
                           color_discrete_sequence=['#AB63FA'])
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("High Risk Customers")
    high_risk = churn[churn['churn_risk']=='High'][
        ['customer_id','recency','frequency','monetary','churn_probability']
    ].sort_values('churn_probability', ascending=False).head(20)
    high_risk['churn_probability'] = (high_risk['churn_probability']*100).round(1).astype(str) + '%'
    high_risk.columns = ['Customer ID','Days Since Purchase','Orders','Total Spent ($)','Churn Probability']
    st.dataframe(high_risk, use_container_width=True)

# ── Forecast ──────────────────────────────────────────
elif page == "📈 Revenue Forecast":
    st.title("📈 30-Day Revenue Forecast")

    total_forecast = forecast['predicted_revenue'].sum()
    avg_daily      = forecast['predicted_revenue'].mean()
    st.metric("Projected 30-Day Revenue", f"${total_forecast:,.0f}")
    st.metric("Avg Daily Revenue",        f"${avg_daily:,.0f}")

    forecast['date'] = pd.to_datetime(forecast['date'])
    fig = go.Figure([
        go.Scatter(x=forecast['date'], y=forecast['upper_bound'],
                   fill=None, mode='lines', line_color='lightblue', name='Upper bound'),
        go.Scatter(x=forecast['date'], y=forecast['lower_bound'],
                   fill='tonexty', mode='lines', line_color='lightblue',
                   fillcolor='rgba(100,149,237,0.2)', name='Lower bound'),
        go.Scatter(x=forecast['date'], y=forecast['predicted_revenue'],
                   mode='lines+markers', line=dict(color='#636EFA', width=2),
                   name='Forecast'),
    ])
    fig.update_layout(
        title='Revenue Forecast with Confidence Intervals',
        xaxis_title='Date', yaxis_title='Revenue ($)',
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Daily Forecast Breakdown")
    display = forecast.copy()
    display['date'] = display['date'].dt.strftime('%Y-%m-%d')
    display.columns = ['Date','Predicted Revenue ($)','Lower Bound ($)','Upper Bound ($)']
    display = display.round(2)
    st.dataframe(display, use_container_width=True)