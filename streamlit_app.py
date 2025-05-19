import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO
import numpy as np

# --- Page Setup ---
st.set_page_config(
    page_title="Elegant Cashflow Dashboard",
    page_icon="💎", # New icon for elegance
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Fresh & Elegant Light Theme Colors ---
COLOR_BACKGROUND_PAGE = "#F8F9FA"        # Very light gray, almost white
COLOR_BACKGROUND_CONTENT = "#FFFFFF"     # Pure White for cards, main content blocks
COLOR_TEXT_PRIMARY = "#212529"           # Very Dark Gray (Bootstrap's default body text)
COLOR_TEXT_SECONDARY = "#6C757D"         # Medium Gray (Bootstrap's secondary text)
COLOR_TEXT_PLACEHOLDER = "#ADB5BD"       # Lighter Gray
COLOR_ACCENT_PRIMARY = "#0D6EFD"         # Bootstrap Blue (a standard, elegant blue)
COLOR_ACCENT_PRIMARY_LIGHT = "#E7F1FF"   # Very light blue for hover/active states or backgrounds
COLOR_ACCENT_POSITIVE = "#198754"        # Bootstrap Green
COLOR_ACCENT_NEGATIVE = "#DC3545"        # Bootstrap Red
COLOR_BORDER_PRIMARY = "#DEE2E6"         # Light Gray (Bootstrap's default border)
COLOR_BORDER_SECONDARY = "#CED4DA"       # Slightly darker border
COLOR_SHADOW_LIGHT = "rgba(0, 0, 0, 0.05)" # Softer shadow
COLOR_SHADOW_MEDIUM = "rgba(0, 0, 0, 0.075)"# Slightly more pronounced shadow for cards

# --- Custom CSS for Fresh & Elegant Light Theme ---
st.markdown(f"""
<style>
    /* --- Global Styles --- */
    body, .stApp {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; /* Common modern font stack */
        color: {COLOR_TEXT_PRIMARY};
        background-color: {COLOR_BACKGROUND_PAGE} !important;
    }}
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: {COLOR_BACKGROUND_PAGE}; }}
    ::-webkit-scrollbar-thumb {{ background: {COLOR_BORDER_SECONDARY}; border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: {COLOR_TEXT_SECONDARY}; }}

    /* --- Main Title Header --- */
    .main-title-container {{
        padding: 25px 30px;
        background: linear-gradient(to right, {COLOR_ACCENT_PRIMARY_LIGHT}, {COLOR_BACKGROUND_CONTENT}); /* Subtle gradient */
        border-bottom: 1px solid {COLOR_BORDER_PRIMARY};
        margin-bottom: 0px; /* Will be wrapped in content-section */
    }}
    .main-title {{
        font-size: 2.2em;
        color: {COLOR_TEXT_PRIMARY};
        font-weight: 600;
    }}
    .main-subtitle {{
        font-size: 1.05em;
        color: {COLOR_TEXT_SECONDARY};
        margin-top: 5px;
    }}

    /* --- Subheader Styling (st.subheader) --- */
    h2 {{ /* Targets st.subheader */
        color: {COLOR_TEXT_PRIMARY};
        border-bottom: 1px solid {COLOR_BORDER_PRIMARY};
        padding-bottom: 10px;
        margin-top: 25px;
        margin-bottom: 20px;
        font-weight: 500;
        font-size: 1.45em;
    }}

    /* --- Sidebar --- */
    section[data-testid="stSidebar"] {{
        background-color: {COLOR_BACKGROUND_CONTENT};
        border-right: 1px solid {COLOR_BORDER_PRIMARY};
        padding: 20px 15px; /* Uniform padding */
    }}
    section[data-testid="stSidebar"] h1 {{ /* Sidebar Title */
        color: {COLOR_ACCENT_PRIMARY} !important;
        font-weight: 600 !important;
        text-align: left !important; /* Align left for a cleaner look */
        border-bottom: 2px solid {COLOR_ACCENT_PRIMARY} !important;
        padding-bottom: 10px !important;
        font-size: 1.3em !important;
        margin: 0 0 25px 0 !important; /* Remove default margins, add bottom */
    }}
    .streamlit-expanderHeader {{
        font-size: 1em !important; /* Larger expander header */
        font-weight: 500 !important;
        color: {COLOR_TEXT_PRIMARY} !important; /* Darker for more importance */
        padding: 12px 10px !important;
        border-radius: 6px; /* Rounded expander */
        margin-bottom: 8px;
        border: 1px solid transparent;
    }}
    .streamlit-expanderHeader:hover {{
        color: {COLOR_ACCENT_PRIMARY} !important;
        background-color: {COLOR_ACCENT_PRIMARY_LIGHT} !important;
        border: 1px solid {COLOR_ACCENT_PRIMARY} !important;
    }}
    section[data-testid="stSidebar"] .stFileUploader label {{
        color: {COLOR_TEXT_PRIMARY} !important; /* Darker label */
        font-size: 0.95em !important;
        font-weight: 500;
        padding-bottom: 8px; /* Space for the drop zone */
    }}
     section[data-testid="stSidebar"] .stFileUploader > div > div {{ /* Target the drop zone */
        border-color: {COLOR_BORDER_SECONDARY};
     }}
    section[data-testid="stSidebar"] .stButton>button {{ /* Sidebar buttons */
        background-color: {COLOR_ACCENT_PRIMARY};
        color: {COLOR_BACKGROUND_CONTENT} !important;
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
        font-size: 0.95em;
        font-weight: 500;
        width: 100%;
        transition: background-color 0.2s ease;
    }}
    section[data-testid="stSidebar"] .stButton>button:hover {{
        background-color: #0B5ED7; /* Darker Bootstrap Blue */
    }}
    section[data-testid="stSidebar"] .stButton.secondary > button {{ /* For secondary actions if needed */
        background-color: {COLOR_BACKGROUND_CONTENT};
        color: {COLOR_ACCENT_PRIMARY} !important;
        border: 1px solid {COLOR_ACCENT_PRIMARY};
    }}
     section[data-testid="stSidebar"] .stButton.secondary > button:hover {{
        background-color: {COLOR_ACCENT_PRIMARY_LIGHT};
    }}


    /* --- Metric Cards --- */
    div[data-testid="stMetric"] {{
        background-color: {COLOR_BACKGROUND_CONTENT};
        border: 1px solid {COLOR_BORDER_PRIMARY};
        border-radius: 8px;
        padding: 22px;
        height: 100%;
        box-shadow: 0 5px 15px {COLOR_SHADOW_LIGHT};
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }}
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 20px {COLOR_SHADOW_MEDIUM};
    }}
    .stMetric > div > div:nth-child(1) {{ /* Metric Label */
        color: {COLOR_TEXT_SECONDARY};
        font-size: 0.9em;
        font-weight: 500;
        margin-bottom: 8px;
        text-transform: capitalize; /* Less shouty */
    }}
    .stMetric > div > div:nth-child(2) {{ /* Metric Value */
        color: {COLOR_TEXT_PRIMARY};
        font-size: 2.2em;
        font-weight: 600;
        line-height: 1.1;
    }}
    .stMetric > div > div:nth-child(3) {{ /* Metric Delta */
        font-size: 0.95em;
        font-weight: 500;
        padding-top: 5px;
    }}
    .stMetric [data-testid="stMetricDelta"] svg {{ visibility: visible !important; }}
    .stMetric [data-testid="stMetricDelta"] div[data-delta-direction="positive"] {{ color: {COLOR_ACCENT_POSITIVE} !important; }}
    .stMetric [data-testid="stMetricDelta"] div[data-delta-direction="negative"] {{ color: {COLOR_ACCENT_NEGATIVE} !important; }}

    /* --- Main Download Button --- */
    .stDownloadButton>button {{
        background-color: {COLOR_ACCENT_PRIMARY};
        color: {COLOR_BACKGROUND_CONTENT} !important;
        border: none;
        border-radius: 6px;
        font-weight: 500;
        padding: 10px 24px;
        font-size: 1em;
        transition: background-color 0.2s ease;
    }}
    .stDownloadButton>button:hover {{ background-color: #0B5ED7; }}

    /* --- Alert Messages --- */
    div[data-testid="stAlert"] {{ border-radius: 6px; border-width: 1px; border-style: solid; padding: 15px; font-size: 0.95em; box-shadow: 0 2px 8px {COLOR_SHADOW_LIGHT}; }}
    div[data-testid="stAlert"][data-baseweb="alert-success"] {{ background-color: #D1E7DD; border-color: #A3CFBB; color: #0A3622; }}
    div[data-testid="stAlert"][data-baseweb="alert-success"] svg {{ fill: {COLOR_ACCENT_POSITIVE}; }}
    div[data-testid="stAlert"][data-baseweb="alert-info"]    {{ background-color: #CFF4FC; border-color: #9EEAF9; color: #055160; }}
    div[data-testid="stAlert"][data-baseweb="alert-info"] svg{{ fill: {COLOR_ACCENT_PRIMARY}; }}
    div[data-testid="stAlert"][data-baseweb="alert-warning"] {{ background-color: #FFF3CD; border-color: #FFECB5; color: #664D03; }}
    div[data-testid="stAlert"][data-baseweb="alert-warning"] svg{{ fill: #FFC107; }}
    div[data-testid="stAlert"][data-baseweb="alert-error"]   {{ background-color: #F8D7DA; border-color: #F1AEB5; color: #58151C; }}
    div[data-testid="stAlert"][data-baseweb="alert-error"] svg  {{ fill: {COLOR_ACCENT_NEGATIVE}; }}

    /* --- Dataframe Styling Wrappers --- */
    .stDataFrame {{ /* For st.dataframe */
        border: 1px solid {COLOR_BORDER_PRIMARY};
        border-radius: 8px;
        overflow: hidden;
        background-color: {COLOR_BACKGROUND_CONTENT};
        box-shadow: 0 5px 15px {COLOR_SHADOW_LIGHT};
    }}
    div.stMarkdown > div[data-testid="element-container"] > div > table {{
        margin-bottom: 25px;
        background-color: {COLOR_BACKGROUND_CONTENT};
        box-shadow: 0 5px 15px {COLOR_SHADOW_LIGHT};
        border-radius: 8px;
        border: 1px solid {COLOR_BORDER_PRIMARY}; /* Add border to HTML table */
    }}

    /* Hide Streamlit footer */
    .stApp > footer {{ visibility: hidden; }}
    /* Custom horizontal rule */
    hr {{ border-top: 1px solid {COLOR_BORDER_PRIMARY}; margin: 30px 0; }}

    /* Wrapper for main content sections */
    .content-section-wrapper {{
        background-color: {COLOR_BACKGROUND_PAGE};
        padding: 0px 30px 30px 30px;
    }}
    /* Styling for Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {COLOR_BACKGROUND_PAGE}; /* Match page background */
        padding-bottom: 0px; /* Remove default padding */
        border-bottom: 2px solid {COLOR_BORDER_PRIMARY}; /* Underline entire tab bar */
        gap: 10px; /* Space between tab buttons */
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent; /* Tabs inherit background */
        color: {COLOR_TEXT_SECONDARY};
        padding: 12px 18px;
        font-weight: 500;
        font-size: 1.0em;
        border-radius: 0; /* No individual radius */
        border-bottom: 2px solid transparent; /* Placeholder for active state */
        transition: color 0.2s ease, border-color 0.2s ease;
        margin-bottom: -2px; /* Overlap with the main border */
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        color: {COLOR_ACCENT_PRIMARY};
        background-color: {COLOR_ACCENT_PRIMARY_LIGHT};
    }}
    .stTabs [data-baseweb="tab--selected"] {{
        color: {COLOR_ACCENT_PRIMARY};
        font-weight: 600;
        border-bottom: 2px solid {COLOR_ACCENT_PRIMARY};
        background-color: transparent;
    }}
    .stTabs [data-testid="stMarkdownContainer"] {{ /* Content within each tab */
        padding-top: 25px;
    }}
    /* Styling for content within cards/containers */
    .card-content-padding {{
        padding: 20px;
        background-color: {COLOR_BACKGROUND_CONTENT};
        border-radius: 8px;
        border: 1px solid {COLOR_BORDER_PRIMARY};
        box-shadow: 0 5px 15px {COLOR_SHADOW_LIGHT};
        margin-bottom: 20px; /* Space between cards/sections */
    }}
</style>
""", unsafe_allow_html=True)

# --- Main Title Section ---
st.markdown("""
<div class='main-title-container'>
    <div class='main-title'>💎 Elegant Cashflow Dashboard</div>
    <div class='main-subtitle'>A refined view of your projected financial health.</div>
</div>
""", unsafe_allow_html=True)

# --- Helper Functions (Largely the same, styling adjusted) ---
def format_week_range(start_date):
    end_date = start_date + pd.Timedelta(days=6)
    return f"{start_date.day} {start_date.strftime('%b')} - {end_date.day} {end_date.strftime('%b')}"

def style_table(df_to_style):
    numeric_cols = df_to_style.select_dtypes(include=np.number).columns.tolist()
    styled_df = df_to_style.style.format(
        lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) and x != 0 else ("-" if isinstance(x, (int, float)) and x == 0 else x),
        na_rep="-"
    ).set_caption(f"<span style='font-size: 1.2em; font-weight:500; color: {COLOR_TEXT_PRIMARY}; display:block; margin-bottom:15px; text-align:left; padding-left:5px;'>Detailed Weekly Breakdown</span>") \
    .set_properties(**{
        'font-size': '9.5pt', 'border': f'1px solid {COLOR_BORDER_PRIMARY}',
        'font-family': "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
        'color': COLOR_TEXT_PRIMARY, 'width': '100%',
        'border-radius': '8px', 'overflow': 'hidden' # No separate box shadow, table itself has border
    }) \
    .set_table_styles([
        {'selector': '', 'props': [('border-collapse', 'collapse')]},
        {'selector': 'caption', 'props': [('caption-side', 'top'), ('padding-top', '10px')]},
        {'selector': 'th', 'props': [
            ('text-align', 'left'), ('padding', '12px 15px'), ('font-weight', '600'),
            ('font-size', '10pt'), ('color', COLOR_TEXT_PRIMARY), ('background-color', '#F9FAFB'), # Lighter header
            ('border-bottom', f'2px solid {COLOR_BORDER_SECONDARY}')]},
        {'selector': 'th.col_heading', 'props': [('text-align', 'center')]}, # Center data column headers
        {'selector': 'td', 'props': [
            ('text-align', 'center'), ('padding', '10px 15px'),
            ('border', f'1px solid {COLOR_BORDER_PRIMARY}')]},
        {'selector': 'th.row_heading.level0', 'props': [('font-weight', '500'), ('color', COLOR_ACCENT_PRIMARY)]},
        {'selector': 'th.row_heading.level1', 'props': [('color', COLOR_TEXT_SECONDARY)]},
        {'selector': 'tr:nth-child(even) td, tr:nth-child(even) th.row_heading', 'props': [('background-color', '#FCFDFD')]}, # Subtle even row
        {'selector': 'tr:hover td, tr:hover th.row_heading', 'props': [('background-color', COLOR_ACCENT_PRIMARY_LIGHT)]}, # Row hover
    ])
    def color_faint_on_zero(val): return f'color: {COLOR_TEXT_PLACEHOLDER};' if (isinstance(val, (int,float)) and val == 0) or pd.isna(val) else f'color: {COLOR_TEXT_PRIMARY};'
    data_cols_to_style = [col for col in df_to_style.columns if df_to_style[col].dtype in [np.int64, np.float64, 'int64', 'float64']]
    if data_cols_to_style: styled_df = styled_df.applymap(color_faint_on_zero, subset=pd.IndexSlice[:, data_cols_to_style])

    if numeric_cols:
        valid_numeric_cols_for_subset = [col for col in numeric_cols if col in df_to_style.columns]
        if valid_numeric_cols_for_subset:
            try:
                def highlight_positive_negative(s):
                    styles = [''] * len(s)
                    for i, val_orig in s.items():
                        idx_loc = s.index.get_loc(i); val = pd.to_numeric(val_orig, errors='coerce')
                        if pd.isna(val) or val == 0: continue
                        if val > 0: styles[idx_loc] = f'color: {COLOR_ACCENT_POSITIVE}; font-weight: 500;'
                        elif val < 0: styles[idx_loc] = f'color: {COLOR_ACCENT_NEGATIVE}; font-weight: 500;'
                    return styles
                styled_df = styled_df.apply(highlight_positive_negative, subset=valid_numeric_cols_for_subset, axis=0)
            except Exception as e: st.warning(f"Could not apply table cell highlights: {e}.")
    def style_net_cashflow_row_light(row):
        if row.name == ("Net Cashflow", ""): return [f'font-weight: 600; background-color: {COLOR_ACCENT_PRIMARY_LIGHT}; color: {COLOR_ACCENT_PRIMARY}; font-size:10.5pt; border-top: 2px solid {COLOR_ACCENT_PRIMARY};'] * len(row)
        return [''] * len(row)
    styled_df = styled_df.apply(style_net_cashflow_row_light, axis=1)
    return styled_df

# --- Sidebar for Inputs ---
with st.sidebar:
    st.markdown("<h1>Setup & Actions</h1>", unsafe_allow_html=True)
    with st.expander("📥 Download Sample Template", expanded=True): # Expanded by default
        sample_data = pd.DataFrame({"Party Type": ["Supplier", "Customer", "Supplier", "Internal"],"Party Name": ["ABC Ltd", "XYZ Inc", "DEF Supplies", "Loan Repay"],"Due Date": ["2024-07-15", "2024-07-10", "2024-07-20", "2024-07-25"],"Expected Date": ["2024-07-20", "2024-07-14", "2024-07-22", "2024-07-25"],"Amount": [-10000, 12000, -5000, -2500]})
        sample_data["Due Date"] = pd.to_datetime(sample_data["Due Date"]).dt.strftime('%Y-%m-%d')
        sample_data["Expected Date"] = pd.to_datetime(sample_data["Expected Date"]).dt.strftime('%Y-%m-%d')
        st.download_button(label="Download Template CSV", data=sample_data.to_csv(index=False).encode('utf-8'), file_name="cashflow_template.csv", mime="text/csv", help="Use this template to structure your cashflow data.")

    uploaded_file = st.file_uploader( "📤 Upload Cashflow Data (CSV or Excel)", type=["csv", "xlsx"], help="Upload your cashflow file...")
    st.markdown("---")
    st.caption(f"<p style='color:{COLOR_TEXT_SECONDARY}; font-size:0.85em; text-align:center; padding-top:10px;'>Crafted with Precision</p>", unsafe_allow_html=True)

# --- Altair Chart Theming Options for Light Theme ---
chart_theme_options_light = {
    "background": "transparent", # Transparent BG to inherit card BG
    "font": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
    "title": {"color": COLOR_TEXT_PRIMARY, "fontSize": 15, "fontWeight": 500, "anchor": "start", "dy": -25, "dx":5},
    "axis": {
        "labelColor": COLOR_TEXT_SECONDARY, "titleColor": COLOR_TEXT_SECONDARY,
        "gridColor": COLOR_BORDER_PRIMARY, "domainColor": COLOR_BORDER_SECONDARY,
        "tickColor": COLOR_BORDER_SECONDARY, "labelFontSize": 11, "titleFontSize": 12,
        "titleFontWeight": 500, "labelFontWeight": 400, "labelPadding": 6, "titlePadding": 12, "domain": False, "ticks":False
    },
    "legend": {"labelColor": COLOR_TEXT_SECONDARY, "titleColor": COLOR_TEXT_SECONDARY, "padding": 10, "symbolType": "square", "orient": "top-right", "offset": 10},
    "view": {"stroke": None},
    "bar": {"discreteBandSize": {"band": 0.7}},
    "text": {"color": COLOR_TEXT_PRIMARY, "fontSize": 9, "fontWeight": 500}
}

# --- Main Panel for Results ---
st.markdown("<div class='content-section-wrapper'>", unsafe_allow_html=True)

if uploaded_file:
    with st.spinner("✨ Preparing your elegant forecast..."):
        try:
            # --- Data Loading and Processing ---
            if uploaded_file.name.endswith(".csv"): df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".xlsx"): df = pd.read_excel(uploaded_file, sheet_name=0, engine='openpyxl')
            else: st.error("Unsupported file type."); st.stop()
            st.success(f"File `{uploaded_file.name}` processed successfully!")
            df.columns = df.columns.str.replace('\ufeff', '', regex=False).str.strip().str.lower()
            required_cols = {"party type", "party name", "due date", "expected date", "amount"}
            missing_cols = required_cols - set(df.columns)
            if missing_cols: st.error(f"Missing required columns: {', '.join(missing_cols)}."); st.stop()
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            if df['amount'].isnull().any(): st.warning("Some 'Amount' values were non-numeric and have been set to zero.") ; df['amount'] = df['amount'].fillna(0)
            for col in ["due date", "expected date"]:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                if df[col].isnull().any(): st.warning(f"Some '{col.title()}' values were not valid dates and ignored for those rows.")
            initial_row_count = len(df); df.dropna(subset=['due date', 'expected date', 'party type', 'party name'], inplace=True) # Amount NaNs handled
            if len(df) < initial_row_count: st.info(f"{initial_row_count - len(df)} rows removed due to missing critical date/party values.")
            if df.empty: st.error("No valid data remaining after processing."); st.stop()
            df["allocation date"] = df[["due date", "expected date"]].max(axis=1)
            df["week_start"] = df["allocation date"].dt.to_period("W").apply(lambda r: r.start_time)
            df["week_range"] = df["week_start"].apply(format_week_range)
            unique_week_starts = sorted(df["week_start"].unique())
            all_week_ranges_sorted = [format_week_range(ws) for ws in unique_week_starts]
            
            # --- OVERVIEW SECTION ---
            st.subheader("Dashboard Overview")
            overview_cols = st.columns([2,3]) # Give more space to the chart
            with overview_cols[0]:
                st.markdown("<div class='card-content-padding'>", unsafe_allow_html=True) # Wrap metrics in a card
                st.markdown(f"<h3 style='color:{COLOR_TEXT_PRIMARY}; font-size:1.2em; margin-bottom:15px;'>Key Financials</h3>", unsafe_allow_html=True)
                total_inflow = df[df['amount'] > 0]['amount'].sum()
                total_outflow_val = df[df['amount'] < 0]['amount'].sum()
                net_overall_cashflow = df['amount'].sum()
                st.metric(label="Total Projected Inflow", value=f"{total_inflow:,.0f}")
                st.metric(label="Total Projected Outflow", value=f"{total_outflow_val:,.0f}")
                delta_for_net, delta_color_for_net = None, "off"
                if abs(total_outflow_val) > 0: net_perc_of_outflow = (net_overall_cashflow / abs(total_outflow_val)) * 100 if abs(total_outflow_val) != 0 else 0; delta_for_net = f"{net_perc_of_outflow:.1f}% vs Outflow"; delta_color_for_net = "normal" if net_overall_cashflow >= 0 else "inverse"
                elif net_overall_cashflow > 0: delta_for_net, delta_color_for_net = "Pure Inflow", "normal"
                st.metric(label="Overall Net Cashflow", value=f"{net_overall_cashflow:,.0f}", delta=delta_for_net, delta_color=delta_color_for_net)
                st.markdown("</div>", unsafe_allow_html=True)

            # --- Pivot Table Data Preparation ---
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
            
            with overview_cols[1]:
                st.markdown("<div class='card-content-padding'>", unsafe_allow_html=True)
                if not net_cashflow_series.empty:
                    net_df = net_cashflow_series.reset_index(); net_df.columns = ["Week Range", "Net Cashflow"]
                    if not net_df.empty and not net_df["Net Cashflow"].isnull().all():
                        net_df["Week Range"] = pd.Categorical(net_df["Week Range"], categories=all_week_ranges_sorted, ordered=True); net_df = net_df.sort_values("Week Range")
                        bars = alt.Chart(net_df).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3, size=18).encode(
                            x=alt.X("Week Range:N", sort=None, title=None, axis=alt.Axis(labelAngle=-45, format='%d %b')),
                            y=alt.Y("Net Cashflow:Q", title="Net Cashflow ($)", axis=alt.Axis(format="~s")),
                            color=alt.condition(alt.datum["Net Cashflow"] >= 0, alt.value(COLOR_ACCENT_POSITIVE), alt.value(COLOR_ACCENT_NEGATIVE)),
                            tooltip=[alt.Tooltip("Week Range:N", title="Week"), alt.Tooltip("Net Cashflow:Q", title="Amount", format=",.0f")]
                        )
                        text_labels = bars.mark_text(align="center", baseline="middle", dy=alt.expr("datum['Net Cashflow'] >= 0 ? -8 : 8")).encode(
                            text=alt.Text("Net Cashflow:Q", format=",.0f"))
                        chart = (bars + text_labels).properties(title="Weekly Net Cashflow Trend", height=320).configure(**chart_theme_options_light)
                        st.altair_chart(chart, use_container_width=True)
                else:
                    st.info("No weekly net cashflow data to display in overview.")
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("---") # Divider after overview

            # --- TABS FOR DEEPER DIVES ---
            tab_details, tab_analysis, tab_data_export = st.tabs(["📊 Detailed Forecast", "📈 Analytical Charts", "📄 Data & Export"])

            with tab_details:
                if not final_table.empty and "No Data" not in final_table.columns:
                    st.markdown(style_table(final_table).to_html(), unsafe_allow_html=True)
                else:
                    st.info("No forecast table to display. Data might be empty after processing.")
            
            with tab_analysis:
                st.subheader("Breakdown by Party Type")
                if not df.empty:
                    summary_by_type = df.groupby("party type")["amount"].sum().reset_index(); summary_by_type.columns = ["Party Type", "Total Amount"]
                    # Data for chart
                    chart_summary_data = []
                    customers_total = summary_by_type[summary_by_type["Party Type"].str.lower().str.contains("customer", case=False)]["Total Amount"].sum()
                    suppliers_total = summary_by_type[summary_by_type["Party Type"].str.lower().str.contains("supplier", case=False)]["Total Amount"].sum()
                    other_types_summary = summary_by_type[~summary_by_type["Party Type"].str.lower().str.contains("customer|supplier", case=False, regex=True)]
                    if customers_total != 0: chart_summary_data.append({"Party Type": "Customers", "Amount": customers_total})
                    if suppliers_total != 0: chart_summary_data.append({"Party Type": "Suppliers", "Amount": suppliers_total})
                    for _, row in other_types_summary.iterrows(): chart_summary_data.append({"Party Type": row["Party Type"], "Amount": row["Total Amount"]})
                    
                    if chart_summary_data:
                        summary_chart_df = pd.DataFrame(chart_summary_data)
                        if not summary_chart_df.empty and not summary_chart_df["Amount"].isnull().all():
                             st.markdown("<div class='card-content-padding'>", unsafe_allow_html=True)
                             summary_bars = alt.Chart(summary_chart_df).mark_bar(size=25).encode(
                                x=alt.X('Amount:Q', title='Total Amount ($)', axis=alt.Axis(format="~s")),
                                y=alt.Y('Party Type:N', sort='-x', title=None),
                                color=alt.condition(alt.datum.Amount >= 0, alt.value(COLOR_ACCENT_POSITIVE), alt.value(COLOR_ACCENT_NEGATIVE)),
                                tooltip=['Party Type', alt.Tooltip('Amount:Q', format=',.0f')]
                            ).properties(title="Total by Party Type", height=alt.Step(38) 
                            ).configure(**chart_theme_options_light)
                             st.altair_chart(summary_bars, use_container_width=True)
                             st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.info("No data for party type summary chart.")
                else:
                    st.info("Upload data to see party type analysis.")
                # Add placeholders for future analytical charts here

            with tab_data_export:
                st.subheader("Uploaded Data Preview")
                st.dataframe(df[['party type', 'party name', 'due date', 'expected date', 'amount', 'allocation date', 'week_range']].head(20), use_container_width=True, hide_index=True)
                
                st.markdown("---")
                st.subheader("Export Forecast")
                # ... (Export logic remains the same)
                towrite = BytesIO()
                export_table = final_table.copy()
                if isinstance(export_table.index, pd.MultiIndex): export_table = export_table.reset_index()
                with pd.ExcelWriter(towrite, engine="xlsxwriter") as writer:
                    export_table.to_excel(writer, sheet_name="Cashflow Forecast", index=False)
                    workbook  = writer.book; worksheet = writer.sheets["Cashflow Forecast"]
                    header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': COLOR_TEXT_SECONDARY, 'font_color': COLOR_BACKGROUND_CONTENT, 'border': 1, 'border_color': COLOR_BORDER_SECONDARY})
                    for col_num, value in enumerate(export_table.columns.values): worksheet.write(0, col_num, value, header_format)
                    worksheet.set_column(0, 0, 20); worksheet.set_column(1, 1, 25)
                    if len(export_table.columns) > 2: worksheet.set_column(2, len(export_table.columns) -1 , 18)
                    money_format = workbook.add_format({'num_format': '#,##0', 'font_color': COLOR_TEXT_PRIMARY, 'bg_color': COLOR_BACKGROUND_CONTENT, 'border':1, 'border_color': COLOR_BORDER_PRIMARY})
                    text_format = workbook.add_format({'font_color': COLOR_TEXT_PRIMARY, 'bg_color': COLOR_BACKGROUND_CONTENT, 'border':1, 'border_color': COLOR_BORDER_PRIMARY})
                    net_cashflow_row_format_num = workbook.add_format({'num_format': '#,##0', 'bold': True, 'font_color': COLOR_ACCENT_PRIMARY, 'bg_color': COLOR_ACCENT_PRIMARY_LIGHT, 'border':1, 'border_color': COLOR_BORDER_PRIMARY, 'top_color': COLOR_BORDER_SECONDARY, 'top':2})
                    net_cashflow_row_format_text = workbook.add_format({'bold': True, 'font_color': COLOR_ACCENT_PRIMARY, 'bg_color': COLOR_ACCENT_PRIMARY_LIGHT, 'border':1, 'border_color': COLOR_BORDER_PRIMARY, 'top_color': COLOR_BORDER_SECONDARY, 'top':2})
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
                st.download_button(label="Download Forecast as Excel", data=towrite.getvalue(), file_name="cashflow_forecast_elegant.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        except pd.errors.ParserError: st.error("❌ Error parsing the uploaded file. Please ensure it's a valid CSV or Excel file.")
        except ImportError as ie:
            if "matplotlib" in str(ie).lower(): st.error("❌ Matplotlib is missing for some styling features.")
            elif "openpyxl" in str(ie).lower(): st.error("❌ openpyxl is missing for reading Excel .xlsx files.")
            else: st.error(f"An import error occurred: {ie}.")
            st.exception(ie)
        except Exception as e: st.error(f"An unexpected error occurred during processing: {e}"); st.exception(e)
else:
    # --- Initial Landing Page Content ---
    st.markdown("<div class='card-content-padding' style='text-align:center; margin-top: 30px;'>", unsafe_allow_html=True)
    st.info("👋 Welcome! Please upload your cashflow file using the sidebar to get started.")
    st.markdown("---") 
    with st.expander("💡 Quick Guide to Using This Dashboard", expanded=True): 
        st.markdown(f"""
            <p style='color:{COLOR_TEXT_PRIMARY}; font-size: 1.05em;'>This dashboard helps you visualize your projected financial health with clarity.</p>
            <h4 style='color:{COLOR_ACCENT_PRIMARY}; margin-top:20px; margin-bottom:8px;'>Getting Started:</h4>
            <ul style='color:{COLOR_TEXT_SECONDARY}; list-style-position: inside; padding-left: 0;'>
                <li style='margin-bottom:8px;'>1️⃣ <strong style='color:{COLOR_TEXT_PRIMARY};'>Prepare Your Data:</strong> Use a CSV or Excel file with columns: `Party Type`, `Party Name`, `Due Date`, `Expected Date`, `Amount`. A sample template is available in the sidebar.</li>
                <li style='margin-bottom:8px;'>2️⃣ <strong style='color:{COLOR_TEXT_PRIMARY};'>Upload Your File:</strong> Use the "Upload Cashflow Data" option in the sidebar.</li>
                <li style='margin-bottom:8px;'>3️⃣ <strong style='color:{COLOR_TEXT_PRIMARY};'>Explore & Analyze:</strong>
                    <ul>
                        <li>View an instant **Dashboard Overview** with key financials and trends.</li>
                        <li>Dive into the **Detailed Forecast** tab for the full weekly breakdown.</li>
                        <li>Check **Analytical Charts** for visual summaries like totals by party type.</li>
                        <li>Review your input in the **Data & Export** tab.</li>
                    </ul>
                </li>
                <li style='margin-bottom:8px;'>4️⃣ <strong style='color:{COLOR_TEXT_PRIMARY};'>Download:</strong> Export the detailed forecast to Excel from the "Data & Export" tab.</li>
            </ul>
            <p style='color:{COLOR_TEXT_SECONDARY}; font-size:0.95em; margin-top:20px;'>✨ **Tip:** For best results, use YYYY-MM-DD for dates and ensure the 'Amount' column is purely numeric.</p>
            """, unsafe_allow_html=True)
    st.balloons()
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True) # Close content-section-wrapper
