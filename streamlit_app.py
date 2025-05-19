import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO
import matplotlib # For background_gradient
import numpy as np # For numeric type checking

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
    /* --- Global Styles --- */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #333;
    }

    /* --- Main Title Area --- */
    .main-title-container {
        padding: 30px 20px;
        background: linear-gradient(135deg, #005f73 0%, #0a9396 100%); /* Teal gradient */
        border-radius: 10px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    .main-title {
        font-size: 2.8em;
        color: #ffffff;
        font-weight: 600;
        letter-spacing: 1px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    .main-subtitle {
        font-size: 1.3em;
        color: #e0fbfc; /* Light cyan for subtitle */
        margin-top: 5px;
    }

    /* --- Subheader Styling (st.subheader) --- */
    h2 { /* Targets st.subheader */
        color: #003459; /* Dark Blue */
        border-bottom: 3px solid #00A99D; /* Teal accent line */
        padding-bottom: 8px;
        margin-top: 40px;
        margin-bottom: 20px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    /* --- Sidebar --- */
    /* Note: These st-emotion-cache selectors are unstable and may break with Streamlit updates. */
    /* Try to find more stable selectors if possible or use Streamlit's theming features. */
    section[data-testid="stSidebar"] { /* More stable way to target sidebar */
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%); /* Light grey gradient */
        border-right: 1px solid #dee2e6;
    }
    section[data-testid="stSidebar"] h1 { /* Sidebar Title */
        color: #005f73 !important; /* Dark Teal */
        font-weight: bold !important;
        text-align: center !important;
        border-bottom: 2px solid #94d2bd !important; /* Lighter teal accent */
        padding-bottom: 10px !important;
        font-size: 1.5em !important; /* Adjust size as needed */
    }
    .streamlit-expanderHeader { /* Expander header - general Streamlit class */
        font-size: 1.05em !important;
        font-weight: 600 !important;
        color: #003459 !important;
    }
     .streamlit-expanderHeader:hover {
        color: #0077B6 !important; /* Brighter blue on hover */
    }

    /* --- Metric Cards --- */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        height: 100%; /* Ensure cards in a row have same height */
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
    }
    .stMetric > div > div:nth-child(1) { /* Label */
        color: #6c757d; /* Muted grey for label */
        font-size: 0.95em;
        font-weight: 500;
        margin-bottom: 5px;
    }
    .stMetric > div > div:nth-child(2) { /* Value */
        color: #003459; /* Dark Blue for value */
        font-size: 2em;
        font-weight: 700;
    }
    .stMetric > div > div:nth-child(3) { /* Delta */
        font-size: 0.9em;
        font-weight: 500;
    }
    .stMetric [data-testid="stMetricDelta"] svg {
         visibility: visible !important;
    }

    /* --- Buttons --- */
    .stButton>button {
        border: none;
        border-radius: 25px;
        color: white;
        font-weight: 600;
        padding: 12px 25px;
        transition: all 0.3s ease;
        background: linear-gradient(135deg, #0077B6 0%, #00B4D8 100%); /* Blue gradient */
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        background: linear-gradient(135deg, #00B4D8 0%, #0077B6 100%);
    }
    .stDownloadButton>button {
        border: none;
        border-radius: 25px;
        color: white;
        font-weight: 600;
        padding: 12px 25px;
        background: linear-gradient(135deg, #E76F51 0%, #F4A261 100%); /* Orange/Yellow gradient */
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stDownloadButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        background: linear-gradient(135deg, #F4A261 0%, #E76F51 100%);
    }

    /* --- Dataframe Styling --- */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }
    /* Pandas Styler handles most table cell styling */

    /* Hide default Streamlit footer */
    .stApp > footer { visibility: hidden; }
    .stException { border-radius: 8px; border: 1px solid #ffcccb; }

    /* Divider styling */
    hr {
        border-top: 1px solid #e9ecef; /* Lighter divider */
        margin-top: 25px;
        margin-bottom: 25px;
    }
</style>
""", unsafe_allow_html=True)

# --- Main Title Section ---
st.markdown("""
<div class='main-title-container'>
    <div class='main-title'>💰 Weekly Cashflow Forecast</div>
    <div class='main-subtitle'>Upload your data to visualize your projected financial health.</div>
</div>
""", unsafe_allow_html=True)
st.divider()

# --- Helper Functions ---
def format_week_range(start_date):
    end_date = start_date + pd.Timedelta(days=6)
    return f"{start_date.day} {start_date.strftime('%b')} - {end_date.day} {end_date.strftime('%b')}"

def style_table(df_to_style):
    numeric_cols = df_to_style.select_dtypes(include='number').columns.tolist()
    styled_df = df_to_style.style.format("{:,.0f}", na_rep="-") \
        .set_caption("<span style='font-size: 1.3em; font-weight:600; color: #003459; display:block; margin-bottom:10px;'>📋 Weekly Cashflow Breakdown</span>") \
        .set_properties(**{
            'font-size': '10pt', 'border': '1px solid #dee2e6', 'width': 'auto',
            'font-family': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
        }) \
        .set_table_styles([
            {'selector': 'th', 'props': [
                ('background-color', '#0077B6'), ('color', 'white'), ('font-weight', '600'),
                ('font-size', '10.5pt'), ('text-align', 'center'), ('border-bottom', '2px solid #005f73')]},
            {'selector': 'td', 'props': [('text-align', 'right'), ('padding', '6px 8px')]},
            {'selector': 'td:hover', 'props': [('background-color', '#e0fbfc')]},
            {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#f8f9fa')]}
        ])
    if numeric_cols:
        valid_numeric_cols_for_subset = [col for col in numeric_cols if col in df_to_style.columns]
        if valid_numeric_cols_for_subset:
            try:
                styled_df = styled_df.background_gradient(
                    cmap='RdYlGn', axis=None, subset=valid_numeric_cols_for_subset, low=0.2, high=0.2
                )
            except Exception as e: st.warning(f"Could not apply background gradient: {e}.")
    def bold_net_cashflow(row):
        if row.name == ("Net Cashflow", ""):
            return ['font-weight: bold; background-color: #94d2bd; color: #003459; font-size:10.5pt;'] * len(row)
        return [''] * len(row)
    styled_df = styled_df.apply(bold_net_cashflow, axis=1)
    return styled_df

# --- Sidebar for Inputs ---
with st.sidebar:
    st.markdown("<h1>⚙️ Inputs & Settings</h1>", unsafe_allow_html=True) # Styled by CSS
    st.markdown("---") # Uses hr CSS styling
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
            label="Download Template CSV", data=sample_data.to_csv(index=False).encode('utf-8'),
            file_name="cashflow_template.csv", mime="text/csv",
            help="Use this template to structure your cashflow data."
        )
    st.markdown("---")
    uploaded_file = st.file_uploader(
        "📤 Upload Cashflow Data (CSV or Excel)", type=["csv", "xlsx"],
        help="Upload your CSV or Excel file with cashflow entries."
    )
    st.markdown("---")
    st.caption("Developed with ❤️")


# --- Main Panel for Results ---
if uploaded_file:
    with st.spinner("🚀 Processing your file... Hold tight!"):
        try:
            # --- 3. File Load and Normalization ---
            if uploaded_file.name.endswith(".csv"): df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".xlsx"): df = pd.read_excel(uploaded_file, sheet_name=0, engine='openpyxl')
            else:
                st.error("Unsupported file type.")
                st.stop()
            st.success(f"✅ File `{uploaded_file.name}` loaded successfully!")
            df.columns = df.columns.str.replace('\ufeff', '', regex=False).str.strip().str.lower()

            # --- 4. Validate Required Columns ---
            required_cols = {"party type", "party name", "due date", "expected date", "amount"}
            missing_cols = required_cols - set(df.columns)
            if missing_cols:
                st.error(f"❌ Missing required columns: {', '.join(missing_cols)}.")
                st.stop()

            # --- 5. Data Type Conversion and Validation ---
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            if df['amount'].isnull().any(): st.warning("⚠️ Some 'Amount' values were non-numeric and ignored.")
            for col in ["due date", "expected date"]:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                if df[col].isnull().any(): st.warning(f"⚠️ Some '{col.title()}' values were not valid dates and ignored.")

            initial_row_count = len(df)
            df.dropna(subset=['amount', 'due date', 'expected date'], inplace=True)
            if len(df) < initial_row_count: st.info(f"ℹ️ {initial_row_count - len(df)} rows removed due to missing/invalid critical values.")
            if df.empty:
                st.error("❌ No valid data remaining after processing.")
                st.stop()

            # --- 6. Allocation + Week Logic (DEFINES all_week_ranges_sorted NEEDED FOR METRICS) ---
            df["allocation date"] = df[["due date", "expected date"]].max(axis=1)
            df["week_start"] = df["allocation date"].dt.to_period("W").apply(lambda r: r.start_time)
            df["week_range"] = df["week_start"].apply(format_week_range)
            unique_week_starts = sorted(df["week_start"].unique())
            all_week_ranges_sorted = [format_week_range(ws) for ws in unique_week_starts]

            st.success(f"✅ Data validated: {df.shape[0]} rows ready for forecasting.")
            st.divider()

            # --- Key Metrics Section ---
            st.subheader("🚀 At a Glance: Forecast Summary")
            total_inflow = df[df['amount'] > 0]['amount'].sum()
            total_outflow_val = df[df['amount'] < 0]['amount'].sum()
            net_overall_cashflow = df['amount'].sum()
            forecast_start_week_display, forecast_end_week_display, num_forecast_weeks = "N/A", "N/A", 0
            if all_week_ranges_sorted:
                forecast_start_week_display, forecast_end_week_display, num_forecast_weeks = all_week_ranges_sorted[0], all_week_ranges_sorted[-1], len(all_week_ranges_sorted)

            col1, col2, col3 = st.columns(3)
            with col1: st.metric(label="💰 Total Inflow", value=f"{total_inflow:,.0f}", help="Sum of all positive cashflow amounts (receipts).")
            with col2: st.metric(label="💸 Total Outflow", value=f"{total_outflow_val:,.0f}", help="Sum of all negative cashflow amounts (payments).")
            with col3:
                delta_for_net, delta_color_for_net, help_text_net = None, "off", "Overall net change in cash position."
                if abs(total_outflow_val) > 0:
                    net_perc_of_outflow = (net_overall_cashflow / abs(total_outflow_val)) * 100
                    delta_for_net = f"{net_perc_of_outflow:.1f}% vs Outflow Mag."
                    delta_color_for_net = "normal" if net_overall_cashflow >= 0 else "inverse"
                    help_text_net += f" Current net ({net_overall_cashflow:,.0f}) is {net_perc_of_outflow:.1f}% of total outflow magnitude ({abs(total_outflow_val):,.0f})."
                elif net_overall_cashflow > 0: delta_for_net, delta_color_for_net, help_text_net = "Pure Inflow", "normal", help_text_net + " All cash movements are inflows."
                elif net_overall_cashflow == 0 and total_inflow == 0 and total_outflow_val == 0: delta_for_net, help_text_net = "Zero Balance", help_text_net + " No cash movements recorded."
                st.metric(label="⚖️ Net Cashflow (Overall)", value=f"{net_overall_cashflow:,.0f}", delta=delta_for_net, delta_color=delta_color_for_net, help=help_text_net)
            
            # Adding a small space before the next row of metrics
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

            col4, col5, col6 = st.columns(3)
            with col4: st.metric(label="🗓️ Forecast Start Week", value=forecast_start_week_display, help="The first week in this forecast.")
            with col5: st.metric(label="🗓️ Forecast End Week", value=forecast_end_week_display, help="The last week in this forecast.")
            with col6: st.metric(label="⏳ No. of Forecast Weeks", value=str(num_forecast_weeks), help="Total number of unique weeks covered.")
            st.divider()

            # --- Data Preview (inside a container) ---
            with st.container(): # Consider st.container(border=True) if st_version >= 1.28
                st.subheader("📄 Uploaded Data Preview (First 5 Valid Rows)")
                st.dataframe(df.head(), use_container_width=True, hide_index=True)
            st.divider()

            # --- 7. Ensure All Party-Week Combos Exist ---
            all_parties = df[["party type", "party name"]].drop_duplicates()
            all_weeks_df = pd.DataFrame({"week_range": all_week_ranges_sorted})
            if not all_parties.empty and not all_weeks_df.empty:
                all_cross = pd.merge(all_parties, all_weeks_df, how="cross")
                grouped = df.groupby(["party type", "party name", "week_range"], as_index=False)["amount"].sum()
                complete_df = pd.merge(all_cross, grouped, on=["party type", "party name", "week_range"], how="left").fillna(0)
            else: complete_df = pd.DataFrame(columns=["party type", "party name", "week_range", "amount"])

            # --- 8. Pivot Table for Display ---
            if not complete_df.empty:
                complete_df['week_range'] = pd.Categorical(complete_df['week_range'], categories=all_week_ranges_sorted, ordered=True)
                pivot_table = complete_df.pivot_table(
                    index=["party type", "party name"], columns="week_range",
                    values="amount", aggfunc="sum", fill_value=0, dropna=False
                )
            else: pivot_table = pd.DataFrame()

            # --- 9. Net Cashflow Row ---
            if not pivot_table.empty:
                net_cashflow_series = pivot_table.sum(numeric_only=True)
                net_row = pd.DataFrame([net_cashflow_series], index=pd.MultiIndex.from_tuples([("Net Cashflow", "")]))
                final_table = pd.concat([pivot_table, net_row])
            else: final_table = pd.DataFrame(columns=["No Data"])

            # --- Main Forecast Display Area ---
            with st.container(): # Consider st.container(border=True) if st_version >= 1.28
                st.subheader("📊 Detailed Weekly Cashflow Forecast")
                if not final_table.empty and "No Data" not in final_table.columns:
                    st.markdown(style_table(final_table).to_html(), unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

                    if not net_cashflow_series.empty:
                        net_df = net_cashflow_series.reset_index()
                        net_df.columns = ["Week Range", "Net Cashflow"]
                        net_df["Week Range"] = pd.Categorical(net_df["Week Range"], categories=all_week_ranges_sorted, ordered=True)
                        net_df = net_df.sort_values("Week Range")
                        bars = alt.Chart(net_df).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5, size=30).encode( # size for bar width
                            x=alt.X("Week Range:N", sort=None, title="Week", axis=alt.Axis(labelAngle=-45, labelFontSize=10, titleFontSize=12)),
                            y=alt.Y("Net Cashflow:Q", title="Net Cashflow ($)", axis=alt.Axis(labelFontSize=10, titleFontSize=12)),
                            color=alt.condition(alt.datum["Net Cashflow"] >= 0, alt.value("#2a9d8f"), alt.value("#e76f51")), # Teal and Orange
                            tooltip=[alt.Tooltip("Week Range:N", title="Week"), alt.Tooltip("Net Cashflow:Q", title="Amount", format=",.0f")]
                        ).properties(title=alt.TitleParams(text="📈 Weekly Net Cashflow Trend", anchor='middle', fontSize=18, fontWeight=600, color="#003459"))
                        text_labels = bars.mark_text(align="center", baseline="middle", dy=alt.expr("datum['Net Cashflow'] >= 0 ? -12 : 12"), fontSize=10, fontWeight=500).encode(
                            text=alt.Text("Net Cashflow:Q", format=",.0f"), color=alt.value("#222222")
                        )
                        chart = (bars + text_labels).properties(height=380).configure_view(strokeOpacity=0).configure_axis(gridColor='#e9ecef') # Light grid
                        st.altair_chart(chart, use_container_width=True)
                    else: st.info("ℹ️ Not enough data for Net Cashflow chart.")
                    st.divider()
                    st.subheader("📤 Export Forecast")
                    towrite = BytesIO()
                    export_table = final_table.copy()
                    if isinstance(export_table.index, pd.MultiIndex): export_table = export_table.reset_index()
                    with pd.ExcelWriter(towrite, engine="xlsxwriter") as writer:
                        export_table.to_excel(writer, sheet_name="Cashflow Forecast", index=False)
                        workbook, worksheet = writer.book, writer.sheets["Cashflow Forecast"]
                        header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#0077B6', 'font_color': 'white', 'border': 1})
                        for col_num, value in enumerate(export_table.columns.values): worksheet.write(0, col_num, value, header_format)
                        worksheet.set_column(0, len(export_table.columns) -1 , 18) # Slightly wider columns
                        money_format = workbook.add_format({'num_format': '#,##0'})
                        # Improved heuristic for amount columns for Excel formatting
                        for col_idx, col_name in enumerate(export_table.columns):
                            # Check if column name contains typical week indicators or if dtype is numeric,
                            # and it's not one of the initial party info columns.
                            is_party_col = col_name.lower() in ["party type", "party name"]
                            if not is_party_col and (export_table[col_name].dtype in ['int64', 'float64', np.number]):
                                 worksheet.set_column(col_idx, col_idx, None, money_format)
                    st.download_button(label="Download Forecast as Excel", data=towrite.getvalue(), file_name="cashflow_forecast.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                else: st.info("ℹ️ No forecast table to display.")
        except pd.errors.ParserError: st.error("❌ Error parsing the uploaded file.")
        except ImportError as ie:
            if "matplotlib" in str(ie).lower(): st.error("❌ Critical component 'Matplotlib' is missing. Install with `pip install matplotlib`.")
            else: st.error(f"An import error occurred: {ie}. A required library might be missing.")
            st.exception(ie)
        except Exception as e:
            st.error(f"An unexpected error occurred during processing.")
            st.exception(e)
else:
    st.info("👈 **Upload your cashflow file using the sidebar to get started!**")
    st.markdown("---")
    with st.expander("💡 How to Use This Dashboard", expanded=True):
        st.markdown("""
            Welcome to your interactive Cashflow Forecast Dashboard!

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
