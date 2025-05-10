import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO

# Page setup
st.set_page_config(page_title="Cashflow Forecast", layout="wide")
st.title("💰 Weekly Cashflow Forecast Dashboard")

# --- 1. Sample Template Download ---
with st.expander("📥 Download Sample Template (for reference)"):
    sample_data = pd.DataFrame({
        "Party Type": ["Supplier", "Customer"],
        "Party Name": ["ABC Ltd", "XYZ Inc"],
        "Due Date": ["2025-05-13", "2025-05-10"],
        "Expected Date": ["2025-05-20", "2025-05-14"],
        "Amount": [-10000, 12000]
    })
    st.download_button(
        label="Download Template CSV",
        data=sample_data.to_csv(index=False).encode(),
        file_name="cashflow_template.csv",
        mime="text/csv"
    )

# --- 2. Upload Section ---
uploaded_file = st.file_uploader("📤 Upload your cashflow data (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file:
    # --- 3. File Load and Normalization ---
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.replace('\ufeff', '')  # remove BOM
    df.columns = df.columns.str.strip().str.lower()

    st.success(f"✅ Uploaded: `{uploaded_file.name}` — {df.shape[0]} rows, {df.shape[1]} columns")

    # --- 4. Display Uploaded Data Preview ---
    st.subheader("📄 Uploaded File Preview")
    st.dataframe(df.head())
    st.write("📌 Column Names Detected:", df.columns.tolist())

    # --- 5. Validate Required Columns ---
    required_cols = {"party type", "party name", "due date", "expected date", "amount"}
    if not required_cols.issubset(df.columns):
        st.error(f"❌ Missing required columns: {required_cols - set(df.columns)}")
        st.stop()

    # --- 6. Allocation + Week Logic ---
    df["due date"] = pd.to_datetime(df["due date"])
    df["expected date"] = pd.to_datetime(df["expected date"])
    df["allocation date"] = df[["due date", "expected date"]].max(axis=1)
    df["week"] = df["allocation date"].dt.to_period("W").apply(lambda r: r.start_time)

    def format_week_range(start):
        end = start + pd.Timedelta(days=6)
        return f"{start.day} {start.strftime('%b')} - {end.day} {end.strftime('%b')}"

    df["week range"] = df["week"].apply(format_week_range)

    # --- 7. Ensure All Party-Week Combos Exist ---
    all_parties = df[["party type", "party name"]].drop_duplicates()
    all_weeks = pd.DataFrame(df["week range"].unique(), columns=["week range"])
    all_cross = all_parties.merge(all_weeks, how="cross")

    grouped = df.groupby(["party type", "party name", "week range"], as_index=False)["amount"].sum()
    complete = all_cross.merge(grouped, on=["party type", "party name", "week range"], how="left").fillna(0)

    # --- 8. Pivot Table for Display ---
    wide_df = complete.pivot_table(
        index=["party type", "party name"],
        columns="week range",
        values="amount",
        aggfunc="sum",
        fill_value=0
    )

    # --- 9. Net Cashflow Row ---
    net_cashflow = wide_df.sum()
    net_row = pd.DataFrame([net_cashflow], index=pd.MultiIndex.from_tuples([("Net Cashflow", "")]))
    final_table = pd.concat([wide_df, net_row])

    # --- 10. Display Table ---
    st.subheader("📋 Weekly Cashflow Breakdown by Party")
    st.dataframe(final_table.style.format("{:,.0f}"), use_container_width=True)

    # --- 11. Chart ---
    st.subheader("📈 Weekly Net Cashflow Chart")
    net_df = net_cashflow.reset_index()
    net_df.columns = ["Week", "Net Cashflow"]
    net_df["Week"] = pd.Categorical(net_df["Week"], categories=net_df["Week"], ordered=True)

    bars = alt.Chart(net_df).mark_bar().encode(
        x="Week:N",
        y="Net Cashflow:Q",
        color=alt.condition(
            alt.datum["Net Cashflow"] > 0,
            alt.value("#4CAF50"),
            alt.value("#EF5350")
        ),
        tooltip=["Week", "Net Cashflow"]
    )

    labels = alt.Chart(net_df).mark_text(
        align="center", baseline="bottom", dy=-5, fontSize=12
    ).encode(
        x="Week:N",
        y="Net Cashflow:Q",
        text=alt.Text("Net Cashflow:Q", format=",.0f"),
        color=alt.value("black")
    )

    st.altair_chart((bars + labels).properties(height=300), use_container_width=True)

    # --- 12. Excel Export ---
    towrite = BytesIO()
    with pd.ExcelWriter(towrite, engine="xlsxwriter") as writer:
        final_table.to_excel(writer, sheet_name="Forecast")
    st.download_button("📤 Download Excel Forecast", towrite.getvalue(), file_name="cashflow_forecast.xlsx")

else:
    st.info("Please upload your cashflow file to begin.")
