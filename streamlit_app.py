import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO
import matplotlib # Ensure this is imported if using background_gradient
import numpy as np # For pd.np.number replacement

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
    h2 { /* Targets st.subheader */
        color: #264653; /* Darker teal/blue */
        border-bottom: 2px solid #E9C46A; /* Sandy yellow accent */
        padding-bottom: 5px;
        margin-top: 30px; /* Add some space above subheaders */
    }
     /* Section Title specifically for subheader after main title */
    div[data-testid="stVerticalBlock"] > div:nth-child(1) > div:nth-child(1) > h2 {
        margin-top: 0px !important; /* Reset margin for first subheader if needed */
    }
    /* Sidebar header */
    .sidebar .sidebar-content > div > h1 {
        color: #2A9D8F;
        font-weight: bold;
    }
    /* Metric labels */
    .stMetric > div > div:nth-child(1) { /* Label */
        color: #264653;
        font-size: 1.05em; /* Slightly smaller for better fit if long */
    }
    /* Metric values */
    .stMetric > div > div:nth-child(2) { /* Value */
        font-size: 1.7em; /* Slightly smaller if needed */
        font-weight: bold;
    }
     /* Metric delta */
    .stMetric > div > div:nth-child(3) { /* Delta */
        font-size: 0.95em; /* Slightly smaller for better fit */
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
    /* Container styling (subtle) */
    .stApp > footer {
        visibility: hidden; /* Hide default Streamlit footer */
    }
    /* Optional: Add subtle border to metric columns for card-like feel */
    /* div[data-testid="stMetric"] {
        background-color: #f9f9f9;
        border: 1px solid #e6e6e6;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    } */
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

def style_table(df_to_style):
    """Applies styling to the forecast table."""
    numeric_cols = df_to_style.select_dtypes(include='number').columns.tolist()

    styled_df = df_to_style.style.format("{:,.0f}", na_rep="-") \
        .set_caption("<span style='font-size: 1.2em; font-weight:bold; color: #264653;'>📋 Weekly Cashflow Breakdown</span>") \
        .set_properties(**{
            'font-size': '10pt',
            'border': '1px solid #e0e0e0',
            'width': 'auto'
        }) \
        .set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#2A9D8F'), ('color', 'white'), ('font-weight', 'bold')]},
            {'selector': 'td:hover', 'props': [('background-color', '#f0f8ff')]},
        ])

    if numeric_cols:
        valid_numeric_cols_for_subset = [col for col in numeric_cols if col in df_to_style.columns]
        if valid_numeric_cols_for_subset:
            try:
                styled_df = styled_df.background_gradient(cmap='RdYlGn', axis=None, subset=valid_numeric_cols_for_subset, low=0.1, high=0.1)
            except Exception as e:
                st.warning(f"Could not apply background gradient: {e}. Matplotlib might be needed or data format issue.")

    def bold_net_cashflow(row):
        if row.name == ("Net Cashflow", ""):
            return ['font-weight: bold; background-color: #E9C46A; color: #264653;'] * len(row)
        return [''] * len(row)

    styled_df = styled_df.apply(bold_net_cashflow, axis=1)
    return styled_df

# --- Sidebar for Inputs ---
with st.sidebar:
    st.markdown("<h1>⚙️ Inputs & Settings</h1>", unsafe_allow_html=True)
    st.markdown("---")
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
    st.caption("Developed with ❤️") # Add your name/company if you wish


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
            if df['amount'].isnull().any():
                st.warning("⚠️ Some 'Amount' values were non-numeric and ignored.")
                # st.dataframe(df[df['amount'].isnull()][list(required_cols - {'amount'})], hide_index=True) # Optional: show problematic rows
            for col in ["due date", "expected date"]:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                if df[col].isnull().any():
                    st.warning(f"⚠️ Some '{col.title()}' values were not valid dates and ignored.")
                    # st.dataframe(df[df[col].isnull()][list(required_cols - {col})], hide_index=True) # Optional

            initial_row_count = len(df)
            df.dropna(subset=['amount', 'due date', 'expected date'], inplace=True)
            if len(df) < initial_row_count:
                st.info(f"ℹ️ {initial_row_count - len(df)} rows removed due to missing/invalid critical values.")
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

            forecast_start_week_display = "N/A"
            forecast_end_week_display = "N/A"
            num_forecast_weeks = 0
            if all_week_ranges_sorted:
                forecast_start_week_display = all_week_ranges_sorted[0]
                forecast_end_week_display = all_week_ranges_sorted[-1]
                num_forecast_weeks = len(all_week_ranges_sorted)

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
                elif net_overall_cashflow > 0:
                    delta_for_net, delta_color_for_net, help_text_net = "Pure Inflow", "normal", help_text_net + " All cash movements are inflows."
                elif net_overall_cashflow == 0 and total_inflow == 0 and total_outflow_val == 0:
                    delta_for_net, help_text_net = "Zero Balance", help_text_net + " No cash movements recorded."
                st.metric(label="⚖️ Net Cashflow (Overall)", value=f"{net_overall_cashflow:,.0f}", delta=delta_for_net, delta_color=delta_color_for_net, help=help_text_net)

            col4, col5, col6 = st.columns(3)
            with col4: st.metric(label="🗓️ Forecast Start Week", value=forecast_start_week_display, help="The first week in this forecast.")
            with col5: st.metric(label="🗓️ Forecast End Week", value=forecast_end_week_display, help="The last week in this forecast.")
            with col6: st.metric(label="⏳ No. of Forecast Weeks", value=str(num_forecast_weeks), help="Total number of unique weeks covered.")
            st.divider()

            # --- Data Preview (inside a container) ---
            with st.container():
                st.subheader("📄 Uploaded Data Preview (First 5 Valid Rows)")
                st.dataframe(df.head(), use_container_width=True, hide_index=True)
            st.divider()

            # --- 7. Ensure All Party-Week Combos Exist ---
            all_parties = df[["party type", "party name"]].drop_duplicates()
            all_weeks_df = pd.DataFrame({"week_range": all_week_ranges_sorted}) # Use already sorted list

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
            with st.container():
                st.subheader("📊 Detailed Weekly Cashflow Forecast")
                if not final_table.empty and "No Data" not in final_table.columns:
                    st.markdown(style_table(final_table).to_html(), unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

                    if not net_cashflow_series.empty:
                        net_df = net_cashflow_series.reset_index()
                        net_df.columns = ["Week Range", "Net Cashflow"]
                        net_df["Week Range"] = pd.Categorical(net_df["Week Range"], categories=all_week_ranges_sorted, ordered=True)
                        net_df = net_df.sort_values("Week Range")
                        bars = alt.Chart(net_df).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
                            x=alt.X("Week Range:N", sort=None, title="Week", axis=alt.Axis(labelAngle=-45)),
                            y=alt.Y("Net Cashflow:Q", title="Net Cashflow ($)"),
                            color=alt.condition(alt.datum["Net Cashflow"] >= 0, alt.value("#4CAF50"), alt.value("#EF5350")),
                            tooltip=[alt.Tooltip("Week Range:N", title="Week"), alt.Tooltip("Net Cashflow:Q", title="Amount", format=",.0f")]
                        ).properties(title=alt.TitleParams(text="📈 Weekly Net Cashflow Trend", anchor='middle', fontSize=18, color="#264653"))
                        text_labels = bars.mark_text(align="center", baseline="middle", dy=alt.expr("datum['Net Cashflow'] >= 0 ? -12 : 12"), fontSize=11).encode(
                            text=alt.Text("Net Cashflow:Q", format=",.0f"), color=alt.value("#111111")
                        )
                        chart = (bars + text_labels).properties(height=400).configure_view(strokeOpacity=0)
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
                        header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#2A9D8F', 'font_color': 'white', 'border': 1})
                        for col_num, value in enumerate(export_table.columns.values): worksheet.write(0, col_num, value, header_format)
                        worksheet.set_column(0, len(export_table.columns) -1 , 15)
                        money_format = workbook.add_format({'num_format': '#,##0'})
                        for col_idx, col_name in enumerate(export_table.columns):
                            if export_table[col_name].dtype in ['int64', 'float64'] and col_idx >= (2 if 'Party Name' in export_table.columns else 1): # Heuristic for amount columns
                                 worksheet.set_column(col_idx, col_idx, None, money_format)
                    st.download_button(label="Download Forecast as Excel", data=towrite.getvalue(), file_name="cashflow_forecast.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                else: st.info("ℹ️ No forecast table to display.")
        except pd.errors.ParserError: st.error("❌ Error parsing the uploaded file.")
        except ImportError as ie:
            if "matplotlib" in str(ie).lower(): st.error("❌ Critical component 'Matplotlib' is missing. Install with `pip install matplotlib`.")
            else: st.error(f"An import error occurred: {ie}. A required library might be missing.")
            st.exception(ie)
        except Exception as e:
            st.error(f"An unexpected error occurred.")
            st.exception(e)
else:
    st.info("👈 **Upload your cashflow file using the sidebar to get started!**")
    st.markdown("---")
    with st.expander("💡 How to Use This Dashboard", expanded=True):
        st.markdown("""
            Welcome to your interactive Cashflow Forecast Dashboard!
            1.  **📥 Prepare Your Data:** Download sample template or ensure your CSV/Excel has: `Party Type`, `Party Name`, `Due Date`, `Expected Date`, `Amount`.
            2.  **📤 Upload Your File:** Use the sidebar uploader.
            3.  **📊 View & Analyze Results:** Key metrics, data preview, detailed table, and net cashflow chart.
            4.  **💾 Download Forecast:** Export as Excel.
            ✨ *Tip: Ensure date and amount columns are clean!*
            """)
    st.balloons()
