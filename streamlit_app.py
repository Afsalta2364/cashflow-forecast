import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# --- Layout and style ---
st.set_page_config(page_title="Cashflow Forecast", layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #f4f6f9;
    }
    .block-container {
        padding: 2rem;
    }
    h1 {
        color: #004085;
    }
    .card {
        background-color: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- App Title ---
st.markdown("<h1>💰 Weekly Cashflow Forecast Dashboard</h1>", unsafe_allow_html=True)

# --- Downloadable Template ---
with st.expander("📥 Download Data Template", expanded=False):
    sample_data = pd.DataFrame({
        "Party Type": ["Supplier", "Customer"],
        "Party Name": ["ABC Ltd", "XYZ Inc"],
        "Due Date": ["2025-05-13", "2025-05-10"],
        "Expected Date": ["2025-05-20", "2025-05-14"],
        "Amount": [-10000, 12000]
    })
    st.download_button(
        "Download CSV Template",
        sample_data.to_csv(index=False).encode(),
        file_name="cashflow_template.csv",
        mime="text/csv"
    )

# --- File Upload ---
st.markdown("### 📤 Upload Your Cashflow Data")
uploaded_file = st.file_uploader("Choose your CSV or Excel file", type=["csv", "xlsx"])

# --- Process Uploaded File ---
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

    # Pivot table
    detailed_breakup = df.pivot_table(
        index=["Party Type", "Party Name"],
        columns="Week Range",
        values="Amount",
        aggfunc="sum",
        fill_value=0
    )

    # Net cashflow row
    try:
        net_cashflow = detailed_breakup.loc["Customer"].sum() + detailed_breakup.loc["Supplier"].sum()
    except KeyError:
        net_cashflow = detailed_breakup.sum()
    detailed_breakup.loc[("Net Cashflow", "")] = net_cashflow

    # Show data in styled container
    st.markdown("<div class='card'><h3>📋 Detailed Weekly Cashflow</h3>", unsafe_allow_html=True)
    st.dataframe(
        detailed_breakup.style.format("{:,.0f}"),
        use_container_width=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Chart section
    st.markdown("<div class='card'><h3>📈 Weekly Net Cashflow Trend</h3>", unsafe_allow_html=True)
    fig, ax = plt.subplots()
    net_cashflow_chart = net_cashflow.reset_index()
    net_cashflow_chart.columns = ["Week", "Net"]
    ax.bar(net_cashflow_chart["Week"], net_cashflow_chart["Net"])
    ax.set_ylabel("Net Cashflow")
    ax.set_title("Net Cashflow by Week")
    plt.xticks(rotation=45)
    st.pyplot(fig)
    st.markdown("</div>", unsafe_allow_html=True)

    # Export
    towrite = BytesIO()
    with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer:
        detailed_breakup.to_excel(writer, sheet_name='Forecast')
    st.download_button("📤 Download Forecast Excel", towrite.getvalue(), file_name="cashflow_forecast.xlsx")

else:
    st.info("Please upload your file to generate the forecast.")
