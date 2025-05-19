import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO
import matplotlib # For background_gradient
import numpy as np

# --- Page Setup ---
st.set_page_config(
    page_title="Cashflow Forecast Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Dark Theme ---
st.markdown("""
<style>
    /* --- Global Styles for Dark Theme --- */
    body {
        font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
        color: #e0e0e0;
        background-color: #121212; /* Standard dark theme background */
    }

    /* --- Main Title Area --- */
    .main-title-container {
        padding: 25px 20px;
        background: #1f2937; /* Dark blue-grey, slightly lighter than body */
        border-radius: 8px;
        margin-bottom: 30px;
        text-align: center;
        border: 1px solid #374151; /* Subtle border */
    }
    .main-title {
        font-size: 2.4em;
        color: #ffffff; /* White for high contrast */
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .main-subtitle {
        font-size: 1.1em;
        color: #9ca3af; /* Lighter grey for subtitle */
        margin-top: 5px;
    }

    /* --- Subheader Styling (st.subheader) --- */
    h2 {
        color: #d1d5db; /* Light grey, almost white */
        border-bottom: 1px solid #4b5563; /* Darker grey accent line */
        padding-bottom: 8px;
        margin-top: 35px;
        margin-bottom: 20px;
        font-weight: 500;
        font-size: 1.4em;
        text-align: left;
    }

    /* --- Sidebar --- */
    section[data-testid="stSidebar"] {
        background-color: #1f2937; /* Consistent dark element background */
        border-right: 1px solid #374151;
    }
    section[data-testid="stSidebar"] h1 { /* Sidebar Title "Inputs & Settings" */
        color: #60a5fa !important; /* Bright blue accent */
        font-weight: 500 !important; text-align: center !important;
        border-bottom: 1px solid #3b82f6 !important; /* Brighter blue border */
        padding-bottom: 10px !important; font-size: 1.3em !important;
        margin-top: 5px !important;
    }
    .streamlit-expanderHeader { /* Expander header in sidebar */
        font-size: 1.0em !important; font-weight: normal !important;
        color: #d1d5db !important;
        padding: 8px 0px !important;
    }
    .streamlit-expanderHeader:hover {
        color: #93c5fd !important; /* Lighter blue on hover */
    }
    section[data-testid="stSidebar"] .stFileUploader label { /* File uploader label */
        color: #d1d5db !important;
        font-size: 0.95em !important;
    }
    section[data-testid="stSidebar"] .stButton>button { /* Buttons in sidebar (like "Download Template") */
        background-color: #3b82f6; /* Accent blue */
        color: white !important;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 0.9em;
    }
    section[data-testid="stSidebar"] .stButton>button:hover {
        background-color: #2563eb;
    }


    /* --- Metric Cards --- */
    div[data-testid="stMetric"] {
        background-color: #1f2937; /* Dark element background */
        border: 1px solid #374151; /* Subtle border */
        border-radius: 8px; padding: 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06); /* Subtle shadow for depth */
        height: 100%;
    }
    .stMetric > div > div:nth-child(1) { /* Label */
        color: #9ca3af; /* Muted light grey for label */
        font-size: 0.85em; font-weight: 400; margin-bottom: 6px;
        text-transform: uppercase; /* Uppercase labels */
        letter-spacing: 0.5px;
    }
    .stMetric > div > div:nth-child(2) { /* Value */
        color: #f3f4f6; /* Very light grey, almost white */
        font-size: 1.9em; font-weight: 600;
    }
    .stMetric > div > div:nth-child(3) { /* Delta */
        font-size: 0.9em; font-weight: 500;
    }
    .stMetric [data-testid="stMetricDelta"] svg { visibility: visible !important; }


    /* --- Main Buttons (e.g., Download Forecast Excel) --- */
    .stDownloadButton>button { /* Main download button */
        background-color: #10b981; /* Emerald green accent */
        color: white !important;
        border: none; border-radius: 6px;
        font-weight: 500; padding: 10px 22px;
        font-size: 0.95em;
    }
    .stDownloadButton>button:hover {
        background-color: #059669; /* Darker green */
    }

    /* --- Alert Messages Styling --- */
    div[data-testid="stAlert"] { border-radius: 6px; border-width: 1px; border-style: solid; padding: 12px 15px; font-size: 0.9em;}
    div[data-testid="stAlert"][data-baseweb="alert-success"] { background-color: rgba(16, 185, 129, 0.15); border-color: #10b981; color: #a7f3d0; }
    div[data-testid="stAlert"][data-baseweb="alert-success"] svg { fill: #a7f3d0; }
    div[data-testid="stAlert"][data-baseweb="alert-info"] { background-color: rgba(59, 130, 246, 0.15); border-color: #3b82f6; color: #bfdbfe; }
    div[data-testid="stAlert"][data-baseweb="alert-info"] svg { fill: #bfdbfe; }
    div[data-testid="stAlert"][data-baseweb="alert-warning"] { background-color: rgba(245, 158, 11, 0.15); border-color: #f59e0b; color: #fde68a; }
    div[data-testid="stAlert"][data-baseweb="alert-warning"] svg { fill: #fde68a; }
    div[data-testid="stAlert"][data-baseweb="alert-error"] { background-color: rgba(239, 68, 68, 0.15); border-color: #ef4444; color: #fecaca; }
    div[data-testid="stAlert"][data-baseweb="alert-error"] svg { fill: #fecaca; }

    /* --- Dataframe Styling (Wrapper for st.dataframe) --- */
    .stDataFrame {
        border: 1px solid #374151; /* Border for st.dataframe */
        border-radius: 6px;
        overflow: hidden; /* Ensures border-radius applies to table content */
    }
    /* For st.markdown table, styling is in style_table function */
    div[data-testid="stMarkdown"] > div[data-testid="element-container"] > div > table { margin-bottom: 25px; }

    .stApp > footer { visibility: hidden; }
    hr { border-top: 1px solid #374151; margin-top: 25px; margin-bottom: 25px; }
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
    text_color_light = "#d1d5db"; text_color_faint = "#6b7280"
    bg_header = "#1f2937"; bg_index_cols = "#111827"
    bg_data_cells = "#1f2937"; bg_net_cashflow = "#2b394c"
    border_color = "#374151"

    styled_df = df_to_style.style.format(
        lambda x: f"{x:,.0f}" if x != 0 else "-", na_rep="-"
    ) \
        .set_caption(f"<span style='font-size: 1.1em; font-weight:500; color: {text_color_light}; display:block; margin-bottom:8px; text-align:left;'>📋 Weekly Cashflow Breakdown</span>") \
        .set_properties(**{
            'font-size': '9pt', 'border': 'none', 'width': 'auto',
            'font-family': "'Inter', 'Segoe UI', sans-serif", 'color': text_color_light
        }) \
        .set_table_styles([
            {'selector': '', 'props': [('border-collapse', 'collapse')]},
            {'selector': 'caption', 'props': [('caption-side', 'top')]},
            {'selector': 'th.col_heading', 'props': [
                ('background-color', bg_header), ('color', text_color_light),
                ('font-weight', '500'), ('font-size', '9pt'), ('text-align', 'center'),
                ('padding', '8px 6px'), ('border', f'1px solid {border_color}')
            ]},
            {'selector': 'th.index_name', 'props': [
                ('background-color', bg_header), ('color', text_color_light),
                ('font-weight', '500'), ('font-size', '9pt'), ('text-align', 'left'),
                ('padding', '8px 6px'), ('border', f'1px solid {border_color}')
            ]},
            {'selector': 'th.row_heading', 'props': [
                ('background-color', bg_index_cols), ('color', text_color_light),
                ('font-weight', 'normal'), ('text-align', 'left'), ('padding', '8px 10px'),
                ('border', f'1px solid {border_color}')
            ]},
            {'selector': 'td', 'props': [
                ('background-color', bg_data_cells), ('color', text_color_light),
                ('text-align', 'right'), ('padding', '8px 10px'),
                ('border', f'1px solid {border_color}')
            ]},
            {'selector': 'th.row_heading.level0', 'props': [('font-weight', '500'), ('color', '#81a1c1')]},
        ])

    def color_zero_values(val):
        return f'color: {text_color_faint}' if val == 0 or pd.isna(val) else f'color: {text_color_light}'
    for col in df_to_style.columns:
        if df_to_style[col].dtype in ['int64', 'float64', np.number]:
             styled_df = styled_df.applymap(color_zero_values, subset=[col])

    if numeric_cols:
        valid_numeric_cols_for_subset = [col for col in numeric_cols if col in df_to_style.columns]
        if valid_numeric_cols_for_subset:
            try:
                def subtle_gradient_for_dark(s):
                    styles = [''] * len(s)
                    max_abs_val = s.abs().max()
                    if pd.isna(max_abs_val) or max_abs_val == 0: max_abs_val = 1
                    for i, val in s.items():
                        if val > 0:
                            opacity = min(0.3, 0.05 + (val / max_abs_val) * 0.25)
                            styles[s.index.get_loc(i)] = f'background-color: rgba(16, 185, 129, {opacity})'
                        elif val < 0:
                            opacity = min(0.3, 0.05 + (abs(val) / max_abs_val) * 0.25)
                            styles[s.index.get_loc(i)] = f'background-color: rgba(239, 68, 68, {opacity})'
                    return styles
                styled_df = styled_df.apply(subtle_gradient_for_dark, subset=valid_numeric_cols_for_subset, axis=0)
            except Exception as e: st.warning(f"Could not apply custom background gradient: {e}.")

    def style_net_cashflow_row(row):
        if row.name == ("Net Cashflow", ""):
            return [f'font-weight: 500; background-color: {bg_net_cashflow}; color: {text_color_light}; border: 1px solid {border_color}; font-size:10pt;'] * len(row)
        return [''] * len(row)
    styled_df = styled_df.apply(style_net_cashflow_row, axis=1)
    return styled_df

# --- Sidebar for Inputs ---
with st.sidebar:
    st.markdown("<h1>Inputs & Settings</h1>", unsafe_allow_html=True)
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
        "Upload Cashflow Data (CSV or Excel)", type=["csv", "xlsx"],
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
            else: st.error("Unsupported file type."); st.stop()
            st.success(f"File `{uploaded_file.name}` loaded successfully!")
            df.columns = df.columns.str.replace('\ufeff', '', regex=False).str.strip().str.lower()

            # --- 4. Validate Required Columns ---
            required_cols = {"party type", "party name", "due date", "expected date", "amount"}
            missing_cols = required_cols - set(df.columns)
            if missing_cols: st.error(f"Missing required columns: {', '.join(missing_cols)}."); st.stop()

            # --- 5. Data Type Conversion and Validation ---
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            if df['amount'].isnull().any(): st.warning("Some 'Amount' values were non-numeric and ignored.")
            for col in ["due date", "expected date"]:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                if df[col].isnull().any(): st.warning(f"Some '{col.title()}' values were not valid dates and ignored.")
            initial_row_count = len(df)
            df.dropna(subset=['amount', 'due date', 'expected date'], inplace=True)
            if len(df) < initial_row_count: st.info(f"{initial_row_count - len(df)} rows removed due to missing/invalid critical values.")
            if df.empty: st.error("No valid data remaining after processing."); st.stop()

            # --- 6. Allocation + Week Logic ---
            df["allocation date"] = df[["due date", "expected date"]].max(axis=1)
            df["week_start"] = df["allocation date"].dt.to_period("W").apply(lambda r: r.start_time)
            df["week_range"] = df["week_start"].apply(format_week_range)
            unique_week_starts = sorted(df["week_start"].unique())
            all_week_ranges_sorted = [format_week_range(ws) for ws in unique_week_starts]
            st.success(f"Data validated: {df.shape[0]} rows ready for forecasting.")
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
            cols1[0].metric(label="Total Inflow", value=f"{total_inflow:,.0f}", help="Sum of all positive cashflow amounts.")
            cols1[1].metric(label="Total Outflow", value=f"{total_outflow_val:,.0f}", help="Sum of all negative cashflow amounts.")
            delta_for_net, delta_color_for_net, help_text_net = None, "off", "Overall net change."
            if abs(total_outflow_val) > 0:
                net_perc_of_outflow = (net_overall_cashflow / abs(total_outflow_val)) * 100 if abs(total_outflow_val) != 0 else 0
                delta_for_net = f"{net_perc_of_outflow:.1f}% vs Outflow Mag."
                delta_color_for_net = "normal" if net_overall_cashflow >= 0 else "inverse"
                help_text_net += f" Net ({net_overall_cashflow:,.0f}) is {net_perc_of_outflow:.1f}% of outflow ({abs(total_outflow_val):,.0f})."
            elif net_overall_cashflow > 0: delta_for_net, delta_color_for_net, help_text_net = "Pure Inflow", "normal", help_text_net + " All inflows."
            elif net_overall_cashflow == 0 and total_inflow == 0 and total_outflow_val == 0: delta_for_net, help_text_net = "Zero Balance", help_text_net + " No movements."
            cols1[2].metric(label="Net Cashflow (Overall)", value=f"{net_overall_cashflow:,.0f}", delta=delta_for_net, delta_color=delta_color_for_net, help=help_text_net)
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            cols2 = st.columns(3)
            cols2[0].metric(label="Forecast Start Week", value=forecast_start_week_display, help="First week in forecast.")
            cols2[1].metric(label="Forecast End Week", value=forecast_end_week_display, help="Last week in forecast.")
            cols2[2].metric(label="No. of Forecast Weeks", value=str(num_forecast_weeks), help="Total weeks covered.")
            st.divider()

            # --- Data Preview ---
            with st.container():
                st.subheader("📄 Uploaded Data Preview (First 5 Valid Rows)")
                st.dataframe(df.head(), use_container_width=True, hide_index=True)
            st.divider()

            # --- Prepare Pivot Table Data ---
            all_parties = df[["party type", "party name"]].drop_duplicates()
            all_weeks_df = pd.DataFrame({"week_range": all_week_ranges_sorted})
            if not all_parties.empty and not all_weeks_df.empty:
                all_cross = pd.merge(all_parties, all_weeks_df, how="cross")
                grouped = df.groupby(["party type", "party name", "week_range"], as_index=False)["amount"].sum()
                complete_df = pd.merge(all_cross, grouped, on=["party type", "party name", "week_range"], how="left").fillna(0)
            else: complete_df = pd.DataFrame(columns=["party type", "party name", "week_range", "amount"])
            if not complete_df.empty:
                complete_df['week_range'] = pd.Categorical(complete_df['week_range'], categories=all_week_ranges_sorted, ordered=True)
                pivot_table = complete_df.pivot_table(index=["party type", "party name"], columns="week_range", values="amount", aggfunc="sum", fill_value=0, dropna=False)
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

                    # Altair chart configuration for dark theme
                    chart_bg_color = '#121212'; chart_text_color = '#9ca3af'; grid_color = '#374151'
                    positive_color = '#10b981'; negative_color = '#ef4444'; bar_label_color = '#f3f4f6'
                    text_color_light_for_title = "#d1d5db"


                    if not net_cashflow_series.empty:
                        net_df = net_cashflow_series.reset_index()
                        net_df.columns = ["Week Range", "Net Cashflow"]
                        net_df["Week Range"] = pd.Categorical(net_df["Week Range"], categories=all_week_ranges_sorted, ordered=True)
                        net_df = net_df.sort_values("Week Range")
                        
                        bars = alt.Chart(net_df).mark_bar(cornerRadiusTopLeft=2, cornerRadiusTopRight=2, size=20).encode(
                            x=alt.X("Week Range:N", sort=None, title="Week",
                                    axis=alt.Axis(labelAngle=-45, labelFontSize=8, titleFontSize=10,
                                                  titleColor=chart_text_color, labelColor=chart_text_color,
                                                  domainColor=grid_color, tickColor=grid_color, gridColor=grid_color,
                                                  format='%d %b')),
                            y=alt.Y("Net Cashflow:Q", title="Net Cashflow ($)",
                                    axis=alt.Axis(labelFontSize=8, titleFontSize=10,
                                                  titleColor=chart_text_color, labelColor=chart_text_color,
                                                  domainColor=grid_color, tickColor=grid_color, gridColor=grid_color,
                                                  format="~s")),
                            color=alt.condition(alt.datum["Net Cashflow"] >= 0, alt.value(positive_color), alt.value(negative_color)),
                            tooltip=[alt.Tooltip("Week Range:N", title="Week"), alt.Tooltip("Net Cashflow:Q", title="Amount", format=",.0f")]
                        ).properties(title=alt.TitleParams(text="📈 Weekly Net Cashflow Trend", anchor='middle', fontSize=14, fontWeight=500, color=text_color_light_for_title, dy=-10))
                        
                        text_labels = bars.mark_text(align="center", baseline="middle", dy=alt.expr("datum['Net Cashflow'] >= 0 ? -8 : 8"), fontSize=8, fontWeight=400).encode(
                            text=alt.Text("Net Cashflow:Q", format=",.0f"), color=alt.value(bar_label_color)
                        )
                        
                        chart = (bars + text_labels).properties(height=300, background=chart_bg_color).configure_view(
                            strokeOpacity=0 ).configure_axis( gridOpacity=0.3 )
                        st.altair_chart(chart, use_container_width=True)
                    else: st.info("ℹ️ Not enough data for Net Cashflow chart.") # Styled by CSS
                    
                    # --- Client and Supplier Wise Summary ---
                    st.divider()
                    st.subheader(" summarized Totals by Party Type")
                    if not df.empty:
                        summary_by_type = df.groupby("party type")["amount"].sum().reset_index()
                        summary_by_type.columns = ["Party Type", "Total Amount"]
                        customers_total = summary_by_type[summary_by_type["Party Type"].str.lower().str.contains("customer", case=False)]["Total Amount"].sum()
                        suppliers_total = summary_by_type[summary_by_type["Party Type"].str.lower().str.contains("supplier", case=False)]["Total Amount"].sum()
                        other_types_summary = summary_by_type[~summary_by_type["Party Type"].str.lower().str.contains("customer|supplier", case=False, regex=True)]
                        
                        col_summary1, col_summary2 = st.columns(2)
                        with col_summary1: st.metric(label="TOTAL FROM CUSTOMERS", value=f"{customers_total:,.0f}")
                        with col_summary2: st.metric(label="TOTAL TO SUPPLIERS", value=f"{suppliers_total:,.0f}")
                        
                        if not other_types_summary.empty:
                            st.markdown("##### Other Party Type Totals:")
                            for _, row in other_types_summary.iterrows():
                                st.markdown(f"- **{row['Party Type']}**: {row['Total Amount']:,.0f}")
                            st.caption("Positive: net inflow, Negative: net outflow.")
                        st.markdown("<br>", unsafe_allow_html=True)

                        chart_summary_data = []
                        if customers_total != 0: chart_summary_data.append({"Party Type": "Customers", "Amount": customers_total, "Flow": "Inflow"})
                        if suppliers_total != 0: chart_summary_data.append({"Party Type": "Suppliers", "Amount": suppliers_total, "Flow": "Outflow"})
                        for _, row in other_types_summary.iterrows():
                             chart_summary_data.append({"Party Type": row["Party Type"], "Amount": row["Total Amount"], "Flow": "Inflow" if row["Total Amount"] >=0 else "Outflow"})
                        
                        if chart_summary_data:
                            summary_chart_df = pd.DataFrame(chart_summary_data)
                            summary_bars = alt.Chart(summary_chart_df).mark_bar(size=30).encode(
                                x=alt.X('Amount:Q', title='Total Amount ($)',
                                        axis=alt.Axis(labelFontSize=9, titleFontSize=10, titleColor=chart_text_color, labelColor=chart_text_color,
                                                      domainColor=grid_color, tickColor=grid_color, gridColor=grid_color, format="~s")),
                                y=alt.Y('Party Type:N', sort='-x', title='Party Type',
                                        axis=alt.Axis(labelFontSize=9, titleFontSize=10, titleColor=chart_text_color, labelColor=chart_text_color,
                                                      domainColor=grid_color, tickColor=grid_color)),
                                color=alt.condition(alt.datum.Amount >= 0, alt.value(positive_color), alt.value(negative_color)),
                                tooltip=['Party Type', alt.Tooltip('Amount:Q', format=',.0f')]
                            ).properties(title=alt.TitleParams(text="📊 Summary by Party Type", anchor='middle', fontSize=14, fontWeight=500, color=text_color_light_for_title, dy=-5),
                                         height=alt.Step(40)).configure_view(strokeOpacity=0).configure_axis(gridOpacity=0.2).properties(background=chart_bg_color)
                            st.altair_chart(summary_bars, use_container_width=True)
                    else: st.info("No data to generate Client/Supplier summary.") # Styled by CSS

                    st.divider()
                    st.subheader("📤 Export Forecast")
                    towrite = BytesIO()
                    export_table = final_table.copy()
                    if isinstance(export_table.index, pd.MultiIndex): export_table = export_table.reset_index()
                    with pd.ExcelWriter(towrite, engine="xlsxwriter") as writer:
                        export_table.to_excel(writer, sheet_name="Cashflow Forecast", index=False)
                        workbook, worksheet = writer.book, writer.sheets["Cashflow Forecast"]
                        header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#4F81BD', 'font_color': '#FFFFFF', 'border': 1})
                        for col_num, value in enumerate(export_table.columns.values): worksheet.write(0, col_num, value, header_format)
                        worksheet.set_column(0, len(export_table.columns) -1 , 18)
                        money_format = workbook.add_format({'num_format': '#,##0'})
                        for col_idx, col_name in enumerate(export_table.columns):
                            is_party_col = col_name.lower() in ["party type", "party name"]
                            if not is_party_col and (export_table[col_name].dtype in ['int64', 'float64', np.number]):
                                 worksheet.set_column(col_idx, col_idx, None, money_format)
                    st.download_button(label="Download Forecast as Excel", data=towrite.getvalue(), file_name="cashflow_forecast.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") # Styled by CSS
                else: st.info("ℹ️ No forecast table to display.") # Styled by CSS
        except pd.errors.ParserError: st.error("❌ Error parsing the uploaded file.") # Styled by CSS
        except ImportError as ie:
            if "matplotlib" in str(ie).lower(): st.error("❌ Matplotlib is missing. Install with `pip install matplotlib`.")
            else: st.error(f"Import error: {ie}.")
            st.exception(ie)
        except Exception as e:
            st.error(f"An unexpected error occurred during processing.")
            st.exception(e)
else:
    st.info("👈 **Upload your cashflow file using the sidebar to get started!**") # Styled by CSS
    st.markdown("---")
    with st.expander("💡 How to Use This Dashboard", expanded=True):
        st.markdown("""
            Welcome to your interactive Cashflow Forecast Dashboard! This tool is designed to help you visualize your weekly financial projections based on your uploaded data.
            #### **Steps to Get Started:**
            1.  **📥 Prepare Your Data:**
                *   If new or unsure, **download the sample CSV template** from "Inputs & Settings" in the sidebar.
                *   Ensure your CSV/Excel has: `Party Type`, `Party Name`, `Due Date`, `Expected Date`, `Amount` (case-insensitive).
                    *   `Amount`: Positive for inflows, negative for outflows. Plain numbers only.
            2.  **📤 Upload Your File:** Use the sidebar uploader (CSV or XLSX).
            3.  **📊 View & Analyze Results:**
                *   **At a Glance Metrics:** Quick summary of totals and forecast period.
                *   **Data Preview:** First few rows of your validated data.
                *   **Detailed Forecast Table:** Weekly breakdown by party.
                *   **Net Cashflow Chart:** Visual trend of weekly net cashflow.
                *   **Summary by Party Type:** Aggregated totals for customers, suppliers, etc.
            4.  **💾 Download Forecast:** Export the detailed forecast as Excel.
            ---
            ✨ **Tips for Best Results:** Consistent date formats, numeric 'Amount' column.
            ---
            If issues arise, verify your file against the sample template.
            """)
    st.balloons()
