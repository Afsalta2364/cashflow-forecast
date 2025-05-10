import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# Configure page
st.set_page_config(page_title="Cashflow Forecast", layout="wide")

# Style
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

st.markdown("<h1>💰 Weekly Cashflow Forecast Dashboard</h1>", unsafe_allow_html=True)

# Downloadable template
with st.expander("📥 Download Template"):
    sample_data = pd.DataFrame({
        "Party Type": ["Supplier", "Customer"],
        "Party Name": ["ABC Ltd", "XYZ Inc"],
        "Due Date": ["2025-05-13", "2025-05-10"],
        "Expected Date": ["2025-05-20", "2025-05-14"],
        "Amount": [-10000, 12000]
    })
    st.download_button("Download CSV Template",
                       sample_data.to_csv(index=False).encode(),
                       file_name="cashflow_template.csv",
                       mime="text/csv")

# Upload file
st.markdown("### 📤 Upload Cashflow Data")
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    # Load data
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
    df["Due Date"] = pd.to_datetime(df["Due Date"])
    df["Expected Date"] = pd.to_datetime(df["Expected Date"])

    # Allocation logic
    df["Allocation Date"] = df[["Due Date", "Expected Date"]].max(axis=1)
    df["Week"] = df["Allocation Date"].dt.to_period("W").apply(lambda r: r.start_time)

    def format_week_range(week_start):
        week_end = week_start + pd.Timedelta(days=6)
        return f"{week_start.day} {week_start.strftime('%b')} - {week_end.day} {week_end.strftime('%b')}"

    df["Week Range"] = df["Week"].apply(format_week_range)

    # Pivot table
    detailed = df.pivot_table(
        index=["Party Type", "Party Name"],
        columns="Week Range",
        values="Amount",
        aggfunc="sum",
        fill_value=0
    )

    # Calculate Net Cashflow per week
    net_cashflow = detailed.sum(numeric_only=True)

    # Reindex as a multi-index row and append
    net_row = pd.DataFrame([net_cashflow], index=pd.MultiIndex.from_tuples([("Net Cashflow", "")]))
    detailed = pd.concat([detailed, net_row])

    # Show data
    st.markdown("### 📋 Detailed Weekly Cashflow")
    st.dataframe(detailed.style.format("{:,.0f}"), use_container_width=True)

    # Net Cashflow Chart
    st.markdown("### 📈 Weekly Net Cashflow Trend")
    net_df = net_cashflow.reset_index()
    net_df.columns = ["Week", "Net Cashflow"]
    fig, ax = plt.subplots()
    ax.bar(net_df["Week"], net_df["Net Cashflow"], color="#4CAF50")
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # Export
    towrite = BytesIO()
    with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer:
        detailed.to_excel(writer, sheet_name='Forecast')
    st.download_button("📤 Download Forecast Excel", towrite.getvalue(), file_name="cashflow_forecast.xlsx")

else:
    st.info("Please upload your file to get started.")
