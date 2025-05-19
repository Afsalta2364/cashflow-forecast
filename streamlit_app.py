import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO
import numpy as np

# --- Page Setup ---
st.set_page_config(
    page_title="Cashflow Forecast Dashboard",
    page_icon="✨", # New icon
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Fresh & Elegant Light Theme Colors ---
COLOR_BACKGROUND_PAGE = "#F0F2F5"        # Light grayish-blue, soft overall background
COLOR_BACKGROUND_CONTENT = "#FFFFFF"     # White for main content areas, cards
COLOR_TEXT_PRIMARY = "#1F2937"           # Dark Gray (almost black) for main text
COLOR_TEXT_SECONDARY = "#6B7280"         # Medium Gray for secondary text, subtitles
COLOR_TEXT_PLACEHOLDER = "#9CA3AF"       # Lighter Gray for placeholders
COLOR_ACCENT_PRIMARY = "#3B82F6"         # Vibrant Blue for primary actions, highlights
COLOR_ACCENT_POSITIVE = "#10B981"        # Green for positive indicators
COLOR_ACCENT_NEGATIVE = "#EF4444"        # Red for negative indicators
COLOR_BORDER_LIGHT = "#E5E7EB"           # Light Gray for subtle borders
COLOR_BORDER_MEDIUM = "#D1D5DB"          # Slightly darker gray for more distinct borders
COLOR_SHADOW = "rgba(0, 0, 0, 0.05)"     # Very subtle shadow for depth

# --- Custom CSS for Fresh & Elegant Light Theme ---
st.markdown(f"""
<style>
    /* --- Global Styles --- */
    body, .stApp {{
        font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
        color: {COLOR_TEXT_PRIMARY};
        background-color: {COLOR_BACKGROUND_PAGE} !important;
    }}

    /* --- Main Title Header --- */
    .main-title-container {{
        padding: 20px 30px;
        background: {COLOR_BACKGROUND_CONTENT};
        border-bottom: 1px solid {COLOR_BORDER_LIGHT};
        margin-bottom: 25px; /* Space before first content block */
    }}
    .main-title {{
        font-size: 2em;
        color: {COLOR_TEXT_PRIMARY};
        font-weight: 600;
    }}
    .main-subtitle {{
        font-size: 1em;
        color: {COLOR_TEXT_SECONDARY};
        margin-top: 4px;
    }}

    /* --- Subheader Styling (st.subheader) --- */
    h2 {{ /* Targets st.subheader */
        color: {COLOR_TEXT_PRIMARY};
        border-bottom: 1px solid {COLOR_BORDER_LIGHT};
        padding-bottom: 10px;
        margin-top: 30px;
        margin-bottom: 20px;
        font-weight: 500;
        font-size: 1.35em;
    }}

    /* --- Sidebar --- */
    section[data-testid="stSidebar"] {{
        background-color: {COLOR_BACKGROUND_CONTENT};
        border-right: 1px solid {COLOR_BORDER_LIGHT};
        padding-top: 15px;
    }}
    section[data-testid="stSidebar"] h1 {{ /* Sidebar Title */
        color: {COLOR_ACCENT_PRIMARY} !important;
        font-weight: 600 !important; /* Bolder title */
        text-align: center !important;
        border-bottom: 2px solid {COLOR_ACCENT_PRIMARY} !important; /* Thicker accent border */
        padding-bottom: 12px !important;
        font-size: 1.25em !important;
        margin: 10px 15px 20px 15px !important; /* Added horizontal margin */
    }}
    .streamlit-expanderHeader {{
        font-size: 0.95em !important;
        font-weight: 500 !important; /* Slightly bolder expander header */
        color: {COLOR_TEXT_SECONDARY} !important;
        padding: 10px 15px !important; /* More padding */
        border-bottom: 1px solid {COLOR_BORDER_LIGHT};
    }}
    .streamlit-expanderHeader:hover {{
        color: {COLOR_ACCENT_PRIMARY} !important;
        background-color: {COLOR_BACKGROUND_PAGE}; /* Match page bg for subtle hover */
    }}
    section[data-testid="stSidebar"] .stFileUploader label {{
        color: {COLOR_TEXT_SECONDARY} !important;
        font-size: 0.9em !important;
        font-weight: 500;
    }}
    section[data-testid="stSidebar"] .stButton>button {{ /* Sidebar buttons */
        background-color: {COLOR_ACCENT_PRIMARY};
        color: {COLOR_BACKGROUND_CONTENT} !important; /* White text */
        border: none;
        border-radius: 6px;
        padding: 9px 18px;
        font-size: 0.9em;
        font-weight: 500;
        width: 100%; /* Make button full width of its container */
        margin-top: 5px;
    }}
    section[data-testid="stSidebar"] .stButton>button:hover {{
        background-color: #2563EB; /* Darker blue on hover */
    }}

    /* --- Metric Cards --- */
    div[data-testid="stMetric"] {{
        background-color: {COLOR_BACKGROUND_CONTENT};
        border: 1px solid {COLOR_BORDER_LIGHT};
        border-radius: 8px;
        padding: 20px; /* More padding */
        height: 100%;
        box-shadow: 0 4px 12px {COLOR_SHADOW}; /* Softer, slightly larger shadow */
    }}
    .stMetric > div > div:nth-child(1) {{ /* Metric Label */
        color: {COLOR_TEXT_SECONDARY};
        font-size: 0.85em;
        font-weight: 500;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .stMetric > div > div:nth-child(2) {{ /* Metric Value */
        color: {COLOR_TEXT_PRIMARY};
        font-size: 2.1em; /* Larger value */
        font-weight: 600;
    }}
    .stMetric > div > div:nth-child(3) {{ /* Metric Delta */
        font-size: 0.9em;
        font-weight: 500;
    }}
    .stMetric [data-testid="stMetricDelta"] svg {{ visibility: visible !important; }}
    .stMetric [data-testid="stMetricDelta"] div[data-delta-direction="positive"] {{ color: {COLOR_ACCENT_POSITIVE} !important; }}
    .stMetric [data-testid="stMetricDelta"] div[data-delta-direction="negative"] {{ color: {COLOR_ACCENT_NEGATIVE} !important; }}


    /* --- Main Download Button --- */
    .stDownloadButton>button {{
        background-color: {COLOR_ACCENT_PRIMARY};
        color: {COLOR_BACKGROUND_CONTENT} !important; /* White text */
        border: none;
        border-radius: 6px;
        font-weight: 500;
        padding: 10px 22px;
        font-size: 0.95em;
    }}
    .stDownloadButton>button:hover {{ background-color: #2563EB; }}

    /* --- Alert Messages --- */
    div[data-testid="stAlert"] {{ border-radius: 6px; border-width: 1px; border-style: solid; padding: 12px 15px; font-size: 0.9em;}}
    div[data-testid="stAlert"][data-baseweb="alert-success"] {{ background-color: rgba(16, 185, 129, 0.1); border-color: {COLOR_ACCENT_POSITIVE}; color: #047857; }} /* Darker green text */
    div[data-testid="stAlert"][data-baseweb="alert-success"] svg {{ fill: {COLOR_ACCENT_POSITIVE}; }}
    div[data-testid="stAlert"][data-baseweb="alert-info"]    {{ background-color: rgba(59, 130, 246, 0.1); border-color: {COLOR_ACCENT_PRIMARY}; color: #1D4ED8; }} /* Darker blue text */
    div[data-testid="stAlert"][data-baseweb="alert-info"] svg{{ fill: {COLOR_ACCENT_PRIMARY}; }}
    div[data-testid="stAlert"][data-baseweb="alert-warning"] {{ background-color: rgba(245, 158, 11, 0.1); border-color: #F59E0B; color: #B45309; }} /* Darker orange text */
    div[data-testid="stAlert"][data-baseweb="alert-warning"] svg{{ fill: #F59E0B; }}
    div[data-testid="stAlert"][data-baseweb="alert-error"]   {{ background-color: rgba(239, 68, 68, 0.1); border-color: {COLOR_ACCENT_NEGATIVE}; color: #B91C1C; }} /* Darker red text */
    div[data-testid="stAlert"][data-baseweb="alert-error"] svg  {{ fill: {COLOR_ACCENT_NEGATIVE}; }}

    /* --- Dataframe Styling Wrappers --- */
    .stDataFrame {{ /* For st.dataframe */
        border: 1px solid {COLOR_BORDER_MEDIUM};
        border-radius: 8px;
        overflow: hidden;
        background-color: {COLOR_BACKGROUND_CONTENT};
        box-shadow: 0 4px 12px {COLOR_SHADOW};
    }}
    /* Center HTML tables rendered via st.markdown */
    div.stMarkdown > div[data-testid="element-container"] > div {{
        display: flex; justify-content: center; width: 100%;
    }}
    div.stMarkdown > div[data-testid="element-container"] > div > table {{
        margin-bottom: 25px; /* More space after table */
        background-color: {COLOR_BACKGROUND_CONTENT};
        box-shadow: 0 4px 12px {COLOR_SHADOW};
        border-radius: 8px; /* Rounded corners for the table wrapper */
    }}

    /* Hide Streamlit footer */
    .stApp > footer {{ visibility: hidden; }}
    /* Custom horizontal rule */
    hr {{
        border-top: 1px solid {COLOR_BORDER_LIGHT};
        margin-top: 30px;
        margin-bottom: 30px;
    }}

    /* Wrapper for main content sections to apply consistent background and padding */
    .content-section-wrapper {{
        background-color: {COLOR_BACKGROUND_PAGE}; /* Page bg for area between cards */
        padding: 0px 25px 25px 25px; /* Padding around chart rows/content */
    }}
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {COLOR_BACKGROUND_PAGE}; /* Ensure tabs bar matches page bg */
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: {COLOR_BACKGROUND_CONTENT};
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        margin-right: 4px;
        color: {COLOR_TEXT_SECONDARY};
    }}
    .stTabs [data-baseweb="tab--selected"] {{
        background-color: {COLOR_BACKGROUND_CONTENT};
        color: {COLOR_ACCENT_PRIMARY};
        font-weight: 500;
    }}

</style>
""", unsafe_allow_html=True)

# --- Main Title Section ---
st.markdown("""
<div class='main-title-container'>
    <div class='main-title'>✨ Cashflow Forecast Dashboard</div>
    <div class='main-subtitle'>Visualize your projected financial health with a fresh perspective.</div>
</div>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def format_week_range(start_date):
    end_date = start_date + pd.Timedelta(days=6)
    return f"{start_date.day} {start_date.strftime('%b')} - {end_date.day} {end_date.strftime('%b')}"

def style_table(df_to_style):
    """Applies custom styling to a Pandas DataFrame for HTML display - Light Theme."""
    numeric_cols = df_to_style.select_dtypes(include=np.number).columns.tolist()
    text_color_primary = COLOR_TEXT_PRIMARY
    text_color_secondary = COLOR_TEXT_SECONDARY
    bg_base = COLOR_BACKGROUND_CONTENT
    bg_header = "#F9FAFB" # Very light gray for header
    bg_index_cols = "#F9FAFB"
    bg_net_cashflow_row = "#EFF6FF" # Light blue for net cashflow row emphasis
    border_color = COLOR_BORDER_LIGHT
    shadow_color = COLOR_SHADOW

    data_col_min_width = '115px' # Slightly wider
    index_col_party_type_width = '110px'
    index_col_party_name_width = '130px'

    styled_df = df_to_style.style.format(
        lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) and x != 0 else ("-" if isinstance(x, (int, float)) and x == 0 else x),
        na_rep="-"
    ) \
        .set_caption(f"<span style='font-size: 1.15em; font-weight:500; color: {text_color_primary}; display:block; margin-bottom:12px; text-align:center;'>📋 Weekly Cashflow Breakdown</span>") \
        .set_properties(**{
            'font-size': '9.5pt', 'border': f'1px solid {border_color}', # Add border to table itself
            'font-family': "'Inter', 'Segoe UI', sans-serif", 'color': text_color_primary,
            'width': 'auto', 'margin-left': 'auto', 'margin-right': 'auto',
            'border-radius': '8px', 'box-shadow': f'0 4px 12px {shadow_color}',
            'background-color': bg_base, 'overflow': 'hidden'
        }) \
        .set_table_styles([
            {'selector': '', 'props': [('border-collapse', 'collapse'), ('width', 'auto'), ('min-width', '70%'), ('max-width', '100%')]}, # collapse for cleaner lines
            {'selector': 'caption', 'props': [('caption-side', 'top'), ('padding-top', '12px')]},
            {'selector': 'th', 'props': [('text-align', 'center'), ('vertical-align', 'middle'), ('padding', '12px 10px'), ('font-weight', '500'), ('font-size', '9.5pt'), ('color', text_color_primary), ('background-color', bg_header), ('border-bottom', f'2px solid {COLOR_BORDER_MEDIUM}')]}, # Heavier bottom border for header
            {'selector': 'th.col_heading, th.index_name', 'props': [('border-right', f'1px solid {border_color}')]},
            {'selector': 'th.col_heading:last-child, th.index_name:last-child', 'props': [('border-right', 'none')]},
            {'selector': 'th.col_heading', 'props': [('min-width', data_col_min_width), ('max-width', data_col_min_width)]},
            {'selector': 'th.row_heading', 'props': [('background-color', bg_index_cols), ('border-right', f'1px solid {border_color}'), ('text-align', 'left'), ('padding-left', '10px')]}, # Align index left
            {'selector': 'th.row_heading.level0', 'props': [('font-weight', '500'), ('color', COLOR_ACCENT_PRIMARY), ('min-width', index_col_party_type_width), ('max-width', index_col_party_type_width)]},
            {'selector': 'th.row_heading.level1', 'props': [('min-width', index_col_party_name_width), ('max-width', index_col_party_name_width), ('color', text_color_secondary)]},
            {'selector': 'td', 'props': [('background-color', bg_base), ('text-align', 'center'), ('vertical-align', 'middle'), ('padding', '10px 10px'), ('border', f'1px solid {border_color}'), ('min-width', data_col_min_width), ('max-width', data_col_min_width)]},
            # {'selector': 'tr:nth-child(even) td', 'props': [('background-color', '#F9FAFB')]}, # Optional: alternating row color
        ])

    def color_faint_on_zero(val):
        return f'color: {COLOR_TEXT_PLACEHOLDER};' if (isinstance(val, (int,float)) and val == 0) or pd.isna(val) else f'color: {text_color_primary};'
    data_cols_to_style = [col for col in df_to_style.columns if df_to_style[col].dtype in [np.int64, np.float64, 'int64', 'float64']]
    if data_cols_to_style:
        styled_df = styled_df.applymap(color_faint_on_zero, subset=pd.IndexSlice[:, data_cols_to_style])

    if numeric_cols:
        valid_numeric_cols_for_subset = [col for col in numeric_cols if col in df_to_style.columns]
        if valid_numeric_cols_for_subset:
            try:
                def highlight_positive_negative(s): # Simpler highlight, just text color
                    styles = [''] * len(s)
                    for i, val_orig in s.items():
                        idx_loc = s.index.get_loc(i)
                        val = pd.to_numeric(val_orig, errors='coerce')
                        if pd.isna(val) or val == 0: continue
                        if val > 0: styles[idx_loc] = f'color: {COLOR_ACCENT_POSITIVE}; font-weight: 500;'
                        elif val < 0: styles[idx_loc] = f'color: {COLOR_ACCENT_NEGATIVE}; font-weight: 500;'
                    return styles
                styled_df = styled_df.apply(highlight_positive_negative, subset=valid_numeric_cols_for_subset, axis=0)
            except Exception as e: st.warning(f"Could not apply table cell highlights: {e}.")

    def style_net_cashflow_row_light(row):
        if row.name == ("Net Cashflow", ""):
            return [f'font-weight: 600; background-color: {bg_net_cashflow_row}; color: {COLOR_ACCENT_PRIMARY}; font-size:10pt; text-align:center; vertical-align:middle; border-top: 2px solid {COLOR_BORDER_MEDIUM};'] * len(row)
        return [''] * len(row)
    styled_df = styled_df.apply(style_net_cashflow_row_light, axis=1)
    return styled_df

# --- Sidebar for Inputs ---
with st.sidebar:
    st.markdown("<h1>Inputs & Settings</h1>", unsafe_allow_html=True)
    # Removed st.markdown("---") as expanders provide separation
    with st.expander("📥 Download Sample Template", expanded=False):
        # ... (sample data and download button code remains the same)
        sample_data = pd.DataFrame({"Party Type": ["Supplier", "Customer", "Supplier", "Internal"],"Party Name": ["ABC Ltd", "XYZ Inc", "DEF Supplies", "Loan Repay"],"Due Date": ["2024-07-15", "2024-07-10", "2024-07-20", "2024-07-25"],"Expected Date": ["2024-07-20", "2024-07-14", "2024-07-22", "2024-07-25"],"Amount": [-10000, 12000, -5000, -2500]})
        sample_data["Due Date"] = pd.to_datetime(sample_data["Due Date"]).dt.strftime('%Y-%m-%d')
        sample_data["Expected Date"] = pd.to_datetime(sample_data["Expected Date"]).dt.strftime('%Y-%m-%d')
        st.download_button(label="Download Template CSV", data=sample_data.to_csv(index=False).encode('utf-8'), file_name="cashflow_template.csv", mime="text/csv", help="Use this template to structure your cashflow data.")

    uploaded_file = st.file_uploader(
        "Upload Cashflow Data (CSV or Excel)",
        type=["csv", "xlsx"],
        help="Upload your CSV or Excel file with cashflow entries."
    )
    st.caption(f"<p style='color:{COLOR_TEXT_SECONDARY}; font-size:0.85em; text-align:center; padding-top:20px;'>Developed with Elegance</p>", unsafe_allow_html=True)


# --- Altair Chart Theming Options for Light Theme ---
chart_theme_options_light = {
    "background": COLOR_BACKGROUND_CONTENT, # Chart bg same as card
    "font": "'Inter', 'Segoe UI', Roboto, sans-serif",
    "title": {
        "color": COLOR_TEXT_PRIMARY, "fontSize": 14, "fontWeight": 500,
        "anchor": "middle", "dy": -15 # Adjust title position
    },
    "axis": {
        "labelColor": COLOR_TEXT_SECONDARY, "titleColor": COLOR_TEXT_SECONDARY,
        "gridColor": COLOR_BORDER_LIGHT, "domainColor": COLOR_BORDER_MEDIUM,
        "tickColor": COLOR_BORDER_MEDIUM, "labelFontSize": 10, "titleFontSize": 11,
        "titleFontWeight": 500, "labelFontWeight": 400,
        "labelPadding": 5, "titlePadding": 10
    },
    "legend": {
        "labelColor": COLOR_TEXT_SECONDARY, "titleColor": COLOR_TEXT_SECONDARY,
        "labelFontSize": 10, "titleFontSize": 11, "padding": 10,
        "symbolType": "square", "orient": "top-right", "offset": 0
    },
    "view": {"stroke": None},
    "bar": {"discreteBandSize": {"band": 0.75}}, # Adjust bar width
    "text": {"color": COLOR_TEXT_PRIMARY, "fontSize": 9, "fontWeight": 500} # For labels on bars
}

# --- Main Panel for Results ---
st.markdown("<div class='content-section-wrapper'>", unsafe_allow_html=True)

if uploaded_file:
    with st.spinner("✨ Processing your file with elegance..."):
        try:
            # --- Data Loading and Processing (Same as your previous version) ---
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
            
            tab1, tab2, tab3 = st.tabs(["🔑 Key Metrics", "📊 Forecast Details", "📋 Data Preview"])

            with tab1:
                st.subheader("🚀 At a Glance: Forecast Summary")
                total_inflow = df[df['amount'] > 0]['amount'].sum(); total_outflow_val = df[df['amount'] < 0]['amount'].sum(); net_overall_cashflow = df['amount'].sum()
                forecast_start_week_display, forecast_end_week_display, num_forecast_weeks = "N/A", "N/A", 0
                if all_week_ranges_sorted: forecast_start_week_display, forecast_end_week_display, num_forecast_weeks = all_week_ranges_sorted[0], all_week_ranges_sorted[-1], len(all_week_ranges_sorted)
                
                cols1_metrics = st.columns(3)
                cols1_metrics[0].metric(label="Total Inflow", value=f"{total_inflow:,.0f}")
                cols1_metrics[1].metric(label="Total Outflow", value=f"{total_outflow_val:,.0f}")
                delta_for_net, delta_color_for_net = None, "off"
                if abs(total_outflow_val) > 0: net_perc_of_outflow = (net_overall_cashflow / abs(total_outflow_val)) * 100 if abs(total_outflow_val) != 0 else 0; delta_for_net = f"{net_perc_of_outflow:.1f}% vs Outflow"; delta_color_for_net = "normal" if net_overall_cashflow >= 0 else "inverse"
                elif net_overall_cashflow > 0: delta_for_net, delta_color_for_net = "Pure Inflow", "normal"
                cols1_metrics[2].metric(label="Net Cashflow (Overall)", value=f"{net_overall_cashflow:,.0f}", delta=delta_for_net, delta_color=delta_color_for_net)
                
                st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True) # Visual separator for metrics
                
                cols2_metrics = st.columns(3)
                cols2_metrics[0].metric(label="Forecast Start Week", value=forecast_start_week_display)
                cols2_metrics[1].metric(label="Forecast End Week", value=forecast_end_week_display)
                cols2_metrics[2].metric(label="No. of Forecast Weeks", value=str(num_forecast_weeks))

                # --- Summarized Totals by Party Type in Metrics Tab ---
                st.subheader("Summary by Party Type")
                if not df.empty:
                    summary_by_type = df.groupby("party type")["amount"].sum().reset_index(); summary_by_type.columns = ["Party Type", "Total Amount"]
                    customers_total = summary_by_type[summary_by_type["Party Type"].str.lower().str.contains("customer", case=False)]["Total Amount"].sum()
                    suppliers_total = summary_by_type[summary_by_type["Party Type"].str.lower().str.contains("supplier", case=False)]["Total Amount"].sum()
                    other_types_summary = summary_by_type[~summary_by_type["Party Type"].str.lower().str.contains("customer|supplier", case=False, regex=True)]
                    
                    col_summary1, col_summary2 = st.columns(2)
                    with col_summary1: st.metric(label="TOTAL FROM CUSTOMERS", value=f"{customers_total:,.0f}")
                    with col_summary2: st.metric(label="TOTAL TO SUPPLIERS", value=f"{suppliers_total:,.0f}")
                    
                    if not other_types_summary.empty:
                        st.markdown(f"<h6 style='color:{COLOR_TEXT_PRIMARY}; margin-top:15px;'>Other Party Type Totals:</h6>", unsafe_allow_html=True)
                        for _, row in other_types_summary.iterrows():
                            st.markdown(f"<span style='color:{COLOR_TEXT_SECONDARY};'>- <strong>{row['Party Type']}</strong>: {row['Total Amount']:,.0f}</span>", unsafe_allow_html=True)


            # --- Pivot Table Data Preparation (Same as your previous version) ---
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

            with tab2:
                st.subheader("Detailed Weekly Cashflow Forecast")
                if not final_table.empty and "No Data" not in final_table.columns:
                    st.markdown(style_table(final_table).to_html(), unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True) # Spacer

                    # --- Weekly Net Cashflow Trend Chart ---
                    if not net_cashflow_series.empty:
                        net_df = net_cashflow_series.reset_index(); net_df.columns = ["Week Range", "Net Cashflow"]
                        if not net_df.empty and not net_df["Net Cashflow"].isnull().all():
                            net_df["Week Range"] = pd.Categorical(net_df["Week Range"], categories=all_week_ranges_sorted, ordered=True); net_df = net_df.sort_values("Week Range")
                            bars = alt.Chart(net_df).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3, size=20).encode(
                                x=alt.X("Week Range:N", sort=None, title=None, axis=alt.Axis(labelAngle=-45, format='%d %b')),
                                y=alt.Y("Net Cashflow:Q", title="Net Cashflow ($)", axis=alt.Axis(format="~s")),
                                color=alt.condition(alt.datum["Net Cashflow"] >= 0, alt.value(COLOR_ACCENT_POSITIVE), alt.value(COLOR_ACCENT_NEGATIVE)),
                                tooltip=[alt.Tooltip("Week Range:N", title="Week"), alt.Tooltip("Net Cashflow:Q", title="Amount", format=",.0f")]
                            )
                            text_labels = bars.mark_text(align="center", baseline="middle", dy=alt.expr("datum['Net Cashflow'] >= 0 ? -8 : 8")).encode(
                                text=alt.Text("Net Cashflow:Q", format=",.0f")) # Text color from theme options
                            chart = (bars + text_labels).properties(title="Weekly Net Cashflow Trend", height=300).configure(**chart_theme_options_light)
                            st.altair_chart(chart, use_container_width=True)
                    
                    # --- Party Type Summary Chart (moved from metrics for space) ---
                    if not df.empty: # Re-check df for this specific chart's data needs
                        st.subheader("Breakdown by Party Type") # Give it its own subheader
                        # ... (chart_summary_data preparation code remains the same)
                        chart_summary_data = []
                        if customers_total != 0: chart_summary_data.append({"Party Type": "Customers", "Amount": customers_total})
                        if suppliers_total != 0: chart_summary_data.append({"Party Type": "Suppliers", "Amount": suppliers_total})
                        for _, row in other_types_summary.iterrows(): chart_summary_data.append({"Party Type": row["Party Type"], "Amount": row["Total Amount"]})
                        
                        if chart_summary_data:
                            summary_chart_df = pd.DataFrame(chart_summary_data)
                            if not summary_chart_df.empty and not summary_chart_df["Amount"].isnull().all():
                                summary_bars = alt.Chart(summary_chart_df).mark_bar(size=28).encode(
                                    x=alt.X('Amount:Q', title='Total Amount ($)', axis=alt.Axis(format="~s")),
                                    y=alt.Y('Party Type:N', sort='-x', title=None),
                                    color=alt.condition(alt.datum.Amount >= 0, alt.value(COLOR_ACCENT_POSITIVE), alt.value(COLOR_ACCENT_NEGATIVE)),
                                    tooltip=['Party Type', alt.Tooltip('Amount:Q', format=',.0f')]
                                ).properties(title="Total by Party Type", height=alt.Step(40) 
                                ).configure(**chart_theme_options_light)
                                st.altair_chart(summary_bars, use_container_width=True)
                    
                    st.subheader("📤 Export Forecast")
                    # ... (Export logic remains the same, Excel styling uses theme colors from Python vars)
                    towrite = BytesIO()
                    export_table = final_table.copy()
                    if isinstance(export_table.index, pd.MultiIndex): export_table = export_table.reset_index()
                    with pd.ExcelWriter(towrite, engine="xlsxwriter") as writer:
                        export_table.to_excel(writer, sheet_name="Cashflow Forecast", index=False)
                        workbook  = writer.book; worksheet = writer.sheets["Cashflow Forecast"]
                        header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': COLOR_TEXT_SECONDARY, 'font_color': COLOR_BACKGROUND_CONTENT, 'border': 1, 'border_color': COLOR_BORDER_MEDIUM})
                        for col_num, value in enumerate(export_table.columns.values): worksheet.write(0, col_num, value, header_format)
                        worksheet.set_column(0, 0, 20); worksheet.set_column(1, 1, 25)
                        if len(export_table.columns) > 2: worksheet.set_column(2, len(export_table.columns) -1 , 18)
                        money_format = workbook.add_format({'num_format': '#,##0', 'font_color': COLOR_TEXT_PRIMARY, 'bg_color': COLOR_BACKGROUND_CONTENT, 'border':1, 'border_color': COLOR_BORDER_LIGHT})
                        text_format = workbook.add_format({'font_color': COLOR_TEXT_PRIMARY, 'bg_color': COLOR_BACKGROUND_CONTENT, 'border':1, 'border_color': COLOR_BORDER_LIGHT})
                        net_cashflow_row_format_num = workbook.add_format({'num_format': '#,##0', 'bold': True, 'font_color': COLOR_ACCENT_PRIMARY, 'bg_color': "#EFF6FF", 'border':1, 'border_color': COLOR_BORDER_LIGHT, 'top_color': COLOR_BORDER_MEDIUM, 'top':2})
                        net_cashflow_row_format_text = workbook.add_format({'bold': True, 'font_color': COLOR_ACCENT_PRIMARY, 'bg_color': "#EFF6FF", 'border':1, 'border_color': COLOR_BORDER_LIGHT, 'top_color': COLOR_BORDER_MEDIUM, 'top':2})
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
                else:
                    st.info("ℹ️ No forecast table to display. Data might be empty after processing.")
            
            with tab3:
                st.subheader("Uploaded Data Preview (First 20 Valid Rows)")
                st.dataframe(df[['party type', 'party name', 'due date', 'expected date', 'amount', 'allocation date', 'week_range']].head(20), use_container_width=True, hide_index=True)

        except pd.errors.ParserError: st.error("❌ Error parsing the uploaded file.")
        except ImportError as ie:
            if "matplotlib" in str(ie).lower(): st.error("❌ Matplotlib is missing.")
            elif "openpyxl" in str(ie).lower(): st.error("❌ openpyxl is missing for Excel files.")
            else: st.error(f"Import error: {ie}.")
            st.exception(ie)
        except Exception as e: st.error(f"An unexpected error occurred: {e}"); st.exception(e)
else:
    # --- Initial Landing Page Content ---
    st.info("👈 **Upload your cashflow file using the sidebar to get started!**")
    st.markdown("---") 
    with st.expander("💡 How to Use This Dashboard", expanded=True): 
        st.markdown(f"""
            <p style='color:{COLOR_TEXT_PRIMARY}; font-size: 1.05em;'>Welcome to your interactive Weekly Cashflow Forecast Dashboard!</p>
            <p style='color:{COLOR_TEXT_SECONDARY};'>This tool helps you visualize your projected financial health with a clean and elegant interface.</p>
            <h4 style='color:{COLOR_ACCENT_PRIMARY}; margin-top:20px; margin-bottom:8px;'>Steps to Get Started:</h4>
            <ul style='color:{COLOR_TEXT_SECONDARY}; list-style-type: "⭐ "; padding-left: 20px;'>
                <li style='margin-bottom:5px;'><strong>Prepare Your Data:</strong> Ensure your data is in a CSV or Excel (`.xlsx`) file.
                    The file must contain columns: `Party Type`, `Party Name`, `Due Date`, `Expected Date`, `Amount`.
                    (You can download a sample template from the sidebar).</li>
                <li style='margin-bottom:5px;'><strong>Upload Your File:</strong> Use the file uploader in the sidebar to select your prepared CSV or Excel file.</li>
                <li style='margin-bottom:5px;'><strong>View & Analyze Results:</strong> Navigate through the tabs to explore key metrics, the detailed forecast table, charts, and a preview of your uploaded data.</li>
                <li style='margin-bottom:5px;'><strong>Download Forecast:</strong> Export the detailed weekly forecast table to an Excel file for offline use or sharing.</li>
            </ul>
            <p style='color:{COLOR_TEXT_SECONDARY}; font-size:0.9em; margin-top:20px;'>✨ **Tips for Best Results:** Use consistent date formats (YYYY-MM-DD is recommended). Ensure the 'Amount' column contains only numeric values.</p>
            """, unsafe_allow_html=True)
    st.balloons()

st.markdown("</div>", unsafe_allow_html=True) # Close content-section-wrapper
