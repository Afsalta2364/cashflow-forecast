import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO
import numpy as np
# import json # No longer needed as we are not parsing the full JSON spec

# --- Page Setup ---
st.set_page_config(
    page_title="Cashflow Forecast Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Theme Colors (Inspired by Income Dashboard) ---
BG_PAGE = "#171E2E"
BG_SIDEBAR = "#252936"
BG_MAIN_CONTENT_WRAPPER = "#1E2A3A"
BG_CARD_ELEMENT = "#2A3B4D"
TEXT_PRIMARY = "#E0E6F1" # Used for chart text labels as per original JSON
TEXT_SECONDARY = "#A0A7B8"
ACCENT_TEAL = "#46D9C4"
ACCENT_RED = "#FF6B6B"
BORDER_COLOR_SOFT = "#3A4A5D"
BORDER_COLOR_MEDIUM = "#4b5563"
CHART_AXIS_LABEL_COLOR = "#e6eaf1" # From JSON config.axis.labelColor
CHART_AXIS_TITLE_COLOR = "#e6eaf1" # From JSON config.axis.titleColor
CHART_GRID_COLOR = "#31333F"       # From JSON config.axis.gridColor
CHART_TITLE_COLOR = "#fafafa"      # From JSON config.title.color


# --- Custom CSS for New Theme (Same as your previous version) ---
st.markdown(f"""
<style>
    /* --- Global Styles --- */
    body {{
        font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
        color: {TEXT_PRIMARY};
        background-color: {BG_PAGE} !important;
    }}
    .stApp {{
        background-color: {BG_PAGE};
    }}
    /* ... (rest of your CSS is kept as is) ... */
    .main-title-container {{ padding: 15px 25px; background: {BG_MAIN_CONTENT_WRAPPER}; border-radius: 0px; margin-bottom: 0px; text-align: left; border-bottom: 1px solid {BORDER_COLOR_SOFT}; }}
    .main-title {{ font-size: 1.8em; color: {TEXT_PRIMARY}; font-weight: 600; letter-spacing: 0.2px; }}
    .main-subtitle {{ font-size: 0.95em; color: {TEXT_SECONDARY}; margin-top: 3px; }}
    h2 {{ color: {TEXT_PRIMARY}; border-bottom: 1px solid {BORDER_COLOR_MEDIUM}; padding-bottom: 8px; margin-top: 25px; margin-bottom: 20px; font-weight: 500; font-size: 1.3em; text-align: left; padding-left: 5px; }}
    section[data-testid="stSidebar"] {{ background-color: {BG_SIDEBAR}; border-right: 1px solid {BORDER_COLOR_SOFT}; }}
    section[data-testid="stSidebar"] h1 {{ color: {ACCENT_TEAL} !important; font-weight: 500 !important; text-align: center !important; border-bottom: 1px solid {ACCENT_TEAL} !important; padding-bottom: 10px !important; font-size: 1.2em !important; margin-top: 10px !important; }}
    .streamlit-expanderHeader {{ font-size: 0.95em !important; font-weight: normal !important; color: {TEXT_SECONDARY} !important; padding: 8px 5px !important; border-bottom: 1px solid {BORDER_COLOR_SOFT}; }}
    .streamlit-expanderHeader:hover {{ color: {TEXT_PRIMARY} !important; background-color: rgba(255,255,255,0.05); }}
    section[data-testid="stSidebar"] .stFileUploader label {{ color: {TEXT_SECONDARY} !important; font-size: 0.9em !important; }}
    section[data-testid="stSidebar"] .stButton>button {{ background-color: {ACCENT_TEAL}; color: {BG_SIDEBAR} !important; border: none; border-radius: 6px; padding: 8px 16px; font-size: 0.85em; font-weight: 500; }}
    section[data-testid="stSidebar"] .stButton>button:hover {{ background-color: #3CD0B8; }}
    div[data-testid="stMetric"] {{ background-color: {BG_CARD_ELEMENT}; border: 1px solid {BORDER_COLOR_SOFT}; border-radius: 8px; padding: 18px; height: 100%; box-shadow: 0 2px 4px rgba(0,0,0,0.15); }}
    .stMetric > div > div:nth-child(1) {{ color: {TEXT_SECONDARY}; font-size: 0.8em; font-weight: 400; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.3px; }}
    .stMetric > div > div:nth-child(2) {{ color: {TEXT_PRIMARY}; font-size: 1.8em; font-weight: 600; }}
    .stMetric > div > div:nth-child(3) {{ font-size: 0.85em; font-weight: 500; }}
    .stMetric [data-testid="stMetricDelta"] svg {{ visibility: visible !important; }}
    .stMetric [data-testid="stMetricDelta"] div[data-delta-direction="positive"] {{ color: {ACCENT_TEAL} !important; }}
    .stMetric [data-testid="stMetricDelta"] div[data-delta-direction="negative"] {{ color: {ACCENT_RED} !important; }}
    .stDownloadButton>button {{ background-color: {ACCENT_TEAL}; color: {BG_SIDEBAR} !important; border: none; border-radius: 6px; font-weight: 500; padding: 10px 22px; font-size: 0.9em; }}
    .stDownloadButton>button:hover {{ background-color: #3CD0B8; }}
    div[data-testid="stAlert"] {{ border-radius: 6px; border-width: 1px; border-style: solid; padding: 12px 15px; font-size: 0.9em;}}
    div[data-testid="stAlert"][data-baseweb="alert-success"] {{ background-color: rgba(70, 217, 196, 0.15); border-color: {ACCENT_TEAL}; color: {ACCENT_TEAL}; }}
    div[data-testid="stAlert"][data-baseweb="alert-success"] svg {{ fill: {ACCENT_TEAL}; }}
    div[data-testid="stAlert"][data-baseweb="alert-info"]    {{ background-color: rgba(96, 165, 250, 0.15); border-color: #60a5fa; color: #93c5fd; }}
    div[data-testid="stAlert"][data-baseweb="alert-info"] svg{{ fill: #93c5fd; }}
    div[data-testid="stAlert"][data-baseweb="alert-warning"] {{ background-color: rgba(245, 158, 11, 0.15); border-color: #f59e0b; color: #fde68a; }}
    div[data-testid="stAlert"][data-baseweb="alert-warning"] svg{{ fill: #fde68a; }}
    div[data-testid="stAlert"][data-baseweb="alert-error"]   {{ background-color: rgba(255, 107, 107, 0.15); border-color: {ACCENT_RED}; color: {ACCENT_RED}; }}
    div[data-testid="stAlert"][data-baseweb="alert-error"] svg  {{ fill: {ACCENT_RED}; }}
    .stDataFrame {{ border: 1px solid {BORDER_COLOR_SOFT}; border-radius: 8px; overflow: hidden; background-color: {BG_CARD_ELEMENT}; }}
    div.stMarkdown > div[data-testid="element-container"] > div {{ display: flex; justify-content: center; width: 100%; }}
    div.stMarkdown > div[data-testid="element-container"] > div > table {{ margin-bottom: 20px; background-color: {BG_CARD_ELEMENT}; }}
    .stApp > footer {{ visibility: hidden; }}
    hr {{ border-top: 1px solid {BORDER_COLOR_MEDIUM}; margin-top: 25px; margin-bottom: 25px; }}
    .content-section-wrapper {{ background-color: {BG_MAIN_CONTENT_WRAPPER}; padding: 1px 20px 20px 20px; }}
</style>
""", unsafe_allow_html=True)

# --- Main Title Section ---
st.markdown("""
<div class='main-title-container'>
    <div class='main-title'>💰 Weekly Cashflow Forecast</div>
    <div class='main-subtitle'>Upload data to visualize your projected financial health.</div>
</div>
""", unsafe_allow_html=True)

# --- Helper Functions (Same as your previous version) ---
def format_week_range(start_date):
    end_date = start_date + pd.Timedelta(days=6)
    return f"{start_date.day} {start_date.strftime('%b')} - {end_date.day} {end_date.strftime('%b')}"

def style_table(df_to_style):
    numeric_cols = df_to_style.select_dtypes(include=np.number).columns.tolist()
    text_color_light = TEXT_PRIMARY; text_color_faint = TEXT_SECONDARY
    bg_base = BG_CARD_ELEMENT; bg_header_gradient_start = "#334155"; bg_header_gradient_end = BG_CARD_ELEMENT
    bg_index_cols = "#212E3C"; bg_net_cashflow = "#334155"
    border_color = BORDER_COLOR_SOFT
    shadow_light = "rgba(200, 200, 255, 0.03)"; shadow_dark = "rgba(0, 0, 0, 0.1)"
    data_col_min_width = '110px'; index_col_party_type_width = '100px'
    index_col_party_name_width = '120px'; index_col_week_range_literal_width = '90px'
    styled_df = df_to_style.style.format(
        lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) and x != 0 else ("-" if isinstance(x, (int, float)) and x == 0 else x),
        na_rep="-"
    ).set_caption(f"<span style='font-size: 1.1em; font-weight:500; color: {text_color_light}; display:block; margin-bottom:10px; text-align:center;'>📋 Weekly Cashflow Breakdown</span>") \
    .set_properties(**{'font-size': '9pt', 'border': 'none', 'font-family': "'Inter', 'Segoe UI', sans-serif", 'color': text_color_light, 'width': 'auto', 'margin-left': 'auto', 'margin-right': 'auto', 'border-radius': '8px', 'box-shadow': f'3px 3px 7px {shadow_dark}, -1px -1px 3px {shadow_light}', 'background-color': bg_base, 'overflow': 'hidden'}) \
    .set_table_styles([
        {'selector': '', 'props': [('border-collapse', 'separate'), ('border-spacing', '0px'), ('width', 'auto'), ('min-width', '65%'), ('max-width', '95%')]},
        {'selector': 'caption', 'props': [('caption-side', 'top'), ('padding-top', '10px')]},
        {'selector': 'th', 'props': [('text-align', 'center'), ('vertical-align', 'middle'), ('padding', '10px 8px'), ('font-weight', '500'), ('font-size', '9pt'), ('color', text_color_light), ('border-bottom', f'1px solid {border_color}')]},
        {'selector': 'th.col_heading, th.index_name', 'props': [('background', f'linear-gradient(to bottom, {bg_header_gradient_start}, {bg_header_gradient_end})'), ('border-right', f'1px solid {border_color}')]},
        {'selector': 'th.col_heading:last-child, th.index_name:last-child', 'props': [('border-right', 'none')]},
        {'selector': 'th.col_heading', 'props': [('min-width', data_col_min_width), ('max-width', data_col_min_width)]},
        {'selector': 'th.index_name', 'props': [('min-width', index_col_week_range_literal_width), ('max-width', index_col_week_range_literal_width)]},
        {'selector': 'th.row_heading', 'props': [('background-color', bg_index_cols), ('border-right', f'1px solid {border_color}')]},
        {'selector': 'th.row_heading.level0', 'props': [('font-weight', '500'), ('color', ACCENT_TEAL), ('min-width', index_col_party_type_width), ('max-width', index_col_party_type_width)]},
        {'selector': 'th.row_heading.level1', 'props': [('min-width', index_col_party_name_width), ('max-width', index_col_party_name_width)]},
        {'selector': 'td', 'props': [('background-color', bg_base), ('text-align', 'center'), ('vertical-align', 'middle'), ('padding', '10px 8px'), ('border-bottom', f'1px solid {border_color}'), ('border-right', f'1px solid {border_color}'), ('min-width', data_col_min_width), ('max-width', data_col_min_width)]},
        {'selector': 'td:last-child', 'props': [('border-right', 'none')]},
        {'selector': 'tr:last-child td, tr:last-child th.row_heading', 'props': [('border-bottom', 'none')]},
    ])
    def color_zero_values(val): return f'color: {text_color_faint};' if (isinstance(val, (int,float)) and val == 0) or pd.isna(val) else f'color: {text_color_light};'
    data_cols_to_style = [col for col in df_to_style.columns if df_to_style[col].dtype in [np.int64, np.float64, 'int64', 'float64']]
    if data_cols_to_style: styled_df = styled_df.applymap(color_zero_values, subset=pd.IndexSlice[:, data_cols_to_style])
    if numeric_cols:
        valid_numeric_cols_for_subset = [col for col in numeric_cols if col in df_to_style.columns]
        if valid_numeric_cols_for_subset:
            try:
                def highlight_cells_for_dark_theme(s):
                    styles = [''] * len(s); s_numeric = pd.to_numeric(s, errors='coerce').dropna()
                    if s_numeric.empty: return styles
                    max_abs_val = s_numeric.abs().max()
                    if pd.isna(max_abs_val) or max_abs_val == 0: max_abs_val = 1
                    for i, val_orig in s.items():
                        idx_loc = s.index.get_loc(i); val = pd.to_numeric(val_orig, errors='coerce')
                        if pd.isna(val): continue
                        if val > 0: opacity = min(0.5, 0.15 + (val / max_abs_val) * 0.35); r, g, b = tuple(int(ACCENT_TEAL.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)); styles[idx_loc] = f'background-color: rgba({r},{g},{b},{opacity:.2f});'
                        elif val < 0: opacity = min(0.5, 0.15 + (abs(val) / max_abs_val) * 0.35); r, g, b = tuple(int(ACCENT_RED.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)); styles[idx_loc] = f'background-color: rgba({r},{g},{b},{opacity:.2f});'
                    return styles
                styled_df = styled_df.apply(highlight_cells_for_dark_theme, subset=valid_numeric_cols_for_subset, axis=0)
            except Exception as e: st.warning(f"Could not apply custom cell highlights: {e}.")
    def style_net_cashflow_row(row):
        if row.name == ("Net Cashflow", ""): return [f'font-weight: 500; background-color: {bg_net_cashflow}; color: {text_color_light}; font-size:9.5pt; text-align:center; vertical-align:middle; border-top: 2px solid {border_color}; border-bottom:none; border-left:none; border-right:none;'] * len(row)
        return [''] * len(row)
    styled_df = styled_df.apply(style_net_cashflow_row, axis=1)
    return styled_df

# --- Sidebar for Inputs (Same as your previous version) ---
with st.sidebar:
    st.markdown("<h1>Inputs & Settings</h1>", unsafe_allow_html=True)
    st.markdown("---", unsafe_allow_html=True)
    with st.expander("📥 Download Sample Template", expanded=False):
        sample_data = pd.DataFrame({"Party Type": ["Supplier", "Customer", "Supplier", "Internal"],"Party Name": ["ABC Ltd", "XYZ Inc", "DEF Supplies", "Loan Repay"],"Due Date": ["2024-07-15", "2024-07-10", "2024-07-20", "2024-07-25"],"Expected Date": ["2024-07-20", "2024-07-14", "2024-07-22", "2024-07-25"],"Amount": [-10000, 12000, -5000, -2500]})
        sample_data["Due Date"] = pd.to_datetime(sample_data["Due Date"]).dt.strftime('%Y-%m-%d')
        sample_data["Expected Date"] = pd.to_datetime(sample_data["Expected Date"]).dt.strftime('%Y-%m-%d')
        st.download_button(label="Download Template CSV", data=sample_data.to_csv(index=False).encode('utf-8'), file_name="cashflow_template.csv", mime="text/csv", help="Use this template to structure your cashflow data.")
    st.markdown("---", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Cashflow Data (CSV or Excel)", type=["csv", "xlsx"], help="Upload your CSV or Excel file...")
    st.markdown("---", unsafe_allow_html=True)
    st.caption(f"<p style='color:{TEXT_SECONDARY}; font-size:0.8em;'>Developed with ❤️ by AI</p>", unsafe_allow_html=True)


# --- Simplified Altair Chart Theming Options ---
# Derived from the general look of the provided JSON config, but more concise.
chart_theme_options = {
    "background": BG_CARD_ELEMENT,
    "font": "'Inter', 'Segoe UI', Roboto, sans-serif", # Match global font
    "title": { # For titles set via .properties(title=...)
        "color": CHART_TITLE_COLOR,
        "fontSize": 16,
        "fontWeight": 600,
        "anchor": "start", # Aligns title to the start of the chart area
        "orient": "top",
        "offset": 10, # Adjust spacing from chart
    },
    "axis": {
        "labelColor": CHART_AXIS_LABEL_COLOR,
        "labelFontSize": 12,
        "labelFontWeight": "normal", # 400
        "titleColor": CHART_AXIS_TITLE_COLOR,
        "titleFontSize": 14,
        "titleFontWeight": "normal", # 400
        "gridColor": CHART_GRID_COLOR,
        "domain": False, # No axis domain line
        "ticks": False,  # No axis ticks
        "titlePadding": 16,
        "labelPadding": 16,
    },
    "legend": {
        "labelColor": CHART_AXIS_LABEL_COLOR, # Re-use axis label color for legend
        "labelFontSize": 12,
        "titleColor": CHART_AXIS_TITLE_COLOR, # Re-use axis title color for legend
        "titleFontSize": 12,
        "symbolType": "square",
        "padding": 5,
    },
    "view": {
        "stroke": "transparent" # No border around the chart view itself
    },
    "bar": { # Specific to bar marks
        "discreteBandSize": {"band": 0.85} # Bar width relative to band (for nominal x-axis)
    },
    "text": { # Default for text marks
        "color": TEXT_PRIMARY, # Color for text labels on bars
        "fontSize": 8
    }
}


# --- Main Panel for Results ---
st.markdown("<div class='content-section-wrapper'>", unsafe_allow_html=True)

if uploaded_file:
    with st.spinner("🚀 Processing your file... Hold tight!"):
        try:
            # --- 1. File Load and Normalization (Same as your previous version) ---
            if uploaded_file.name.endswith(".csv"): df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".xlsx"): df = pd.read_excel(uploaded_file, sheet_name=0, engine='openpyxl')
            else: st.error("Unsupported file type."); st.stop()
            st.success(f"File `{uploaded_file.name}` loaded successfully!")
            df.columns = df.columns.str.replace('\ufeff', '', regex=False).str.strip().str.lower()
            required_cols = {"party type", "party name", "due date", "expected date", "amount"}
            missing_cols = required_cols - set(df.columns)
            if missing_cols: st.error(f"Missing required columns: {', '.join(missing_cols)}."); st.stop()
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            if df['amount'].isnull().any(): st.warning("Some 'Amount' values were non-numeric and ignored.")
            for col in ["due date", "expected date"]:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                if df[col].isnull().any(): st.warning(f"Some '{col.title()}' values were not valid dates and ignored.")
            initial_row_count = len(df); df.dropna(subset=['amount', 'due date', 'expected date', 'party type', 'party name'], inplace=True)
            if len(df) < initial_row_count: st.info(f"{initial_row_count - len(df)} rows removed due to missing/invalid critical values.")
            if df.empty: st.error("No valid data remaining after processing."); st.stop()
            df["allocation date"] = df[["due date", "expected date"]].max(axis=1)
            df["week_start"] = df["allocation date"].dt.to_period("W").apply(lambda r: r.start_time)
            df["week_range"] = df["week_start"].apply(format_week_range)
            unique_week_starts = sorted(df["week_start"].unique())
            all_week_ranges_sorted = [format_week_range(ws) for ws in unique_week_starts]
            st.success(f"Data validated: {df.shape[0]} rows ready for forecasting.")
            st.divider()

            # --- 4. Key Metrics Section (Same as your previous version) ---
            st.subheader("🚀 At a Glance: Forecast Summary")
            total_inflow = df[df['amount'] > 0]['amount'].sum(); total_outflow_val = df[df['amount'] < 0]['amount'].sum(); net_overall_cashflow = df['amount'].sum()
            forecast_start_week_display, forecast_end_week_display, num_forecast_weeks = "N/A", "N/A", 0
            if all_week_ranges_sorted: forecast_start_week_display, forecast_end_week_display, num_forecast_weeks = all_week_ranges_sorted[0], all_week_ranges_sorted[-1], len(all_week_ranges_sorted)
            cols1 = st.columns(3)
            cols1[0].metric(label="Total Inflow", value=f"{total_inflow:,.0f}", help="Sum of all positive cashflow amounts.")
            cols1[1].metric(label="Total Outflow", value=f"{total_outflow_val:,.0f}", help="Sum of all negative cashflow amounts.")
            delta_for_net, delta_color_for_net, help_text_net = None, "off", "Overall net change."
            if abs(total_outflow_val) > 0: net_perc_of_outflow = (net_overall_cashflow / abs(total_outflow_val)) * 100 if abs(total_outflow_val) != 0 else 0; delta_for_net = f"{net_perc_of_outflow:.1f}% vs Outflow Mag."; delta_color_for_net = "normal" if net_overall_cashflow >= 0 else "inverse"; help_text_net += f" Net ({net_overall_cashflow:,.0f}) is {net_perc_of_outflow:.1f}% of outflow ({abs(total_outflow_val):,.0f})."
            elif net_overall_cashflow > 0: delta_for_net, delta_color_for_net, help_text_net = "Pure Inflow", "normal", help_text_net + " All inflows."
            elif net_overall_cashflow == 0 and total_inflow == 0 and total_outflow_val == 0: delta_for_net, help_text_net = "Zero Balance", help_text_net + " No movements."
            cols1[2].metric(label="Net Cashflow (Overall)", value=f"{net_overall_cashflow:,.0f}", delta=delta_for_net, delta_color=delta_color_for_net, help=help_text_net)
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            cols2 = st.columns(3)
            cols2[0].metric(label="Forecast Start Week", value=forecast_start_week_display, help="First week in forecast.")
            cols2[1].metric(label="Forecast End Week", value=forecast_end_week_display, help="Last week in forecast.")
            cols2[2].metric(label="No. of Forecast Weeks", value=str(num_forecast_weeks), help="Total weeks covered.")
            st.divider()

            # --- 5. Data Preview (Same as your previous version) ---
            with st.container():
                st.subheader("📄 Uploaded Data Preview (First 5 Valid Rows)")
                st.dataframe(df[['party type', 'party name', 'due date', 'expected date', 'amount', 'allocation date', 'week_range']].head(), use_container_width=True, hide_index=True)
            st.divider()

            # --- 6. Prepare Pivot Table Data (Same as your previous version) ---
            all_parties = df[["party type", "party name"]].drop_duplicates().reset_index(drop=True)
            all_weeks_df = pd.DataFrame({"week_range": all_week_ranges_sorted})
            final_table = pd.DataFrame(columns=["No Data"]); net_cashflow_series = pd.Series(dtype='float64')
            if not all_parties.empty and not all_weeks_df.empty:
                all_cross = pd.merge(all_parties, all_weeks_df, how="cross")
                grouped = df.groupby(["party type", "party name", "week_range"], as_index=False)["amount"].sum()
                complete_df = pd.merge(all_cross, grouped, on=["party type", "party name", "week_range"], how="left").fillna(0)
            else: complete_df = pd.DataFrame(columns=["party type", "party name", "week_range", "amount"])
            if not complete_df.empty:
                complete_df['week_range'] = pd.Categorical(complete_df['week_range'], categories=all_week_ranges_sorted, ordered=True)
                pivot_table = complete_df.pivot_table(index=["party type", "party name"], columns="week_range", values="amount", aggfunc="sum", fill_value=0, dropna=False)
                if not pivot_table.empty:
                    net_cashflow_series = pivot_table.sum(numeric_only=True)
                    net_row_df = pd.DataFrame([net_cashflow_series], index=pd.MultiIndex.from_tuples([("Net Cashflow", "")]))
                    net_row_df.index.names = ["party type", "party name"]
                    final_table = pd.concat([pivot_table, net_row_df])
            
            # --- 7. Main Forecast Display Area ---
            with st.container(): 
                st.subheader("📊 Detailed Weekly Cashflow Forecast")
                if not final_table.empty and "No Data" not in final_table.columns:
                    st.markdown(style_table(final_table).to_html(), unsafe_allow_html=True)
                    
                    # --- Weekly Net Cashflow Trend Chart (Using simplified Altair theming) ---
                    if not net_cashflow_series.empty:
                        net_df = net_cashflow_series.reset_index(); net_df.columns = ["Week Range", "Net Cashflow"]
                        if not net_df.empty and not net_df["Net Cashflow"].isnull().all():
                            net_df["Week Range"] = pd.Categorical(net_df["Week Range"], categories=all_week_ranges_sorted, ordered=True); net_df = net_df.sort_values("Week Range")
                            
                            bars = alt.Chart(net_df).mark_bar(
                                cornerRadiusTopLeft=2,
                                cornerRadiusTopRight=2,
                                size=18 
                            ).encode(
                                x=alt.X("Week Range:N", sort=None, title="Week", 
                                        axis=alt.Axis(format="%d %b", labelAngle=-45)),
                                y=alt.Y("Net Cashflow:Q", title="Net Cashflow ($)", 
                                        axis=alt.Axis(format="~s")),
                                color=alt.condition(alt.datum["Net Cashflow"] >= 0, alt.value(ACCENT_TEAL), alt.value(ACCENT_RED)),
                                tooltip=[alt.Tooltip("Week Range:N", title="Week"), 
                                         alt.Tooltip("Net Cashflow:Q", title="Amount", format=",.0f")]
                            )
                            
                            text_labels = bars.mark_text(
                                align="center",
                                baseline="middle",
                                dy=alt.expr("datum['Net Cashflow'] >= 0 ? -7 : 7"),
                                fontSize=8 # This will be overridden by chart_theme_options['text']['fontSize'] if that key is used
                            ).encode(
                                text=alt.Text("Net Cashflow:Q", format=",.0f"), 
                                color=alt.value(TEXT_PRIMARY) # Explicit color for labels on bars
                            )
                            
                            chart = (bars + text_labels).properties(
                                title="📈 Weekly Net Cashflow Trend",
                                height=280,
                                padding={"bottom": 20} 
                            ).configure(**chart_theme_options) # Apply the theme dictionary

                            st.altair_chart(chart, use_container_width=True)
                    
                    st.divider()
                    # --- Summarized Totals by Party Type ---
                    st.subheader(" summarized Totals by Party Type")
                    if not df.empty:
                        summary_by_type = df.groupby("party type")["amount"].sum().reset_index(); summary_by_type.columns = ["Party Type", "Total Amount"]
                        customers_total = summary_by_type[summary_by_type["Party Type"].str.lower().str.contains("customer", case=False)]["Total Amount"].sum()
                        suppliers_total = summary_by_type[summary_by_type["Party Type"].str.lower().str.contains("supplier", case=False)]["Total Amount"].sum()
                        other_types_summary = summary_by_type[~summary_by_type["Party Type"].str.lower().str.contains("customer|supplier", case=False, regex=True)]
                        col_summary1, col_summary2 = st.columns(2)
                        with col_summary1: st.metric(label="TOTAL FROM CUSTOMERS", value=f"{customers_total:,.0f}")
                        with col_summary2: st.metric(label="TOTAL TO SUPPLIERS", value=f"{suppliers_total:,.0f}")
                        if not other_types_summary.empty:
                            st.markdown(f"<h5 style='color:{TEXT_PRIMARY};'>Other Party Type Totals:</h5>", unsafe_allow_html=True)
                            for _, row in other_types_summary.iterrows():
                                st.markdown(f"<span style='color:{TEXT_SECONDARY};'>- <strong>{row['Party Type']}</strong>: {row['Total Amount']:,.0f}</span>", unsafe_allow_html=True)
                            st.caption(f"<p style='color:{TEXT_SECONDARY};'>Positive: net inflow, Negative: net outflow.</p>", unsafe_allow_html=True)

                        chart_summary_data = []
                        if customers_total != 0: chart_summary_data.append({"Party Type": "Customers", "Amount": customers_total})
                        if suppliers_total != 0: chart_summary_data.append({"Party Type": "Suppliers", "Amount": suppliers_total})
                        for _, row in other_types_summary.iterrows(): chart_summary_data.append({"Party Type": row["Party Type"], "Amount": row["Total Amount"]})
                        if chart_summary_data:
                            summary_chart_df = pd.DataFrame(chart_summary_data)
                            if not summary_chart_df.empty and not summary_chart_df["Amount"].isnull().all():
                                summary_bars = alt.Chart(summary_chart_df).mark_bar(size=25).encode(
                                    x=alt.X('Amount:Q', title='Total Amount ($)', axis=alt.Axis(format="~s")),
                                    y=alt.Y('Party Type:N', sort='-x', title='Party Type'),
                                    color=alt.condition(alt.datum.Amount >= 0, alt.value(ACCENT_TEAL), alt.value(ACCENT_RED)),
                                    tooltip=['Party Type', alt.Tooltip('Amount:Q', format=',.0f')]
                                ).properties(title="📊 Summary by Party Type", height=alt.Step(35) 
                                ).configure(**chart_theme_options) # Apply the theme dictionary
                                st.altair_chart(summary_bars, use_container_width=True)
                    else: st.info("No base data for Client/Supplier summary.")

                    # --- 8. Export Forecast (Same as your previous version, styling adapted in helper) ---
                    st.divider()
                    st.subheader("📤 Export Forecast")
                    towrite = BytesIO()
                    export_table = final_table.copy()
                    if isinstance(export_table.index, pd.MultiIndex): export_table = export_table.reset_index()
                    with pd.ExcelWriter(towrite, engine="xlsxwriter") as writer:
                        export_table.to_excel(writer, sheet_name="Cashflow Forecast", index=False)
                        workbook  = writer.book; worksheet = writer.sheets["Cashflow Forecast"]
                        header_bg_excel = BG_SIDEBAR; header_font_excel = TEXT_PRIMARY
                        cell_bg_excel = BG_CARD_ELEMENT; cell_font_excel = TEXT_PRIMARY
                        header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': header_bg_excel, 'font_color': header_font_excel, 'border': 1, 'border_color': BORDER_COLOR_MEDIUM})
                        for col_num, value in enumerate(export_table.columns.values): worksheet.write(0, col_num, value, header_format)
                        worksheet.set_column(0, 0, 20); worksheet.set_column(1, 1, 25)
                        if len(export_table.columns) > 2: worksheet.set_column(2, len(export_table.columns) -1 , 18)
                        money_format = workbook.add_format({'num_format': '#,##0', 'font_color': cell_font_excel, 'bg_color': cell_bg_excel, 'border':1, 'border_color': BORDER_COLOR_SOFT})
                        text_format = workbook.add_format({'font_color': cell_font_excel, 'bg_color': cell_bg_excel, 'border':1, 'border_color': BORDER_COLOR_SOFT})
                        net_cashflow_row_format_num = workbook.add_format({'num_format': '#,##0', 'bold': True, 'font_color': cell_font_excel, 'bg_color': "#334155", 'border':1, 'border_color': BORDER_COLOR_SOFT, 'top_color': BORDER_COLOR_MEDIUM, 'top':2})
                        net_cashflow_row_format_text = workbook.add_format({'bold': True, 'font_color': cell_font_excel, 'bg_color': "#334155", 'border':1, 'border_color': BORDER_COLOR_SOFT, 'top_color': BORDER_COLOR_MEDIUM, 'top':2})
                        for row_num_excel in range(len(export_table)):
                            is_net_row = "party type" in export_table.columns and export_table.iloc[row_num_excel]["party type"] == "Net Cashflow"
                            for col_idx_excel, col_name_excel in enumerate(export_table.columns):
                                cell_val_excel = export_table.iloc[row_num_excel, col_idx_excel]
                                current_num_fmt = net_cashflow_row_format_num if is_net_row else money_format
                                current_text_fmt = net_cashflow_row_format_text if is_net_row else text_format
                                if col_name_excel.lower() not in ["party type", "party name"] and pd.api.types.is_number(cell_val_excel):
                                    worksheet.write_number(row_num_excel + 1, col_idx_excel, cell_val_excel, current_num_fmt)
                                else:
                                    worksheet.write_string(row_num_excel + 1, col_idx_excel, str(pd.NA if pd.isna(cell_val_excel) else cell_val_excel) , current_text_fmt)
                    st.download_button(label="Download Forecast as Excel", data=towrite.getvalue(), file_name="cashflow_forecast.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                else: st.info("ℹ️ No forecast table to display.")
        except pd.errors.ParserError: st.error("❌ Error parsing the uploaded file.")
        except ImportError as ie:
            if "matplotlib" in str(ie).lower(): st.error("❌ Matplotlib is missing.")
            elif "openpyxl" in str(ie).lower(): st.error("❌ openpyxl is missing for Excel files.")
            else: st.error(f"Import error: {ie}.")
            st.exception(ie)
        except Exception as e: st.error(f"An unexpected error occurred: {e}"); st.exception(e)
else:
    # --- Initial Landing Page Content (Same as your previous version) ---
    st.info("👈 **Upload your cashflow file using the sidebar to get started!**")
    st.markdown("---") 
    with st.expander("💡 How to Use This Dashboard", expanded=True): 
        st.markdown(f"""
            <p style='color:{TEXT_PRIMARY};'>Welcome to your interactive Weekly Cashflow Forecast Dashboard! This tool helps you visualize your projected financial health.</p>
            <h4 style='color:{ACCENT_TEAL}; margin-top:15px;'>Steps to Get Started:</h4>
            <ol style='color:{TEXT_SECONDARY};'>
                <li><strong>Prepare Your Data:</strong> Ensure CSV/Excel with columns: `Party Type`, `Party Name`, `Due Date`, `Expected Date`, `Amount`. (Download sample from sidebar).</li>
                <li><strong>Upload Your File:</strong> Use the sidebar uploader.</li>
                <li><strong>View & Analyze Results:</strong> Explore metrics, tables, and charts.</li>
                <li><strong>Download Forecast:</strong> Export data to Excel.</li>
            </ol>
            <p style='color:{TEXT_SECONDARY}; font-size:0.9em; margin-top:15px;'>✨ Tips: Use YYYY-MM-DD for dates. Ensure 'Amount' is numeric.</p>
            """, unsafe_allow_html=True)
    st.balloons()

st.markdown("</div>", unsafe_allow_html=True) # Close content-section-wrapper
