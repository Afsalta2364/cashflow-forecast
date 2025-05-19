import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO
import matplotlib # Ensure this is imported if using background_gradient

# --- Page Setup ---
st.set_page_config(
    page_title="Cashflow Forecast Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for enhanced look and feel ---
st.markdown("""
<style>
    /* Main title */
    .main-title {
        font-size: 3em;
        color: #2A9D8F; /* Tealish color */
        text-align: center;
        font-weight: bold;
        margin-bottom: 20px;
    }
    /* Subheader styling */
    h2 {
        color: #264653; /* Darker teal/blue */
        border-bottom: 2px solid #E9C46A; /* Sandy yellow accent */
        padding-bottom: 5px;
    }
    /* Sidebar header */
    .sidebar .sidebar-content > div > h1 {
        color: #2A9D8F;
        font-weight: bold;
    }
    /* Metric labels */
    .stMetric > div > div:nth-child(1) {
        color: #264653; /* Darker label color for metric */
        font-size: 1.1em;
    }
    /* Metric values */
    .stMetric > div > div:nth-child(2) {
        font-size: 1.8em;
        font-weight: bold;
    }
    /* Expander header */
    .streamlit-expanderHeader {
        font-size: 1.1em;
        font-weight: bold;
        color: #264653;
    }
    /* Style buttons */
    .stButton>button {
        border: 2px solid #2A9D8F;
        border-radius: 20px;
        color: #2A9D8F;
        font-weight: bold;
        padding: 10px 20px;
        transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #2A9D8F;
        color: white;
    }
    .stDownloadButton>button {
        border: 2px solid #E76F51; /* Orange for download */
        border-radius: 20px;
        color: #E76F51;
        font-weight: bold;
        padding: 10px 20px;
        background-color: white;
    }
    .stDownloadButton>button:hover {
        background-color: #E76F51;
        color: white;
    }
    /* Container styling */
    .stApp > footer {
        visibility: hidden; /* Hide default Streamlit footer */
    }
    div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"]>div[data-testid="stHorizontalBlock"] {
      border: 1px solid #e6e6e6;
      border-radius: 10px;
      padding: 15px;
      box-shadow: 0 4px 8px rgba(0,0,0,0.1);
      background-color: #f9f9f9; /* Light background for containers */
    }

</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>💰 Weekly Cashflow Forecast Dashboard</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2em; color: #264653;'>Upload your cashflow data (CSV or Excel) to visualize your projected financial health.</p>", unsafe_allow_html=True)
st.divider()

# --- Helper Functions ---
def format_week_range(start_date):
    """Formats a week's start date into a 'Day Mon - Day Mon' string."""
    end_date = start_date + pd.Timedelta(days=6)
    return f"{start_date.day} {start_date.strftime('%b')} - {end_date.day} {end_date.strftime('%b')}"

def style_table(df):
    """Applies styling to the forecast table."""
    # Determine numeric columns for gradient (week range columns)
    numeric_cols = df.select_dtypes(include=pd.np.number).columns.tolist()

    styled_df = df.style.format("{:,.0f}", na_rep="-") \
        .set_caption("<span style='font-size: 1.2em; font-weight:bold; color: #264653;'>📋 Weekly Cashflow Breakdown</span>") \
        .set_properties(**{
            'font-size': '10pt',
            'border': '1px solid #e0e0e0',
            'width': 'auto'
        }) \
        .set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#2A9D8F'), ('color', 'white'), ('font-weight', 'bold')]},
            {'selector': 'td:hover', 'props': [('background-color', '#f0f8ff')]}, # Light blue on hover
        ])

    if numeric_cols: # Apply gradient only if there are numeric columns
        try:
            styled_df = styled_df.background_gradient(cmap='RdYlGn', axis=None, subset=numeric_cols, low=0.1, high=0.1) #axis=None for whole table context
        except Exception as e:
            st.warning(f"Could not apply background gradient: {e}. Matplotlib might be needed or data format issue.")


    def bold_net_cashflow(row):
        if row.name == ("Net Cashflow", ""):
            return ['font-weight: bold; background-color: #E9C46A; color: #264653;'] * len(row) # Sandy yellow bg for Net Cashflow
        return [''] * len(row)

    styled_df = styled_df.apply(bold_net_cashflow, axis=1)
    return styled_df

# --- Sidebar for Inputs ---
with st.sidebar:
    st.markdown("<h1>⚙️ Inputs & Settings</h1>", unsafe_allow_html=True)
    st.markdown("---")

    # 1. Sample Template Download
    with st.expander("📥 Download Sample Template", expanded=False):
        sample_data = pd.DataFrame({
            "Party Type": ["Supplier", "Customer", "Supplier"],
            "Party Name": ["ABC Ltd", "XYZ Inc", "DEF Supplies"],
            "Due Date": ["2024-07-15", "2024-07-10", "2024-07-20"],
            "Expected Date": ["2024-07-20", "2024-07-14", "2024-07-22"],
            "Amount": [-10000, 12000, -5000]
        })
        sample_data["Due Date"] = pd.to_datetime(sample_data["Due Date"]).dt.strftime('%Y-%m-%d')
        sample_data["Expected Date"] = pd.to_datetime(sample_data["Expected Date"]).dt.strftime('%Y-%m-%d')

        st.download_button(
            label="Download Template CSV",
            data=sample_data.to_csv(index=False).encode('utf-8'),
            file_name="cashflow_template.csv",
            mime="text/csv",
            help="Use this template to structure your cashflow data."
        )
    st.markdown("---")
    # 2. Upload Section
    uploaded_file = st.file_uploader(
        "📤 Upload Cashflow Data (CSV or Excel)",
        type=["csv", "xlsx"],
        help="Upload your CSV or Excel file with cashflow entries."
    )
    st.markdown("---")
    st.caption("Developed with ❤️ by Your Name/Company")


# --- Main Panel for Results ---
if uploaded_file:
    with st.spinner("🚀 Processing your file... Hold tight!"):
        try:
            # --- 3. File Load and Normalization ---
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file, sheet_name=0, engine='openpyxl')
            else:
                st.error("Unsupported file type. Please upload a CSV or XLSX file.")
                st.stop()

            st.success(f"✅ File `{uploaded_file.name}` loaded successfully!")

            df.columns = df.columns.str.replace('\ufeff', '', regex=False).str.strip().str.lower()

            # --- 4. Validate Required Columns ---
            required_cols = {"party type", "party name", "due date", "expected date", "amount"}
            missing_cols = required_cols - set(df.columns)
            if missing_cols:
                st.error(f"❌ Missing required columns: {', '.join(missing_cols)}. Please ensure your file has these columns.")
                st.stop()

            # --- 5. Data Type Conversion and Validation ---
            # Convert 'amount' to numeric
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            if df['amount'].isnull().any():
                st.warning(
                    "⚠️ Some 'Amount' values were non-numeric and have been ignored. "
                    "Please check these rows in your input file:"
                )
                st.dataframe(df[df['amount'].isnull()][required_cols - {'amount'}], hide_index=True)

            # Convert date columns
            for col in ["due date", "expected date"]:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                if df[col].isnull().any():
                    st.warning(
                        f"⚠️ Some '{col.title()}' values were not valid dates and have been ignored. "
                        "Please check these rows in your input file:"
                    )
                    st.dataframe(df[df[col].isnull()][required_cols - {col}], hide_index=True)

            initial_row_count = len(df)
            df.dropna(subset=['amount', 'due date', 'expected date'], inplace=True)
            if len(df) < initial_row_count:
                st.info(f"ℹ️ {initial_row_count - len(df)} rows were removed due to missing/invalid critical values (Amount or Dates).")

            if df.empty:
                st.error("❌ No valid data remaining after processing. Please check your file for correct formatting and values.")
                st.stop()

            # --- 6. Allocation + Week Logic ---
            df["allocation date"] = df[["due date", "expected date"]].max(axis=1)
            df["week_start"] = df["allocation date"].dt.to_period("W").apply(lambda r: r.start_time)
            df["week_range"] = df["week_start"].apply(format_week_range)

            st.success(f"✅ Data validated: {df.shape[0]} rows are ready for forecasting.")
            st.divider()

            # --- Key Metrics Section ---
            st.subheader("🚀 At a Glance: Forecast Summary")
            total_inflow = df[df['amount'] > 0]['amount'].sum()
            total_outflow = df[df['amount'] < 0]['amount'].sum()
            net_overall_cashflow = df['amount'].sum()
            forecast_start_date = df['allocation date'].min().strftime('%d %b %Y')
            forecast_end_date = df['allocation date'].max().strftime('%d %b %Y')

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="💰 Total Inflow", value=f"{total_inflow:,.0f}", delta_color="normal")
            with col2:
                st.metric(label="💸 Total Outflow", value=f"{total_outflow:,.0f}", delta_color="inverse") # Negative is "good" for outflow value
            with col3:
                st.metric(label="⚖️ Net Cashflow (Overall)", value=f"{net_overall_cashflow:,.0f}",
                          delta=f"{((total_inflow / abs(total_outflow) * 100) if total_outflow !=0 else 0) - 100 :.1f}% vs Outflow" if total_outflow !=0 else "N/A" )

            col4, col5 = st.columns(2)
            with col4:
                st.metric(label="🗓️ Forecast Start", value=forecast_start_date)
            with col5:
                st.metric(label="🗓️ Forecast End", value=forecast_end_date)
            st.divider()


            # --- Data Preview (inside a container) ---
            with st.container(): #border=True can be added in st>=1.28
                st.subheader("📄 Uploaded Data Preview (First 5 Valid Rows)")
                st.dataframe(df.head(), use_container_width=True, hide_index=True)
            st.divider()


            # --- 7. Ensure All Party-Week Combos Exist ---
            all_parties = df[["party type", "party name"]].drop_duplicates()
            unique_week_starts = sorted(df["week_start"].unique())
            all_week_ranges_sorted = [format_week_range(ws) for ws in unique_week_starts]
            all_weeks_df = pd.DataFrame({"week_range": all_week_ranges_sorted})

            if not all_parties.empty and not all_weeks_df.empty:
                all_cross = pd.merge(all_parties, all_weeks_df, how="cross")
                grouped = df.groupby(["party type", "party name", "week_range"], as_index=False)["amount"].sum()
                complete_df = pd.merge(all_cross, grouped, on=["party type", "party name", "week_range"], how="left").fillna(0)
            else:
                complete_df = pd.DataFrame(columns=["party type", "party name", "week_range", "amount"])

            # --- 8. Pivot Table for Display ---
            if not complete_df.empty:
                complete_df['week_range'] = pd.Categorical(complete_df['week_range'], categories=all_week_ranges_sorted, ordered=True)
                pivot_table = complete_df.pivot_table(
                    index=["party type", "party name"],
                    columns="week_range", values="amount", aggfunc="sum", fill_value=0, dropna=False
                )
            else:
                pivot_table = pd.DataFrame()

            # --- 9. Net Cashflow Row ---
            if not pivot_table.empty:
                net_cashflow_series = pivot_table.sum(numeric_only=True)
                net_row = pd.DataFrame([net_cashflow_series], index=pd.MultiIndex.from_tuples([("Net Cashflow", "")]))
                final_table = pd.concat([pivot_table, net_row])
            else:
                final_table = pd.DataFrame(columns=["No Data"])

            # --- Main Forecast Display Area ---
            with st.container(): #border=True
                st.subheader("📊 Detailed Weekly Cashflow Forecast")
                if not final_table.empty and "No Data" not in final_table.columns:
                    # --- 10. Display Table ---
                    st.markdown(style_table(final_table).to_html(), unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True) # Spacer

                    # --- 11. Chart ---
                    if not net_cashflow_series.empty:
                        net_df = net_cashflow_series.reset_index()
                        net_df.columns = ["Week Range", "Net Cashflow"]
                        net_df["Week Range"] = pd.Categorical(net_df["Week Range"], categories=all_week_ranges_sorted, ordered=True)
                        net_df = net_df.sort_values("Week Range")

                        bars = alt.Chart(net_df).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
                            x=alt.X("Week Range:N", sort=None, title="Week", axis=alt.Axis(labelAngle=-45)),
                            y=alt.Y("Net Cashflow:Q", title="Net Cashflow ($)"),
                            color=alt.condition(
                                alt.datum["Net Cashflow"] >= 0,
                                alt.value("#4CAF50"), alt.value("#EF5350")
                            ),
                            tooltip=[
                                alt.Tooltip("Week Range:N", title="Week"),
                                alt.Tooltip("Net Cashflow:Q", title="Amount", format=",.0f")
                            ]
                        ).properties(
                            title=alt.TitleParams(
                                text="📈 Weekly Net Cashflow Trend",
                                anchor='middle',
                                fontSize=18,
                                color="#264653"
                            )
                        )
                        text_labels = bars.mark_text(align="center", baseline="middle", dy=alt.expr("datum['Net Cashflow'] >= 0 ? -12 : 12"), fontSize=11).encode(
                            text=alt.Text("Net Cashflow:Q", format=",.0f"),
                            color=alt.value("#111111")
                        )
                        chart = (bars + text_labels).properties(height=400).configure_view(strokeOpacity=0)
                        st.altair_chart(chart, use_container_width=True)
                    else:
                        st.info("ℹ️ Not enough data to generate Net Cashflow chart.")
                    st.divider()
                    # --- 12. Excel Export ---
                    st.subheader("📤 Export Forecast")
                    towrite = BytesIO()
                    # Write to Excel, convert MultiIndex to a more Excel-friendly format
                    export_table = final_table.copy()
                    if isinstance(export_table.index, pd.MultiIndex):
                        export_table = export_table.reset_index()

                    with pd.ExcelWriter(towrite, engine="xlsxwriter") as writer:
                        export_table.to_excel(writer, sheet_name="Cashflow Forecast", index=False)
                        workbook = writer.book
                        worksheet = writer.sheets["Cashflow Forecast"]
                        # Add some basic formatting to Excel
                        header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#2A9D8F', 'font_color': 'white', 'border': 1})
                        for col_num, value in enumerate(export_table.columns.values):
                            worksheet.write(0, col_num, value, header_format)
                        worksheet.set_column(0, len(export_table.columns) -1 , 15) # Set column width
                        # Add number format for amount columns
                        money_format = workbook.add_format({'num_format': '#,##0'})
                        # Find columns that are week ranges (likely all except first two if Party Type/Name are columns)
                        for col_idx, col_name in enumerate(export_table.columns):
                            if 'Week Range' in str(col_name) or 'Amount' in str(col_name) or export_table[col_name].dtype in [pd.np.number]: # Heuristic
                                if col_idx >= 2: # Assuming first two are party type/name
                                     worksheet.set_column(col_idx, col_idx, None, money_format)


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
        except ImportError as ie:
            if "matplotlib" in str(ie).lower():
                st.error("❌ Critical component 'Matplotlib' is missing. This is needed for table styling. Please install it (`pip install matplotlib`).")
            else:
                st.error(f"An import error occurred: {ie}. A required library might be missing.")
            st.exception(ie)
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            st.exception(e) # Shows full traceback for debugging

else:
    st.info("👈 **Upload your cashflow file using the sidebar to get started!**")
    st.markdown("---")
    with st.expander("💡 How to Use This Dashboard", expanded=True):
        st.markdown("""
            Welcome to your interactive Cashflow Forecast Dashboard! Follow these simple steps:

            1.  **📥 Prepare Your Data:**
                *   If you're unsure about the format, **download the sample template** from the sidebar.
                *   Ensure your CSV or Excel file includes these columns (case-insensitive):
                    *   `Party Type` (e.g., Customer, Supplier)
                    *   `Party Name` (e.g., Acme Corp, John Doe)
                    *   `Due Date` (Format: YYYY-MM-DD or similar)
                    *   `Expected Date` (Format: YYYY-MM-DD; the later of Due/Expected is used)
                    *   `Amount` (Positive for inflows, negative for outflows. Just numbers, no currency symbols in cells.)

            2.  **📤 Upload Your File:**
                *   Use the **file uploader in the sidebar** to select your prepared cashflow data.

            3.  **📊 View & Analyze Results:**
                *   **At a Glance Metrics:** Get a quick overview of total inflows, outflows, and the forecast period.
                *   **Data Preview:** Check the first few rows of your (processed) data.
                *   **Detailed Forecast Table:** See a weekly breakdown by party.
                *   **Net Cashflow Chart:** Visualize your weekly net cashflow trend.

            4.  **💾 Download Forecast:**
                *   Export the generated forecast table as an Excel file for offline use or sharing.

            ✨ *Tip: Ensure your date and amount columns are clean for best results!*
            """)
    st.balloons()
