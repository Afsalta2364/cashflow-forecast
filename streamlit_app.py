import streamlit as st
import pandas as pd
from io import BytesIO

# Page configuration
st.set_page_config(page_title="Cashflow Forecast Dashboard", layout="wide")

# Styles
st.markdown("""
    <style>
    .main { background-color: #f7f9fc; }
    h1, h2, h3 { color: #1f77b4; }
    .css-1d391kg { background-color: #ffffff; padding: 1rem; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# App title
st.title("📊 Weekly Cashflow Forecast Tool")

st.markdown("Upload a cashflow file based on the template below and get a clean, detailed weekly forecast.")

# Template
sample_data = pd.DataFrame({
    "Party Type": ["Supplier", "Customer"],
    "Party Name": ["ABC Ltd", "XYZ Inc"],
    "Due Date": ["2025-05-13", "2025-05-10"],
    "Expected Date": ["2025-05-20", "2025-05-14"],
    "Amount": [-10000, 12000]
})
csv = sample_data.to_csv(index=False).encode()
st.download_button("📥 Download Template", data=csv, file_name="cashflow_template.csv", mime="text/csv")

# Upload section
st.markdown("### 📤 Upload Your Data")
uploaded_file = st.file_uploader("Upload a CSV or Excel file based on the template above", type=["csv", "xlsx"])

if uploaded_file:
    # Read data
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)

    # Process dates
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
    detailed_breakup = df.pivot_table(
        index=["Party Type", "Party Name"],
        columns="Week Range",
        values="Amount",
        aggfunc="sum",
        fill_value=0
    )

    # Add Net Cashflow row
    try:
        net_cashflow = detailed_breakup.loc["Customer"].sum() + detailed_breakup.loc["Supplier"].sum()
    except KeyError:
        net_cashflow = detailed_breakup.sum()
    detailed_breakup.loc[("Net Cashflow", "")] = net_cashflow

    # Display
    st.markdown("### 💸 Detailed Weekly Cashflow View")
    st.dataframe(detailed_breakup.style
                 .format("{:,.0f}")
                 .background_gradient(cmap="Greens", axis=1)
                 .set_table_styles([{
                     'selector': 'th',
                     'props': [('background-color', '#e3f2fd')]
                 }])
    )

    # Chart
    st.markdown("### 📈 Net Cashflow Over Time")
    net_cashflow_chart = net_cashflow.reset_index()
    net_cashflow_chart.columns = ["Week Range", "Net Cashflow"]
    net_cashflow_chart = net_cashflow_chart.set_index("Week Range")
    st.bar_chart(net_cashflow_chart)

    # Export to Excel
    towrite = BytesIO()
    output = pd.ExcelWriter(towrite, engine='xlsxwriter')
    detailed_breakup.to_excel(output, sheet_name='Cashflow Forecast')
    output.close()
    st.download_button("📤 Download Forecast as Excel", data=towrite.getvalue(), file_name="cashflow_forecast.xlsx")

else:
    st.info("Awaiting file upload to show forecast view.")
