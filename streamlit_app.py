import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO

# Page config
st.set_page_config(page_title="Cashflow Forecast", layout="wide")

# Styling
st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    .block-container { padding: 2rem; }
    h1 { color: #004085; }
    .card {
        background-color: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1>💰 Weekly Cashflow Forecast Dashboard</h1>", unsafe_allow_html=True)

# Template Download
with st.expander("📥 Download Template"):
    sample_data = pd.DataFrame({
        "Party Type": ["Supplier", "Customer", "Supplier"],
        "Party Name": ["ABC Ltd", "XYZ Inc", "RST Ltd"],
        "Due Date": ["2025-05-13", "2025-05-10", "2025-05-22"],
        "Expected Date": ["2025-05-20", "2025-05-14", "2025-05-28"],
        "Amount": [-10000, 12000, -5000]
    })
    st.download_button(
        "Download CSV Template",
        data=sample_data.to_csv(index=False).encode(),
        file_name="cashflow_template.csv",
        mime="text/csv"
    )

# File Upload
st.markdown("### 📤 Upload Cashflow Data")
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
    df["Due Date"] = pd.to_datetime(df["Due Date"])
    df["Expected Date"] = pd.to_datetime(df["Expected Date"])
    df["Allocation Date"] = df[["Due Date", "Expected Date"]].max(axis=1)
    df["Week"] = df["Allocation Date"].dt.to_period("W").apply(lambda r: r.start_time)

    def format_week_range(week_start):
        week_end = week_start + pd.Timedelta(days=6)
        return f"{week_start.day} {week_start.strftime('%b')} - {week_end.day} {week_end.strftime('%b')}"

    df["Week Range"] = df["Week"].apply(format_week_range)

    # Summarize by Party + Week
    pivot_df = df.groupby(["Party Type", "Party Name", "Week Range"])["Amount"].sum().reset_index()

    # Pivot to wide format
    detailed = pivot_df.pivot_table(
        index=["Party Type", "Party Name"],
        columns="Week Range",
        values="Amount",
        aggfunc="sum",
        fill_value=0
    )

    # Calculate Net Cashflow
    net_cashflow = detailed.sum(numeric_only=True)
    net_row = pd.DataFrame([net_cashflow], index=pd.MultiIndex.from_tuples([("Net Cashflow", "")]))
    detailed = pd.concat([detailed, net_row])

    # Display Table
    st.markdown("### 📋 Detailed Weekly Cashflow")
    st.dataframe(detailed.style.format("{:,.0f}"), use_container_width=True)

    # Net Cashflow Chart
    st.markdown("### 📈 Weekly Net Cashflow Trend")
    net_df = net_cashflow.reset_index()
    net_df.columns = ["Week", "Net Cashflow"]
    net_df["Week"] = pd.Categorical(net_df["Week"], categories=net_df["Week"], ordered=True)

    bar_chart = alt.Chart(net_df).mark_bar().encode(
        x=alt.X("Week:N", title=None),
        y=alt.Y("Net Cashflow:Q", title="Net Cashflow"),
        color=alt.condition(
            alt.datum["Net Cashflow"] > 0,
            alt.value("#4CAF50"),
            alt.value("#EF5350")
        ),
        tooltip=["Week", "Net Cashflow"]
    )

    labels = alt.Chart(net_df).mark_text(
        align="center",
        baseline="bottom",
        dy=-5,
        fontSize=12
    ).encode(
        x="Week:N",
        y="Net Cashflow:Q",
        text=alt.Text("Net Cashflow:Q", format=",.0f"),
        color=alt.value("black")
    )

    final_chart = (bar_chart + labels).properties(
        width="container",
        height=300
    ).configure_axis(
        labelAngle=0
    ).configure_view(
        stroke=None
    )

    st.altair_chart(final_chart, use_container_width=True)

    # Export to Excel
    towrite = BytesIO()
    with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer:
        detailed.to_excel(writer, sheet_name='Forecast')
    st.download_button("📤 Download Forecast Excel", towrite.getvalue(), file_name="cashflow_forecast.xlsx")

else:
    st.info("Please upload your file to see the forecast.")
