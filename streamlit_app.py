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
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>💰 Weekly Cashflow Forecast Dashboard</h1>", unsafe_allow_html=True)

# Sample template download
with st.expander("📥 Download Template"):
    sample_data = pd.DataFrame({
        "Party Type": ["Supplier", "Customer"],
        "Party Name": ["ABC Ltd", "XYZ Inc"],
        "Due Date": ["2025-05-13", "2025-05-10"],
        "Expected Date": ["2025-05-20", "2025-05-14"],
        "Amount": [-10000, 12000]
    })
    st.download_button(
        "Download CSV Template",
        data=sample_data.to_csv(index=False).encode(),
        file_name="cashflow_template.csv",
        mime="text/csv"
    )

# Upload
st.markdown("### 📤 Upload Your Cashflow Data")
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    # Load and normalize columns
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip().str.lower()

    # Validate required columns
    required_columns = {"party type", "party name", "due date", "expected date", "amount"}
    if not required_columns.issubset(set(df.columns)):
        st.error(f"Uploaded file is missing required columns: {required_columns - set(df.columns)}")
        st.stop()

    # Date handling
    df["due date"] = pd.to_datetime(df["due date"])
    df["expected date"] = pd.to_datetime(df["expected date"])
    df["allocation date"] = df[["due date", "expected date"]].max(axis=1)
    df["week"] = df["allocation date"].dt.to_period("W").apply(lambda r: r.start_time)

    def format_week_range(week_start):
        week_end = week_start + pd.Timedelta(days=6)
        return f"{week_start.day} {week_start.strftime('%b')} - {week_end.day} {week_end.strftime('%b')}"

    df["week range"] = df["week"].apply(format_week_range)

    # Build complete party-week matrix
    all_parties = df[["party type", "party name"]].drop_duplicates()
    all_weeks = pd.DataFrame(df["week range"].unique(), columns=["week range"])
    all_cross = all_parties.merge(all_weeks, how="cross")

    pivot_df = df.groupby(["party type", "party name", "week range"], as_index=False)["amount"].sum()
    complete_df = all_cross.merge(pivot_df, on=["party type", "party name", "week range"], how="left").fillna(0)

    # Pivot to detailed table
    wide_df = complete_df.pivot_table(
        index=["party type", "party name"],
        columns="week range",
        values="amount",
        aggfunc="sum",
        fill_value=0
    )

    # Add net cashflow row
    net_cashflow = wide_df.sum(numeric_only=True)
    net_row = pd.DataFrame([net_cashflow], index=pd.MultiIndex.from_tuples([("Net Cashflow", "")]))
    final_table = pd.concat([wide_df, net_row])

    # Display
    st.markdown("### 📋 Detailed Weekly Cashflow")
    st.dataframe(final_table.style.format("{:,.0f}"), use_container_width=True)

    # Chart
    st.markdown("### 📈 Weekly Net Cashflow Trend")
    net_df = net_cashflow.reset_index()
    net_df.columns = ["Week", "Net Cashflow"]
    net_df["Week"] = pd.Categorical(net_df["Week"], categories=net_df["Week"], ordered=True)

    chart = alt.Chart(net_df).mark_bar().encode(
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

    st.altair_chart((chart + labels).properties(height=300), use_container_width=True)

    # Excel Export
    towrite = BytesIO()
    with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer:
        final_table.to_excel(writer, sheet_name='Forecast')
    st.download_button("📤 Download Forecast Excel", towrite.getvalue(), file_name="cashflow_forecast.xlsx")

else:
    st.info("Please upload a valid file to begin.")
