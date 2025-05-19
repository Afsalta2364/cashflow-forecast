import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO

# --- Page Setup ---
st.set_page_config(
    page_title="Cashflow Forecast Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("💰 Weekly Cashflow Forecast Dashboard")
st.markdown("Upload your cashflow data (CSV or Excel) to visualize your forecast.")

# --- Helper Functions ---
def format_week_range(start_date):
    """Formats a week's start date into a 'Day Mon - Day Mon' string."""
    end_date = start_date + pd.Timedelta(days=6)
    return f"{start_date.day} {start_date.strftime('%b')} - {end_date.day} {end_date.strftime('%b')}"

def style_table(df):
    """Applies styling to the forecast table."""
    styled_df = df.style.format("{:,.0f}") \
        .set_caption("Weekly Cashflow Breakdown") \
        .background_gradient(cmap='RdYlGn', axis=1, subset=pd.IndexSlice[:, df.columns[:-1]]) # Apply to all but last column if 'Total' exists

    # Make "Net Cashflow" row bold - more robust way to find it
    def bold_net_cashflow(row):
        if row.name == ("Net Cashflow", ""): # Check for MultiIndex tuple
            return ['font-weight: bold'] * len(row)
        return [''] * len(row)

    styled_df = styled_df.apply(bold_net_cashflow, axis=1)
    return styled_df

# --- Sidebar for Inputs ---
with st.sidebar:
    st.header("⚙️ Inputs & Settings")

    # 1. Sample Template Download
    with st.expander("📥 Download Sample Template"):
        sample_data = pd.DataFrame({
            "Party Type": ["Supplier", "Customer", "Supplier"],
            "Party Name": ["ABC Ltd", "XYZ Inc", "DEF Supplies"],
            "Due Date": ["2024-07-15", "2024-07-10", "2024-07-20"],
            "Expected Date": ["2024-07-20", "2024-07-14", "2024-07-22"],
            "Amount": [-10000, 12000, -5000]
        })
        # Ensure date columns are strings for CSV output consistency
        sample_data["Due Date"] = pd.to_datetime(sample_data["Due Date"]).dt.strftime('%Y-%m-%d')
        sample_data["Expected Date"] = pd.to_datetime(sample_data["Expected Date"]).dt.strftime('%Y-%m-%d')

        st.download_button(
            label="Download Template CSV",
            data=sample_data.to_csv(index=False).encode('utf-8'), # Specify encoding
            file_name="cashflow_template.csv",
            mime="text/csv",
            help="Use this template to structure your cashflow data."
        )

    # 2. Upload Section
    uploaded_file = st.file_uploader(
        "📤 Upload Cashflow Data",
        type=["csv", "xlsx"],
        help="Upload your CSV or Excel file with cashflow entries."
    )

# --- Main Panel for Results ---
if uploaded_file:
    st.header("📊 Forecast Results")
    try:
        # --- 3. File Load and Normalization ---
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file, sheet_name=0, engine='openpyxl') # Read first sheet
        else:
            st.error("Unsupported file type. Please upload a CSV or XLSX file.")
            st.stop()

        st.success(f"✅ Successfully loaded `{uploaded_file.name}`")

        # Clean column names (remove BOM, strip whitespace, lowercase)
        df.columns = df.columns.str.replace('\ufeff', '', regex=False).str.strip().str.lower()

        st.subheader("📄 Data Preview (First 5 Rows)")
        st.dataframe(df.head())
        st.write("Detected column names:", df.columns.tolist())

        # --- 4. Validate Required Columns ---
        required_cols = {"party type", "party name", "due date", "expected date", "amount"}
        missing_cols = required_cols - set(df.columns)
        if missing_cols:
            st.error(f"❌ Missing required columns: {', '.join(missing_cols)}. Please ensure your file has these columns.")
            st.stop()

        # --- 5. Data Type Conversion and Validation ---
        st.markdown("---")
        st.subheader("🛠️ Data Processing & Validation")

        # Convert 'amount' to numeric
        original_amount_type = df['amount'].dtype
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        if df['amount'].isnull().any():
            st.warning(
                "⚠️ Some 'Amount' values could not be converted to numbers and were set to NaN. "
                "These rows might be excluded or cause issues. Please check your input file."
            )
            st.dataframe(df[df['amount'].isnull()]) # Show rows with conversion issues


        # Convert date columns
        for col in ["due date", "expected date"]:
            original_date_type = df[col].dtype
            df[col] = pd.to_datetime(df[col], errors='coerce')
            if df[col].isnull().any():
                st.warning(
                    f"⚠️ Some '{col.title()}' values could not be converted to dates and were set to NaN. "
                    "These rows might be excluded or cause issues. Please check your input file."
                )
                st.dataframe(df[df[col].isnull()]) # Show rows with conversion issues

        # Drop rows where essential data is missing after coercion
        initial_row_count = len(df)
        df.dropna(subset=['amount', 'due date', 'expected date'], inplace=True)
        if len(df) < initial_row_count:
            st.info(f"ℹ️ {initial_row_count - len(df)} rows were removed due to missing critical values (Amount or Dates) after conversion.")

        if df.empty:
            st.error("❌ No valid data remaining after processing. Please check your file for correct formatting and values.")
            st.stop()

        st.success(f"✅ Data validated: {df.shape[0]} rows and {df.shape[1]} columns are ready for forecasting.")

        # --- 6. Allocation + Week Logic ---
        df["allocation date"] = df[["due date", "expected date"]].max(axis=1)
        df["week_start"] = df["allocation date"].dt.to_period("W").apply(lambda r: r.start_time)
        df["week_range"] = df["week_start"].apply(format_week_range)

        # --- 7. Ensure All Party-Week Combos Exist for consistent pivoting ---
        all_parties = df[["party type", "party name"]].drop_duplicates()
        
        # Ensure week_range is sorted chronologically for columns
        unique_week_starts = sorted(df["week_start"].unique())
        all_week_ranges_sorted = [format_week_range(ws) for ws in unique_week_starts]
        all_weeks_df = pd.DataFrame({"week_range": all_week_ranges_sorted})

        if not all_parties.empty and not all_weeks_df.empty:
            all_cross = pd.merge(all_parties, all_weeks_df, how="cross")
            grouped = df.groupby(["party type", "party name", "week_range"], as_index=False)["amount"].sum()
            complete_df = pd.merge(all_cross, grouped, on=["party type", "party name", "week_range"], how="left").fillna(0)
        else:
            st.warning("⚠️ Not enough data to create a full forecast structure (e.g., no parties or no date ranges).")
            complete_df = pd.DataFrame(columns=["party type", "party name", "week_range", "amount"]) # Empty structure

        # --- 8. Pivot Table for Display ---
        if not complete_df.empty:
            # Ensure 'week_range' is categorical and ordered for correct pivot column order
            complete_df['week_range'] = pd.Categorical(complete_df['week_range'], categories=all_week_ranges_sorted, ordered=True)

            pivot_table = complete_df.pivot_table(
                index=["party type", "party name"],
                columns="week_range",
                values="amount",
                aggfunc="sum",
                fill_value=0,
                dropna=False # Keep all week columns even if all values are 0 for that week
            )
        else:
            pivot_table = pd.DataFrame() # Empty pivot if no data

        # --- 9. Net Cashflow Row ---
        if not pivot_table.empty:
            net_cashflow_series = pivot_table.sum(numeric_only=True) # Sum only numeric columns
            net_row = pd.DataFrame([net_cashflow_series], index=pd.MultiIndex.from_tuples([("Net Cashflow", "")]))
            final_table = pd.concat([pivot_table, net_row])
        else:
            final_table = pd.DataFrame(columns=["No Data"]) # Placeholder if pivot is empty

        # --- 10. Display Table ---
        st.markdown("---")
        st.subheader("📋 Weekly Cashflow Breakdown by Party")
        if not final_table.empty and "No Data" not in final_table.columns:
            st.dataframe(style_table(final_table), use_container_width=True)

            # --- 11. Chart ---
            st.markdown("---")
            st.subheader("📈 Weekly Net Cashflow Chart")
            if not net_cashflow_series.empty:
                net_df = net_cashflow_series.reset_index()
                net_df.columns = ["Week Range", "Net Cashflow"]
                # Ensure 'Week Range' is categorical and ordered for correct chart order
                net_df["Week Range"] = pd.Categorical(net_df["Week Range"], categories=all_week_ranges_sorted, ordered=True)
                net_df = net_df.sort_values("Week Range")


                bars = alt.Chart(net_df).mark_bar().encode(
                    x=alt.X("Week Range:N", sort=None, title="Week"), # Use sort=None as it's pre-sorted
                    y=alt.Y("Net Cashflow:Q", title="Net Cashflow"),
                    color=alt.condition(
                        alt.datum["Net Cashflow"] >= 0, # Use >= 0 for green if 0 is neutral/good
                        alt.value("#4CAF50"),  # Green
                        alt.value("#EF5350")   # Red
                    ),
                    tooltip=[
                        alt.Tooltip("Week Range:N", title="Week"),
                        alt.Tooltip("Net Cashflow:Q", title="Amount", format=",.0f")
                    ]
                )

                text_labels = bars.mark_text(
                    align="center",
                    baseline="middle",
                    dy=alt.expr("datum['Net Cashflow'] >= 0 ? -10 : 10"), # Adjust dy based on bar direction
                    fontSize=12
                ).encode(
                    text=alt.Text("Net Cashflow:Q", format=",.0f"),
                    color=alt.value("black") # Ensure text is visible
                )

                chart = (bars + text_labels).properties(
                    height=350,
                    title="Weekly Net Cashflow Trend"
                )
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("ℹ️ Not enough data to generate Net Cashflow chart.")

            # --- 12. Excel Export ---
            st.markdown("---")
            st.subheader("📤 Export Forecast")
            towrite = BytesIO()
            with pd.ExcelWriter(towrite, engine="xlsxwriter") as writer:
                final_table.to_excel(writer, sheet_name="Cashflow Forecast", index=True)
            st.download_button(
                label="Download Forecast as Excel",
                data=towrite.getvalue(),
                file_name="cashflow_forecast.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Download the processed cashflow forecast table."
            )
        else:
            st.info("ℹ️ No forecast table to display. Please check your uploaded data and processing steps.")

    except pd.errors.ParserError:
        st.error("❌ Error parsing the uploaded file. It might be corrupted or not a valid CSV/Excel format.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        st.exception(e) # Shows full traceback for debugging during development

else:
    st.info("👈 Upload your cashflow file using the sidebar to begin forecasting.")
    st.markdown("""
        ### How to Use:
        1.  **Download Sample Template (Optional):** If you're unsure about the format, download the sample CSV from the sidebar.
        2.  **Prepare Your Data:** Ensure your CSV or Excel file has the following columns (case-insensitive):
            *   `Party Type` (e.g., Customer, Supplier)
            *   `Party Name` (e.g., Acme Corp, John Doe)
            *   `Due Date` (e.g., YYYY-MM-DD or other common date formats)
            *   `Expected Date` (e.g., YYYY-MM-DD or other common date formats - this will be used if later than Due Date)
            *   `Amount` (positive for inflows, negative for outflows)
        3.  **Upload Your File:** Use the uploader in the sidebar.
        4.  **View Results:** The dashboard will display a data preview, the cashflow table, and a net cashflow chart.
        5.  **Download Forecast:** You can download the generated forecast as an Excel file.
    """)
