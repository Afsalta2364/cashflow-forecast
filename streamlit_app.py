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

# --- Custom CSS for enhanced look and feel (aiming for theme adaptability) ---
st.markdown("""
<style>
    /* --- Global Styles --- */
    body {
        font-family: 'Roboto', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: var(--text-color, #333333); /* Fallback if var is not defined */
        background-color: var(--background-color, #ffffff);
    }

    /* --- Main Title Area --- */
    .main-title-container {
        padding: 25px 20px; /* Reduced padding */
        background: var(--primary-color, #0077B6); /* Use Streamlit's primary or a fixed color */
        border-radius: 8px; /* Slightly less rounded */
        margin-bottom: 25px;
        text-align: center;
        box-shadow: 0 6px 12px rgba(0,0,0,0.08);
    }
    .main-title {
        font-size: 2.5em; /* Adjusted size */
        color: var(--white, #ffffff); /* Assuming primary is dark enough for white text */
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .main-subtitle {
        font-size: 1.15em; /* Adjusted size */
        color: var(--gray-100, #f0f8ff); /* Lighter color for subtitle, fallback AliceBlue */
        margin-top: 3px;
    }

    /* --- Subheader Styling (st.subheader) --- */
    h2 {
        color: var(--text-color, #2c3e50);
        border-bottom: 2px solid var(--primary-color-desaturated, #adb5bd); /* Neutral border */
        padding-bottom: 6px;
        margin-top: 30px;
        margin-bottom: 15px;
        font-weight: 500;
        font-size: 1.5em; /* Adjusted size */
        text-align: left;
    }

    /* --- Sidebar --- */
    section[data-testid="stSidebar"] {
        background-color: var(--secondary-background-color, #f8f9fa); /* Light neutral */
        border-right: 1px solid var(--gray-300, #dee2e6);
    }
    section[data-testid="stSidebar"] h1 {
        color: var(--primary-color, #005f73) !important;
        font-weight: bold !important; text-align: center !important;
        border-bottom: 2px solid var(--primary-color-lightened, #94d2bd) !important;
        padding-bottom: 10px !important; font-size: 1.4em !important; /* Adjusted */
    }
    .streamlit-expanderHeader {
        font-size: 1.0em !important; font-weight: 500 !important; /* Adjusted */
        color: var(--text-color, #003459) !important;
    }
    .streamlit-expanderHeader:hover {
        color: var(--primary-color, #0077B6) !important;
    }

    /* --- Metric Cards --- */
    div[data-testid="stMetric"] {
        background-color: var(--secondary-background-color, #ffffff);
        border: 1px solid var(--gray-300, #e0e0e0); /* Slightly lighter border */
        border-radius: 6px; padding: 15px; /* Adjusted */
        box-shadow: 0 3px 6px rgba(0,0,0,0.04); /* Softer shadow */
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        height: 100%;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px); box-shadow: 0 5px 10px rgba(0,0,0,0.06);
    }
    .stMetric > div > div:nth-child(1) { /* Label */
        color: var(--gray-700, #555555); /* Darker grey for label */
        font-size: 0.9em; font-weight: 500; margin-bottom: 4px; /* Adjusted */
    }
    .stMetric > div > div:nth-child(2) { /* Value */
        color: var(--text-color, #222222); /* Darker text for value */
        font-size: 1.8em; font-weight: 600; /* Adjusted */
    }
    .stMetric > div > div:nth-child(3) { /* Delta */
        font-size: 0.85em; font-weight: 500; /* Adjusted */
    }
    .stMetric [data-testid="stMetricDelta"] svg { visibility: visible !important; }


    /* --- Buttons (Using fixed colors that aim for general visibility) --- */
    .stButton>button, .stDownloadButton>button {
        border: none; border-radius: 20px; /* Slightly less rounded */
        color: #ffffff !important; /* Explicit white text for buttons */
        font-weight: 500; padding: 10px 20px; /* Adjusted */
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08); /* Softer shadow */
    }
    .stButton>button { background: var(--primary-color, #007bff); } /* Standard blue */
    .stButton>button:hover { background: var(--primary-color-darkened, #0056b3); transform: translateY(-1px); box-shadow: 0 3px 6px rgba(0,0,0,0.1); }

    .stDownloadButton>button { background: var(--success-color, #28a745); } /* Standard green, or a similar semantic color */
    .stDownloadButton>button:hover { background: var(--success-color-darkened, #1e7e34); transform: translateY(-1px); box-shadow: 0 3px 6px rgba(0,0,0,0.1); }


    /* --- Dataframe Styling (Wrapper) --- */
    div[data-testid="stMarkdown"] > div[data-testid="element-container"] > div > table {
        margin-bottom: 20px;
        /* Table itself styled by Pandas Styler */
    }

    .stApp > footer { visibility: hidden; }
    .stException { border-radius: 6px; border: 1px solid #dc3545; background-color: #f8d7da; color: #721c24; padding: 10px;}
    hr { border-top: 1px solid var(--gray-300, #e0e0e0); margin-top: 20px; margin-bottom: 20px; } /* Adjusted */
</style>
""", unsafe_allow_html=True)

# --- Main Title Section ---
st.markdown("""
<div class='main-title-container'>
    <div class='main-title'>💰 Weekly Cashflow Forecast</div>
    <div class='main-subtitle'>Upload data to visualize your projected financial health.</div>
</div>
""", unsafe_allow_html=True)
st.divider()

# --- Helper Functions ---
def format_week_range(start_date):
    end_date = start_date + pd.Timedelta(days=6)
    return f"{start_date.day} {start_date.strftime('%b')} - {end_date.day} {end_date.strftime('%b')}"

def style_table(df_to_style):
    numeric_cols = df_to_style.select_dtypes(include='number').columns.tolist()
    # Theme-aware color choices (conceptual - best handled by Streamlit's theme config if possible)
    text_color_primary = "var(--text-color, #212529)" # Bootstrap's default dark
    text_color_secondary = "var(--text-color-muted, #6c757d)" # Bootstrap's muted
    bg_color_table_header = "var(--secondary-background-color, #f8f9fa)" # Light grey, good for light theme
    border_color_subtle = "var(--border-color, #dee2e6)" # Standard border color

    styled_df = df_to_style.style.format("{:,.0f}", na_rep="-") \
        .set_caption(f"<span style='font-size: 1.2em; font-weight:500; color: {text_color_primary}; display:block; margin-bottom:10px; text-align:left;'>📋 Weekly Cashflow Breakdown</span>") \
        .set_properties(**{
            'font-size': '9.5pt', 'border': 'none', 'width': 'auto',
            'font-family': "'Roboto', 'Segoe UI', sans-serif", 'color': text_color_secondary
        }) \
        .set_table_styles([
            {'selector': '', 'props': [('border-collapse', 'collapse')]},
            {'selector': 'caption', 'props': [('caption-side', 'top')]},
            {'selector': 'th.col_heading', 'props': [
                ('background-color', bg_color_table_header), ('color', text_color_primary),
                ('font-weight', '500'), ('font-size', '9.5pt'), ('text-align', 'center'),
                ('padding', '8px 6px'), ('border-bottom', f'2px solid {border_color_subtle}')
            ]},
            {'selector': 'th.index_name', 'props': [
                ('background-color', bg_color_table_header), ('color', text_color_primary),
                ('font-weight', '500'), ('font-size', '9.5pt'), ('text-align', 'left'),
                ('padding', '8px 6px'), ('border-bottom', f'2px solid {border_color_subtle}'),
                ('border-right', f'1px solid {border_color_subtle}')
            ]},
            {'selector': 'th.row_heading', 'props': [
                ('background-color', "var(--background-color, #ffffff)"), # Match main page bg
                ('color', text_color_primary), ('font-weight', 'normal'), ('text-align', 'left'),
                ('padding', '6px 8px'), ('border-right', f'1px solid {border_color_subtle}'),
                ('border-bottom', f'1px solid {border_color_subtle}')
            ]},
            {'selector': 'td', 'props': [
                ('text-align', 'right'), ('padding', '6px 8px'),
                ('border-bottom', f'1px solid {border_color_subtle}')
            ]},
        ])

    if numeric_cols:
        valid_numeric_cols_for_subset = [col for col in numeric_cols if col in df_to_style.columns]
        if valid_numeric_cols_for_subset:
            try:
                styled_df = styled_df.background_gradient(
                    cmap='RdYlGn', axis=None, subset=valid_numeric_cols_for_subset,
                    low=0.48, high=0.48, text_color_threshold=0.408
                )
            except Exception as e: st.warning(f"Could not apply background gradient for table: {e}.")

    def style_net_cashflow_row(row):
        if row.name == ("Net Cashflow", ""):
            return [f'font-weight: 500; background-color: var(--secondary-background-color, #e9ecef); color: {text_color_primary}; border-top: 1.5px solid {border_color_subtle}; font-size:10pt;'] * len(row)
        return [''] * len(row)
    styled_df = styled_df.apply(style_net_cashflow_row, axis=1)
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

            # --- 6. Allocation + Week Logic ---
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

            cols1 = st.columns(3)
            cols1[0].metric(label="💰 Total Inflow", value=f"{total_inflow:,.0f}", help="Sum of all positive cashflow amounts (receipts).")
            cols1[1].metric(label="💸 Total Outflow", value=f"{total_outflow_val:,.0f}", help="Sum of all negative cashflow amounts (payments).")

            delta_for_net, delta_color_for_net, help_text_net = None, "off", "Overall net change in cash position."
            if abs(total_outflow_val) > 0:
                net_perc_of_outflow = (net_overall_cashflow / abs(total_outflow_val)) * 100 if abs(total_outflow_val) != 0 else 0
                delta_for_net = f"{net_perc_of_outflow:.1f}% vs Outflow Mag."
                delta_color_for_net = "normal" if net_overall_cashflow >= 0 else "inverse"
                help_text_net += f" Net ({net_overall_cashflow:,.0f}) is {net_perc_of_outflow:.1f}% of outflow magnitude ({abs(total_outflow_val):,.0f})."
            elif net_overall_cashflow > 0: delta_for_net, delta_color_for_net, help_text_net = "Pure Inflow", "normal", help_text_net + " All movements are inflows."
            elif net_overall_cashflow == 0 and total_inflow == 0 and total_outflow_val == 0: delta_for_net, help_text_net = "Zero Balance", help_text_net + " No cash movements."
            cols1[2].metric(label="⚖️ Net Cashflow (Overall)", value=f"{net_overall_cashflow:,.0f}", delta=delta_for_net, delta_color=delta_color_for_net, help=help_text_net)
            
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True) # Spacer

            cols2 = st.columns(3)
            cols2[0].metric(label="🗓️ Forecast Start Week", value=forecast_start_week_display, help="The first week in this forecast.")
            cols2[1].metric(label="🗓️ Forecast End Week", value=forecast_end_week_display, help="The last week in this forecast.")
            cols2[2].metric(label="⏳ No. of Forecast Weeks", value=str(num_forecast_weeks), help="Total number of unique weeks covered.")
            st.divider()

            # --- Data Preview ---
            with st.container():
                st.subheader("📄 Uploaded Data Preview (First 5 Valid Rows)")
                st.dataframe(df.head(), use_container_width=True, hide_index=True)
            st.divider()

            # --- 7. Prepare Pivot Table Data ---
            all_parties = df[["party type", "party name"]].drop_duplicates()
            all_weeks_df = pd.DataFrame({"week_range": all_week_ranges_sorted})
            if not all_parties.empty and not all_weeks_df.empty:
                all_cross = pd.merge(all_parties, all_weeks_df, how="cross")
                grouped = df.groupby(["party type", "party name", "week_range"], as_index=False)["amount"].sum()
                complete_df = pd.merge(all_cross, grouped, on=["party type", "party name", "week_range"], how="left").fillna(0)
            else: complete_df = pd.DataFrame(columns=["party type", "party name", "week_range", "amount"])

            if not complete_df.empty:
                complete_df['week_range'] = pd.Categorical(complete_df['week_range'], categories=all_week_ranges_sorted, ordered=True)
                pivot_table = complete_df.pivot_table(
                    index=["party type", "party name"], columns="week_range",
                    values="amount", aggfunc="sum", fill_value=0, dropna=False
                )
            else: pivot_table = pd.DataFrame()

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
                        bars = alt.Chart(net_df).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3, size=25).encode(
                            x=alt.X("Week Range:N", sort=None, title="Week", axis=alt.Axis(labelAngle=-45, labelFontSize=9, titleFontSize=11)),
                            y=alt.Y("Net Cashflow:Q", title="Net Cashflow ($)", axis=alt.Axis(labelFontSize=9, titleFontSize=11)),
                            color=alt.condition(alt.datum["Net Cashflow"] >= 0, alt.value("#28a745"), alt.value("#dc3545")), # Bootstrap success/danger
                            tooltip=[alt.Tooltip("Week Range:N", title="Week"), alt.Tooltip("Net Cashflow:Q", title="Amount", format=",.0f")]
                        ).properties(title=alt.TitleParams(text="📈 Weekly Net Cashflow Trend", anchor='middle', fontSize=16, fontWeight=500, color="var(--text-color, #2c3e50)"))
                        text_labels = bars.mark_text(align="center", baseline="middle", dy=alt.expr("datum['Net Cashflow'] >= 0 ? -10 : 10"), fontSize=9, fontWeight=400).encode(
                            text=alt.Text("Net Cashflow:Q", format=",.0f"), color=alt.value("var(--text-color, #222222)")
                        )
                        chart = (bars + text_labels).properties(height=350).configure_view(strokeOpacity=0).configure_axis(gridColor="var(--gray-200, #e9ecef)")
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
                        # Using colors that work well on white Excel background
                        header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#4F81BD', 'font_color': '#FFFFFF', 'border': 1})
                        for col_num, value in enumerate(export_table.columns.values): worksheet.write(0, col_num, value, header_format)
                        worksheet.set_column(0, len(export_table.columns) -1 , 18)
                        money_format = workbook.add_format({'num_format': '#,##0'})
                        for col_idx, col_name in enumerate(export_table.columns):
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
            1.  **📥 Prepare Your Data:** Download sample template or ensure your CSV/Excel has: `Party Type`, `Party Name`, `Due Date`, `Expected Date`, `Amount`.
            2.  **📤 Upload Your File:** Use the sidebar uploader.
            3.  **📊 View & Analyze Results:** Key metrics, data preview, detailed table, and net cashflow chart.
            4.  **💾 Download Forecast:** Export as Excel.
            ✨ *Tip: Ensure date and amount columns are clean!*
            """)
    st.balloons()
