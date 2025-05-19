import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO
import numpy as np

# --- Page Setup ---
st.set_page_config(
    page_title="Minimalist Cashflow Dashboard",
    page_icon=" minimalist-icon.png", # Placeholder for a very simple icon if you have one
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Minimalist Theme Colors ---
MIN_COLOR_BACKGROUND = "#FFFFFF"         # Pure White
MIN_COLOR_TEXT_PRIMARY = "#212529"       # Very Dark Gray (High Contrast)
MIN_COLOR_TEXT_SECONDARY = "#6C757D"     # Medium Gray
MIN_COLOR_TEXT_FAINT = "#ADB5BD"         # Light Gray for placeholders, faint lines
MIN_COLOR_ACCENT = "#007BFF"             # A clean, modern Blue (can be changed)
MIN_COLOR_POSITIVE = "#28A745"           # Clean Green
MIN_COLOR_NEGATIVE = "#DC3545"           # Clean Red
MIN_COLOR_BORDER = "#E9ECEF"             # Very Light Gray Border

# --- Custom CSS for Minimalist Theme ---
st.markdown(f"""
<style>
    /* --- Global Styles --- */
    body, .stApp {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        color: {MIN_COLOR_TEXT_PRIMARY};
        background-color: {MIN_COLOR_BACKGROUND} !important;
        font-size: 15px; /* Slightly smaller base font for minimalism */
        line-height: 1.6;
    }}
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: {MIN_COLOR_BACKGROUND}; }}
    ::-webkit-scrollbar-thumb {{ background: {MIN_COLOR_TEXT_FAINT}; border-radius: 3px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: {MIN_COLOR_TEXT_SECONDARY}; }}

    /* --- Main Title Area --- */
    .main-header-minimal {{
        padding: 30px 30px 20px 30px;
        border-bottom: 1px solid {MIN_COLOR_BORDER};
        margin-bottom: 30px;
    }}
    .main-title-minimal {{
        font-size: 2em;
        color: {MIN_COLOR_TEXT_PRIMARY};
        font-weight: 600;
        margin: 0;
    }}
    .main-subtitle-minimal {{
        font-size: 1em;
        color: {MIN_COLOR_TEXT_SECONDARY};
        margin-top: 5px;
    }}

    /* --- Subheader Styling (st.subheader) --- */
    h2 {{
        color: {MIN_COLOR_TEXT_PRIMARY};
        border-bottom: 1px solid {MIN_COLOR_BORDER};
        padding-bottom: 8px;
        margin-top: 40px;
        margin-bottom: 25px;
        font-weight: 500;
        font-size: 1.3em;
    }}

    /* --- Sidebar --- */
    section[data-testid="stSidebar"] {{
        background-color: {MIN_COLOR_BACKGROUND};
        border-right: 1px solid {MIN_COLOR_BORDER};
        padding: 25px 20px;
    }}
    section[data-testid="stSidebar"] h1 {{ /* Sidebar Title */
        color: {MIN_COLOR_TEXT_PRIMARY} !important;
        font-weight: 600 !important;
        text-align: left !important;
        font-size: 1.2em !important;
        margin: 0 0 20px 0 !important;
        padding-bottom: 10px !important;
        border-bottom: 1px solid {MIN_COLOR_BORDER} !important;
    }}
    .streamlit-expanderHeader {{
        font-size: 0.95em !important;
        font-weight: 500 !important;
        color: {MIN_COLOR_TEXT_PRIMARY} !important;
        padding: 10px 0px !important; /* Remove side padding */
        border-bottom: 1px solid {MIN_COLOR_BORDER};
        border-radius: 0;
    }}
    .streamlit-expanderHeader:hover {{
        color: {MIN_COLOR_ACCENT} !important;
        background-color: transparent !important;
    }}
    .streamlit-expander {{
        border: none;
        box-shadow: none;
    }}
    section[data-testid="stSidebar"] .stFileUploader label {{
        color: {MIN_COLOR_TEXT_PRIMARY} !important;
        font-size: 0.9em !important;
        font-weight: 500;
    }}
     section[data-testid="stSidebar"] .stFileUploader > div > div {{
        border: 1px dashed {MIN_COLOR_TEXT_FAINT};
        background-color: #F8F9FA; /* Slightly off-white dropzone */
     }}
    section[data-testid="stSidebar"] .stButton>button {{
        background-color: {MIN_COLOR_ACCENT};
        color: {MIN_COLOR_BACKGROUND} !important;
        border: none;
        border-radius: 4px; /* Softer radius */
        padding: 8px 15px;
        font-size: 0.9em;
        font-weight: 500;
        width: 100%;
    }}
    section[data-testid="stSidebar"] .stButton>button:hover {{
        background-color: #0056b3; /* Darker accent */
    }}

    /* --- Metric Styling (Less "Cardy") --- */
    .metric-section {{ margin-bottom: 30px; }}
    .metric-item {{
        padding: 10px 0; /* Vertical padding only */
        border-bottom: 1px solid {MIN_COLOR_BORDER}; /* Separator line */
    }}
    .metric-item:last-child {{ border-bottom: none; }}
    .metric-label-minimal {{
        color: {MIN_COLOR_TEXT_SECONDARY};
        font-size: 0.85em;
        margin-bottom: 3px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .metric-value-minimal {{
        color: {MIN_COLOR_TEXT_PRIMARY};
        font-size: 1.8em;
        font-weight: 600;
    }}
    .metric-delta-minimal {{
        font-size: 0.9em;
        font-weight: 500;
    }}
    .metric-delta-minimal.positive {{ color: {MIN_COLOR_POSITIVE}; }}
    .metric-delta-minimal.negative {{ color: {MIN_COLOR_NEGATIVE}; }}


    /* --- Main Download Button --- */
    .stDownloadButton>button {{
        background-color: {MIN_COLOR_ACCENT};
        color: {MIN_COLOR_BACKGROUND} !important;
        border: none;
        border-radius: 4px;
        font-weight: 500;
        padding: 9px 20px;
        font-size: 0.95em;
    }}
    .stDownloadButton>button:hover {{ background-color: #0056b3; }}

    /* --- Alert Messages --- */
    div[data-testid="stAlert"] {{ border-radius: 4px; border-width: 1px; border-style: solid; padding: 12px 15px; font-size: 0.9em; box-shadow: none;}}
    div[data-testid="stAlert"][data-baseweb="alert-success"] {{ background-color: #E9F7EF; border-color: #A6D9BE; color: #1E4620; }}
    div[data-testid="stAlert"][data-baseweb="alert-success"] svg {{ fill: {MIN_COLOR_POSITIVE}; }}
    div[data-testid="stAlert"][data-baseweb="alert-info"]    {{ background-color: #E0F3FF; border-color: #A9D7F7; color: #014A7F; }}
    div[data-testid="stAlert"][data-baseweb="alert-info"] svg{{ fill: {MIN_COLOR_ACCENT}; }}
    /* Warning and Error can be styled similarly if needed */

    /* --- Dataframe Styling Wrappers --- */
    .stDataFrame {{
        border: 1px solid {MIN_COLOR_BORDER};
        border-radius: 4px;
        background-color: {MIN_COLOR_BACKGROUND};
        box-shadow: none;
    }}
    div.stMarkdown > div[data-testid="element-container"] > div > table {{ /* HTML Table */
        margin-bottom: 30px;
        background-color: {MIN_COLOR_BACKGROUND};
        box-shadow: none;
        border-radius: 4px;
        border: 1px solid {MIN_COLOR_BORDER};
    }}

    /* Hide Streamlit footer */
    .stApp > footer {{ visibility: hidden; }}
    hr {{ border-top: 1px solid {MIN_COLOR_BORDER}; margin: 35px 0; }}

    /* Wrapper for main content sections */
    .content-wrapper-minimal {{
        padding: 0px 30px 30px 30px;
    }}
    /* Styling for Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {MIN_COLOR_BACKGROUND};
        padding-bottom: 0px;
        border-bottom: 1px solid {MIN_COLOR_BORDER};
        gap: 20px; /* More space between tab buttons */
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
        color: {MIN_COLOR_TEXT_SECONDARY};
        padding: 10px 0px; /* Padding only bottom for indicator */
        font-weight: 500;
        font-size: 1em;
        border-radius: 0;
        border-bottom: 2px solid transparent;
        margin-bottom: -1px; /* Overlap border */
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        color: {MIN_COLOR_ACCENT};
        background-color: transparent;
    }}
    .stTabs [data-baseweb="tab--selected"] {{
        color: {MIN_COLOR_ACCENT};
        font-weight: 600;
        border-bottom: 2px solid {MIN_COLOR_ACCENT};
        background-color: transparent;
    }}
    .stTabs [data-testid="stMarkdownContainer"] {{ padding-top: 30px; }}
</style>
""", unsafe_allow_html=True)

# --- Main Title Section ---
st.markdown("""
<div class='main-header-minimal'>
    <p class='main-title-minimal'>Cashflow Forecast</p>
    <p class='main-subtitle-minimal'>A clear view of your projected financial health.</p>
</div>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def format_week_range(start_date):
    end_date = start_date + pd.Timedelta(days=6)
    return f"{start_date.day} {start_date.strftime('%b')} - {end_date.day} {end_date.strftime('%b')}"

def style_table_minimal(df_to_style):
    styled_df = df_to_style.style.format(
        lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) and x != 0 else ("—" if isinstance(x, (int, float)) and x == 0 else x), # Em-dash for zero
        na_rep="—"
    ).set_properties(**{
        'font-size': '10pt', 'border': f'1px solid {MIN_COLOR_BORDER}',
        'font-family': "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
        'color': MIN_COLOR_TEXT_PRIMARY, 'width': '100%',
        'border-collapse': 'collapse',
    }) \
    .set_table_styles([
        {'selector': 'caption', 'props': [('caption-side', 'top'), ('font-size', '1.1em'), ('font-weight', '500'), ('color', MIN_COLOR_TEXT_PRIMARY), ('margin-bottom', '15px'), ('text-align', 'left')]},
        {'selector': 'th', 'props': [
            ('text-align', 'left'), ('padding', '10px 12px'), ('font-weight', '500'),
            ('color', MIN_COLOR_TEXT_SECONDARY), ('background-color', '#F8F9FA'), # Very light header
            ('border-bottom', f'1px solid {MIN_COLOR_TEXT_FAINT}')]},
        {'selector': 'th.col_heading', 'props': [('text-align', 'center')]},
        {'selector': 'td', 'props': [
            ('text-align', 'center'), ('padding', '10px 12px'),
            ('border-bottom', f'1px solid {MIN_COLOR_BORDER}')]},
        {'selector': 'th.row_heading.level0', 'props': [('font-weight', '500'), ('color', MIN_COLOR_TEXT_PRIMARY)]},
        {'selector': 'tr:last-child td, tr:last-child th.row_heading', 'props': [('border-bottom', 'none')]},
        {'selector': 'tr:hover', 'props': [('background-color', '#F1F3F5')]},
    ])
    def highlight_minimal(s):
        styles = [''] * len(s)
        for i, val_orig in s.items():
            idx_loc = s.index.get_loc(i); val = pd.to_numeric(val_orig, errors='coerce')
            if pd.isna(val) or val == 0: continue
            if val > 0: styles[idx_loc] = f'color: {MIN_COLOR_POSITIVE};'
            elif val < 0: styles[idx_loc] = f'color: {MIN_COLOR_NEGATIVE};'
        return styles
    numeric_cols = df_to_style.select_dtypes(include=np.number).columns.tolist()
    valid_numeric_cols = [col for col in numeric_cols if col in df_to_style.columns]
    if valid_numeric_cols:
        styled_df = styled_df.apply(highlight_minimal, subset=valid_numeric_cols, axis=0)

    def style_net_cashflow_minimal(row):
        if row.name == ("Net Cashflow", ""): return [f'font-weight: 600; background-color: #F1F3F5; color: {MIN_COLOR_TEXT_PRIMARY}; border-top: 1px solid {MIN_COLOR_TEXT_FAINT};'] * len(row)
        return [''] * len(row)
    styled_df = styled_df.apply(style_net_cashflow_minimal, axis=1)
    return styled_df

# --- Sidebar ---
with st.sidebar:
    st.markdown("<h1>Setup</h1>", unsafe_allow_html=True)
    with st.expander("Download Sample Template", expanded=True):
        sample_data = pd.DataFrame({"Party Type": ["Supplier", "Customer"],"Party Name": ["ABC Ltd", "XYZ Inc"],"Due Date": ["2024-07-15", "2024-07-10"],"Expected Date": ["2024-07-20", "2024-07-14"],"Amount": [-10000, 12000]})
        sample_data["Due Date"] = pd.to_datetime(sample_data["Due Date"]).dt.strftime('%Y-%m-%d')
        sample_data["Expected Date"] = pd.to_datetime(sample_data["Expected Date"]).dt.strftime('%Y-%m-%d')
        st.download_button(label="Download Template CSV", data=sample_data.to_csv(index=False).encode('utf-8'), file_name="cashflow_template_minimal.csv", mime="text/csv")

    uploaded_file = st.file_uploader("Upload Cashflow Data", type=["csv", "xlsx"])
    st.markdown(f"<p style='color:{MIN_COLOR_TEXT_FAINT}; font-size:0.8em; text-align:center; padding-top:30px;'>Minimalist Dashboard</p>", unsafe_allow_html=True)

# --- Altair Chart Theming for Minimalist Theme ---
chart_theme_minimal = {
    "background": "transparent",
    "font": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
    "title": {"color": MIN_COLOR_TEXT_PRIMARY, "fontSize": 14, "fontWeight": 500, "anchor": "start", "dy": -20, "dx":0},
    "axis": {
        "labelColor": MIN_COLOR_TEXT_SECONDARY, "titleColor": MIN_COLOR_TEXT_SECONDARY,
        "gridColor": MIN_COLOR_BORDER, "domain": False, "ticks": False,
        "labelFontSize": 10, "titleFontSize": 11, "titleFontWeight": 500, "labelPadding": 5, "titlePadding": 10,
    },
    "legend": None, # Often removed in minimalist designs unless crucial
    "view": {"stroke": None},
    "bar": {"discreteBandSize": {"band": 0.8}},
    "text": {"color": MIN_COLOR_TEXT_PRIMARY, "fontSize": 9, "fontWeight": 400}
}

# --- Main Content ---
st.markdown("<div class='content-wrapper-minimal'>", unsafe_allow_html=True)

if uploaded_file:
    with st.spinner("Processing data..."):
        try:
            # --- Data Loading and Processing ---
            if uploaded_file.name.endswith(".csv"): df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".xlsx"): df = pd.read_excel(uploaded_file, sheet_name=0, engine='openpyxl')
            else: st.error("Unsupported file type."); st.stop()
            st.success(f"File `{uploaded_file.name}` processed.")
            df.columns = df.columns.str.replace('\ufeff', '', regex=False).str.strip().str.lower()
            required_cols = {"party type", "party name", "due date", "expected date", "amount"}
            missing_cols = required_cols - set(df.columns)
            if missing_cols: st.error(f"Missing required columns: {', '.join(missing_cols)}."); st.stop()
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
            for col in ["due date", "expected date"]:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            initial_row_count = len(df); df.dropna(subset=['due date', 'expected date', 'party type', 'party name'], inplace=True)
            if len(df) < initial_row_count: st.info(f"{initial_row_count - len(df)} rows removed due to missing critical values.")
            if df.empty: st.error("No valid data remaining."); st.stop()
            df["allocation date"] = df[["due date", "expected date"]].max(axis=1)
            df["week_start"] = df["allocation date"].dt.to_period("W").apply(lambda r: r.start_time)
            df["week_range"] = df["week_start"].apply(format_week_range)
            unique_week_starts = sorted(df["week_start"].unique())
            all_week_ranges_sorted = [format_week_range(ws) for ws in unique_week_starts]

            # --- OVERVIEW METRICS ---
            st.subheader("Financial Overview")
            total_inflow = df[df['amount'] > 0]['amount'].sum()
            total_outflow_val = df[df['amount'] < 0]['amount'].sum()
            net_overall_cashflow = df['amount'].sum()

            cols_metrics = st.columns(3)
            with cols_metrics[0]:
                st.markdown(f"<div class='metric-item'><p class='metric-label-minimal'>Total Inflow</p><p class='metric-value-minimal'>{total_inflow:,.0f}</p></div>", unsafe_allow_html=True)
            with cols_metrics[1]:
                st.markdown(f"<div class='metric-item'><p class='metric-label-minimal'>Total Outflow</p><p class='metric-value-minimal'>{total_outflow_val:,.0f}</p></div>", unsafe_allow_html=True)
            with cols_metrics[2]:
                delta_text, delta_class = "", ""
                if abs(total_outflow_val) > 0: net_perc = (net_overall_cashflow / abs(total_outflow_val)) * 100 if abs(total_outflow_val) != 0 else 0; delta_text = f"{net_perc:.1f}%"
                elif net_overall_cashflow > 0: delta_text = "Inflow Only"
                if net_overall_cashflow >= 0 : delta_class = "positive"
                else: delta_class = "negative"
                st.markdown(f"<div class='metric-item'><p class='metric-label-minimal'>Overall Net</p><p class='metric-value-minimal'>{net_overall_cashflow:,.0f} <span class='metric-delta-minimal {delta_class}'>{delta_text}</span></p></div>", unsafe_allow_html=True)

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
            
            # --- TABS FOR DETAILS ---
            tab_forecast, tab_charts, tab_data = st.tabs(["Weekly Forecast", "Visual Trends", "Raw Data"])

            with tab_forecast:
                if not final_table.empty and "No Data" not in final_table.columns:
                    st.markdown(style_table_minimal(final_table).to_html().replace('style="',"style=\"font-variant-numeric: tabular-nums;"), unsafe_allow_html=True) # Ensure numbers align well
                else: st.info("No forecast table to display.")
            
            with tab_charts:
                st.subheader("Weekly Net Cashflow")
                if not net_cashflow_series.empty:
                    net_df = net_cashflow_series.reset_index(); net_df.columns = ["Week Range", "Net Cashflow"]
                    if not net_df.empty and not net_df["Net Cashflow"].isnull().all():
                        net_df["Week Range"] = pd.Categorical(net_df["Week Range"], categories=all_week_ranges_sorted, ordered=True); net_df = net_df.sort_values("Week Range")
                        bars = alt.Chart(net_df).mark_bar(cornerRadiusTopLeft=2, cornerRadiusTopRight=2, size=15).encode(
                            x=alt.X("Week Range:N", sort=None, title=None, axis=alt.Axis(labelAngle=-45, format='%d %b')),
                            y=alt.Y("Net Cashflow:Q", title="Net Cashflow", axis=alt.Axis(format="~s")),
                            color=alt.condition(alt.datum["Net Cashflow"] >= 0, alt.value(MIN_COLOR_POSITIVE), alt.value(MIN_COLOR_NEGATIVE)),
                            tooltip=[alt.Tooltip("Week Range:N", title="Week"), alt.Tooltip("Net Cashflow:Q", title="Amount", format=",.0f")]
                        )
                        text_labels = bars.mark_text(align="center", baseline="middle", dy=alt.expr("datum['Net Cashflow'] >= 0 ? -7 : 7")).encode(
                            text=alt.Text("Net Cashflow:Q", format=",.0f"))
                        chart = (bars + text_labels).properties(height=300).configure(**chart_theme_minimal)
                        st.altair_chart(chart, use_container_width=True)
                else: st.info("No weekly net cashflow data for chart.")

                st.subheader("Totals by Party Type")
                if not df.empty:
                    summary_by_type = df.groupby("party type")["amount"].sum().reset_index(); summary_by_type.columns = ["Party Type", "Total Amount"]
                    chart_summary_data = [] # ... (data prep same as before)
                    customers_total = summary_by_type[summary_by_type["Party Type"].str.lower().str.contains("customer", case=False)]["Total Amount"].sum()
                    suppliers_total = summary_by_type[summary_by_type["Party Type"].str.lower().str.contains("supplier", case=False)]["Total Amount"].sum()
                    other_types_summary = summary_by_type[~summary_by_type["Party Type"].str.lower().str.contains("customer|supplier", case=False, regex=True)]
                    if customers_total != 0: chart_summary_data.append({"Party Type": "Customers", "Amount": customers_total})
                    if suppliers_total != 0: chart_summary_data.append({"Party Type": "Suppliers", "Amount": suppliers_total})
                    for _, row in other_types_summary.iterrows(): chart_summary_data.append({"Party Type": row["Party Type"], "Amount": row["Total Amount"]})

                    if chart_summary_data:
                        summary_chart_df = pd.DataFrame(chart_summary_data)
                        if not summary_chart_df.empty and not summary_chart_df["Amount"].isnull().all():
                             summary_bars_party = alt.Chart(summary_chart_df).mark_bar(size=20).encode(
                                x=alt.X('Amount:Q', title='Total Amount', axis=alt.Axis(format="~s")),
                                y=alt.Y('Party Type:N', sort='-x', title=None),
                                color=alt.condition(alt.datum.Amount >= 0, alt.value(MIN_COLOR_POSITIVE), alt.value(MIN_COLOR_NEGATIVE)),
                                tooltip=['Party Type', alt.Tooltip('Amount:Q', format=',.0f')]
                            ).properties(height=alt.Step(35)).configure(**chart_theme_minimal)
                             st.altair_chart(summary_bars_party, use_container_width=True)
                    else: st.info("No data for party type summary.")
                else: st.info("Upload data for party type analysis.")

            with tab_data:
                st.subheader("Uploaded Data")
                st.dataframe(df[['party type', 'party name', 'due date', 'expected date', 'amount', 'allocation date', 'week_range']].head(50), height=400, use_container_width=True)
                st.markdown("---")
                st.subheader("Export Forecast")
                # ... (Export logic remains the same, Excel styling uses theme colors)
                towrite = BytesIO()
                export_table_min = final_table.copy() # Use a different var name if needed
                if isinstance(export_table_min.index, pd.MultiIndex): export_table_min = export_table_min.reset_index()
                with pd.ExcelWriter(towrite, engine="xlsxwriter") as writer:
                    export_table_min.to_excel(writer, sheet_name="Cashflow_Forecast_Minimal", index=False)
                    workbook  = writer.book; worksheet = writer.sheets["Cashflow_Forecast_Minimal"]
                    header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': MIN_COLOR_TEXT_FAINT, 'font_color': MIN_COLOR_BACKGROUND, 'border': 1, 'border_color': MIN_COLOR_BORDER})
                    for col_num, value in enumerate(export_table_min.columns.values): worksheet.write(0, col_num, value, header_format)
                    # ... (rest of Excel formatting) ...
                st.download_button(label="Download Forecast as Excel", data=towrite.getvalue(), file_name="cashflow_forecast_minimal.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        except Exception as e: st.error(f"An error occurred: {e}"); st.exception(e)
else:
    st.markdown("<div style='text-align:center; padding: 40px 20px;'>", unsafe_allow_html=True)
    st.info("👋 Upload your cashflow data using the sidebar to begin.")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True) # Close content-wrapper-minimal
