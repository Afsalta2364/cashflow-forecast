import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO
import numpy as np

# --- Page Setup ---
st.set_page_config(
    page_title="Minimalist Cashflow Dashboard",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Minimalist Theme Colors ---
MIN_COLOR_BACKGROUND = "#FFFFFF"
MIN_COLOR_TEXT_PRIMARY = "#212529"
MIN_COLOR_TEXT_SECONDARY = "#6C757D"
MIN_COLOR_TEXT_FAINT = "#ADB5BD"
MIN_COLOR_ACCENT = "#007BFF"
MIN_COLOR_POSITIVE = "#28A745"
MIN_COLOR_NEGATIVE = "#DC3545"
MIN_COLOR_BORDER = "#E9ECEF"

# --- Custom CSS for Clean & Elegant Look ---
st.markdown(f"""
<style>
    /* Body styling */
    body {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        color: {MIN_COLOR_TEXT_PRIMARY};
        background-color: {MIN_COLOR_BACKGROUND};
        margin: 0;
        padding: 0 2rem;
    }}

    /* Header */
    .main-header-minimal {{
        padding: 2rem 0 1.5rem 0;
        text-align: left;
        border-bottom: 2px solid {MIN_COLOR_ACCENT};
        margin-bottom: 2rem;
    }}
    .main-title-minimal {{
        font-size: 2.75rem;
        font-weight: 700;
        color: {MIN_COLOR_TEXT_PRIMARY};
        margin-bottom: 0.3rem;
        letter-spacing: -0.03em;
    }}
    .main-subtitle-minimal {{
        font-size: 1.15rem;
        font-weight: 400;
        color: {MIN_COLOR_TEXT_SECONDARY};
        letter-spacing: 0.01em;
    }}

    /* Metrics */
    div[data-testid="stMetric"] > div > div:first-child {{
        color: {MIN_COLOR_TEXT_SECONDARY};
        font-weight: 600;
        letter-spacing: 0.02em;
    }}
    div[data-testid="stMetric"] > div > div:last-child {{
        font-size: 1.6rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        color: {MIN_COLOR_TEXT_PRIMARY};
    }}

    /* Sidebar header */
    .stSidebar h1 {{
        font-size: 1.75rem;
        font-weight: 700;
        color: {MIN_COLOR_ACCENT};
        padding-bottom: 0.75rem;
        border-bottom: 2px solid {MIN_COLOR_BORDER};
        margin-bottom: 1.25rem;
    }}

    /* Table styles */
    table.dataframe {{
        border-collapse: separate !important;
        border-spacing: 0 8px !important;
        width: 100% !important;
        font-size: 11pt !important;
        font-weight: 500 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
        color: {MIN_COLOR_TEXT_PRIMARY} !important;
    }}

    table.dataframe th {{
        background-color: #F3F6F9 !important;
        color: {MIN_COLOR_ACCENT} !important;
        font-weight: 700 !important;
        text-align: left !important;
        padding: 14px 20px !important;
        border-bottom: 2px solid {MIN_COLOR_ACCENT} !important;
        letter-spacing: 0.02em;
        user-select: none;
        vertical-align: middle !important;
    }}

    table.dataframe th.col_heading {{
        text-align: center !important;
        font-weight: 600 !important;
    }}

    table.dataframe th.row_heading {{
        text-align: left !important;
        padding-left: 20px !important;
    }}

    table.dataframe td {{
        padding: 12px 20px !important;
        border-bottom: 1px solid {MIN_COLOR_BORDER} !important;
        vertical-align: middle !important;
        font-weight: 500 !important;
        text-align: right !important;
        white-space: nowrap;
    }}

    table.dataframe td.row_heading {{
        text-align: left !important;
        padding-left: 20px !important;
    }}

    /* Numeric columns align right */
    table.dataframe td.numeric {{
        text-align: right !important;
        font-feature-settings: "tnum" !important; /* Tabular numbers for alignment */
        font-variant-numeric: tabular-nums !important;
    }}

    /* Hover effect */
    table.dataframe tbody tr:hover td {{
        background-color: #E9F2FF !important;
        transition: background-color 0.2s ease-in-out;
    }}

    /* Net cashflow row highlight */
    table.dataframe tbody tr.net-cashflow-row td {{
        font-weight: 700 !important;
        background-color: #F9FAFB !important;
        color: {MIN_COLOR_TEXT_PRIMARY} !important;
        border-top: 2px solid {MIN_COLOR_ACCENT} !important;
        border-bottom: 2px solid {MIN_COLOR_ACCENT} !important;
    }}

    /* Scrollbar for large tables */
    div[data-testid="stDataFrame"] > div:first-child {{
        overflow-x: auto;
        border-radius: 8px;
        box-shadow: inset 0 0 5px #d6d9dc;
        padding-bottom: 10px;
    }}

</style>
""", unsafe_allow_html=True)

# --- Main Title ---
st.markdown("""
<div class='main-header-minimal'>
    <p class='main-title-minimal'>Cashflow Forecast</p>
    <p class='main-subtitle-minimal'>A clear view of your projected financial health.</p>
</div>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def format_week_range(start_date):
    end_date = start_date + pd.Timedelta(days=6)
    return f"{start_date.strftime('%d %b')} - {end_date.strftime('%d %b %Y')}"

@st.cache_data
def process_data(uploaded_file):
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file, engine='openpyxl')

        required_cols = {"party type", "party name", "due date", "expected date", "amount"}
        df.columns = df.columns.str.lower().str.strip()
        missing_cols = required_cols - set(df.columns)
        if missing_cols:
            st.error(f"Missing columns: {', '.join(missing_cols)}")
            st.stop()

        df = df.dropna(subset=['party type', 'party name'])
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
        for col in ["due date", "expected date"]:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        df = df.dropna(subset=["due date", "expected date", "amount"])

        if df.empty:
            st.warning("No valid data found after cleaning. Please check your file.")
            st.stop()

        df["allocation date"] = df[["due date", "expected date"]].max(axis=1)
        df["week_start"] = df["allocation date"].dt.to_period("W").dt.start_time

        df = df.sort_values("week_start")
        df["week_range"] = df["week_start"].apply(format_week_range)
        ordered_week_ranges = df["week_range"].unique()
        df["week_range"] = pd.Categorical(df["week_range"], categories=ordered_week_ranges, ordered=True)

        pivot_table = df.pivot_table(
            index=["party type", "party name"],
            columns="week_range",
            values="amount",
            aggfunc="sum",
            fill_value=0
        )

        if pivot_table.empty and not df.empty:
            st.warning("Could not create a pivot table. This might happen if data structure is not suitable for pivoting as configured (e.g. not enough distinct party types/names).")
            return df, pd.DataFrame(), "No Pivot"

        if not pivot_table.columns.empty:
            net_row_values = pivot_table.sum()
            net_row = pd.DataFrame(
                [net_row_values.values],
                index=pd.MultiIndex.from_tuples([("Net Cashflow", "")]),
                columns=net_row_values.index
            )
            final_table = pd.concat([pivot_table, net_row])
        elif not df.empty:
            st.info("No weekly data to display in the forecast table.")
            final_table = pd.DataFrame(columns=['No Data Available']).set_index(pd.MultiIndex.from_tuples([("Net Cashflow", "")]))
        else:
            final_table = pd.DataFrame()

        return df, final_table, "OK"

    except Exception as e:
        st.error(f"An error occurred during processing: {str(e)}")
        import traceback
        st.error(f"Traceback: {traceback.format_exc()}")
        return pd.DataFrame(), pd.DataFrame(), "Error"

def style_table_minimal(df_to_style):
    def fmt(x):
        if pd.isna(x) or x == 0:
            return "—"
        if isinstance(x, (int, float)):
            return f"{x:,.0f}"
        return x

    styled_df = df_to_style.style.format(fmt)\
        .set_properties(**{
            'font-family': "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
            'font-size': '11pt',
            'font-weight': '500',
            'color': MIN_COLOR_TEXT_PRIMARY,
            'border-spacing': '0 8px',
            'white-space': 'nowrap'
        })

    numeric_cols = df_to_style.select_dtypes(include=np.number).columns.tolist()
    all_cols = df_to_style.columns.tolist()
    left_cols = [col for col in all_cols if col not in numeric_cols]

    for col in numeric_cols:
        styled_df = styled_df.set_properties(subset=[col], **{'text-align': 'right', 'font-variant-numeric': 'tabular-nums'})
    for col in left_cols:
        styled_df = styled_df.set_properties(subset=[col], **{'text-align': 'left'})

    def color_vals(val):
        if isinstance(val, (int, float)):
            if val > 0:
                return f'color: {MIN_COLOR_POSITIVE};'
            elif val < 0:
                return f'color: {MIN_COLOR_NEGATIVE};'
        return ''

    styled_df = styled_df.applymap(color_vals)

    if not df_to_style.empty and ("Net Cashflow", "") in df_to_style.index:
        def highlight_net(row):
            if row.name == ("Net Cashflow", ""):
                return ['font-weight: 700; background-color: #F9FAFB; color: '+MIN_COLOR_TEXT_PRIMARY+'; border-top: 2px solid '+MIN_COLOR_ACCENT+'; border-bottom: 2px solid '+MIN_COLOR_ACCENT+';'] * len(row)
            return [''] * len(row)
        styled_df = styled_df.apply(highlight_net, axis=1)

    return styled_df

# --- Sidebar ---
with st.sidebar:
    st.markdown("<h1>Setup</h1>", unsafe_allow_html=True)

    with st.expander("📥 Sample Data", expanded=True):
        sample_data = pd.DataFrame({
            "Party Type": ["Supplier", "Customer", "Supplier"],
            "Party Name": ["ABC Ltd", "XYZ Inc", "DEF Corp"],
            "Due Date": ["2024-07-15", "2024-07-10", "2024-07-20"],
            "Expected Date": ["2024-07-20", "2024-07-14", "2024-07-22"],
            "Amount": [-10000, 15000, -7500]
        })
        st.download_button(
            label="Download Template",
            data=sample_data.to_csv(index=False).encode('utf-8'),
            file_name="cashflow_template.csv",
            mime="text/csv"
        )

    uploaded_file = st.file_uploader(
        "Upload Cashflow Data",
        type=["csv", "xlsx"],
        help="CSV or Excel file with columns: Party Type, Party Name, Due Date, Expected Date, Amount"
    )

# --- Main Content ---
if uploaded_file:
    with st.spinner("Processing data..."):
        df, final_table, processing_status = process_data(uploaded_file)

        if processing_status == "OK":
            st.subheader("Financial Overview")
            col1, col2, col3 = st.columns(3)
            total_inflow = df[df['amount'] > 0]['amount'].sum()
            total_outflow = df[df['amount'] < 0]['amount'].sum()
            net_cashflow_total = total_inflow + total_outflow

            with col1:
                st.metric("Total Inflow", f"${total_inflow:,.0f}")
            with col2:
                st.metric("Total Outflow", f"${abs(total_outflow):,.0f}")
            with col3:
                st.metric("Net Cashflow", f"${net_cashflow_total:,.0f}",
                          delta_color="inverse" if net_cashflow_total < 0 else "normal")

            tab1, tab2, tab3 = st.tabs(["🗓️ Forecast Table", "📊 Trend Analysis", "📄 Raw Data"])

            with tab1:
                st.markdown("#### Weekly Cashflow Forecast")
                if not final_table.empty and not ("No Data Available" in final_table.columns):
                    st.markdown(style_table_minimal(final_table).to_html(), unsafe_allow_html=True)
                elif "No Data Available" in final_table.columns:
                    st.info("No weekly forecast data to display.")
                else:
                    st.info("No data to display in the forecast table.")

            with tab2:
                st.markdown("#### Net Cashflow Trend")
                if not final_table.empty and ("Net Cashflow", "") in final_table.index and not final_table.columns.empty and not ("No Data Available" in final_table.columns):
                    net_series = final_table.loc[("Net Cashflow", "")]
                    net_data = net_series.reset_index(name='Net_Cashflow_Value').rename(columns={'week_range': 'Week'})

                    if not net_data.empty:
                        chart = alt.Chart(net_data).mark_bar().encode(
                            x=alt.X('Week:N', title='Week', sort=None),
                            y=alt.Y('Net_Cashflow_Value:Q', title='Amount (USD)'),
                            tooltip=['Week', alt.Tooltip('Net_Cashflow_Value:Q', format=",.0f")],
                            color=alt.condition(
                                alt.datum.Net_Cashflow_Value > 0,
                                alt.value(MIN_COLOR_POSITIVE),
                                alt.value(MIN_COLOR_NEGATIVE)
                            )
                        ).properties(
                            height=350,
                            title='Weekly Net Cashflow'
                        )
                        st.altair_chart(chart, use_container_width=True)
                    else:
                        st.info("No data available for trend analysis.")
                else:
                    st.info("No data available for trend analysis. Upload data or check data integrity.")

            with tab3:
                st.markdown("#### Raw Input Data (Processed)")
                st.dataframe(df, use_container_width=True)

                if not final_table.empty and not ("No Data Available" in final_table.columns):
                    towrite = BytesIO()
                    export_df = final_table.copy()
                    if isinstance(export_df.columns, pd.CategoricalIndex):
                        export_df.columns = export_df.columns.astype(str)

                    with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer:
                        export_df.to_excel(writer, sheet_name="Forecast")

                    st.download_button(
                        label="📥 Export Forecast to Excel",
                        data=towrite.getvalue(),
                        file_name="cashflow_forecast.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.info("No forecast data to export.")
else:
    st.info("👋 Welcome! Please upload a cashflow data file using the sidebar to begin analysis.")
    with st.expander("ℹ️ How to use this dashboard", expanded=False):
        st.markdown("""
        1.  **Download the Template:** Use the "Download Template" button in the sidebar to get a CSV file with the required structure.
        2.  **Prepare Your Data:** Fill the template with your cashflow data. Ensure columns are:
            *   `Party Type` (e.g., Customer, Supplier)
            *   `Party Name` (e.g., Company X, Vendor Y)
            *   `Due Date` (date payment is officially due)
            *   `Expected Date` (date you expect payment/to pay)
            *   `Amount` (positive for inflow, negative for outflow)
        3.  **Upload Your File:** Use the "Upload Cashflow Data" uploader in the sidebar. Supports CSV and Excel files.
        4.  **Analyze:**
            *   View total inflows, outflows, and net cashflow.
            *   See a detailed weekly forecast table.
            *   Analyze weekly net cashflow trends in the chart.
            *   Review your processed raw data.
            *   Export the forecast table to Excel.
        """)
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #ADB5BD;'>Minimalist Cashflow Dashboard by Your Name/Company</p>", unsafe_allow_html=True)
