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

# --- Custom CSS ---
# Assuming the CSS part is intentionally minimal or managed elsewhere.
# If specific CSS styles were intended here, they should be added.
st.markdown(f"""
<style>
    /* Base body styling for minimalism */
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        color: {MIN_COLOR_TEXT_PRIMARY};
        background-color: {MIN_COLOR_BACKGROUND};
    }}

    /* Custom header styling */
    .main-header-minimal {{
        padding: 2rem 0rem;
        text-align: left;
        border-bottom: 1px solid {MIN_COLOR_BORDER};
        margin-bottom: 2rem;
    }}
    .main-title-minimal {{
        font-size: 2.5rem;
        font-weight: 600;
        color: {MIN_COLOR_TEXT_PRIMARY};
        margin-bottom: 0.5rem;
    }}
    .main-subtitle-minimal {{
        font-size: 1.1rem;
        color: {MIN_COLOR_TEXT_SECONDARY};
    }}

    /* Metric styles */
    div[data-testid="stMetric"] > div > div:first-child {{ /* Metric label */
        color: {MIN_COLOR_TEXT_SECONDARY};
    }}

    /* Sidebar header */
    .stSidebar h1 {{
        font-size: 1.5rem;
        font-weight: 600;
        color: {MIN_COLOR_ACCENT};
        padding-bottom: 0.5rem;
        border-bottom: 1px solid {MIN_COLOR_BORDER};
        margin-bottom: 1rem;
    }}
    /* ... (any other original CSS styles if they existed) ... */
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
    return f"{start_date.strftime('%d %b')} - {end_date.strftime('%d %b %Y')}" # Added %Y for year clarity

def style_table_minimal(df_to_style):
    styled_df = df_to_style.style.format(
        lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) and x != 0 else "—",
        na_rep="—"
    ).set_properties(**{
        'font-size': '10pt',
        'border': f'1px solid {MIN_COLOR_BORDER}',
        'font-family': "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
        'color': MIN_COLOR_TEXT_PRIMARY,
        'width': 'auto', # Ensure table width is reasonable
        'margin': 'auto' # Center table if it's narrower than container
    }).set_table_styles([
        {'selector': 'th', 'props': [
            ('text-align', 'left'),
            ('padding', '10px 12px'),
            ('background-color', '#F8F9FA'), # Light gray for headers
            ('border-bottom', f'2px solid {MIN_COLOR_ACCENT}')]}, # Accent border for headers
        {'selector': 'th.col_heading', 'props': [('text-align', 'center')]}, # Center column headers
        {'selector': 'th.row_heading', 'props': [('text-align', 'left')]}, # Left align row headers (index)
        {'selector': 'td', 'props': [
            ('text-align', 'right'), # Typically numbers are right-aligned
            ('padding', '10px 12px'),
            ('border-bottom', f'1px solid {MIN_COLOR_BORDER}')]},
        {'selector': 'tr:hover td', 'props': [('background-color', '#EFF7FF')]}, # Hover effect
        {'selector': 'tr:last-child td', 'props': [('border-bottom', 'none')]},
    ])

    numeric_cols = df_to_style.select_dtypes(include=np.number).columns.tolist()
    def color_values(val):
        if isinstance(val, (int, float)):
            if val > 0: return f'color: {MIN_COLOR_POSITIVE};'
            if val < 0: return f'color: {MIN_COLOR_NEGATIVE};'
        return ''
    styled_df = styled_df.map(color_values, subset=numeric_cols) # map is correct for element-wise

    # Net cashflow row styling - CORRECTED
    if not df_to_style.empty and ("Net Cashflow", "") in df_to_style.index:
        def highlight_net_cashflow_row(row_series):
            if row_series.name == ("Net Cashflow", ""):
                return [f'font-weight: 600; background-color: #F1F3F5; color: {MIN_COLOR_TEXT_PRIMARY};'] * len(row_series)
            return [''] * len(row_series)
        styled_df = styled_df.apply(highlight_net_cashflow_row, axis=1)

    return styled_df

# --- Sidebar ---
with st.sidebar:
    st.markdown("<h1>Setup</h1>", unsafe_allow_html=True)

    with st.expander("📥 Sample Data", expanded=True):
        sample_data = pd.DataFrame({
            "Party Type": ["Supplier", "Customer", "Supplier"],
            "Party Name": ["ABC Ltd", "XYZ Inc", "DEF Corp"],
            "Due Date": ["2024-07-15", "2024-07-10", "2024-07-20"],
            "Expected Date": ["2024-07-20", "2024-07-14", "2024-07-22"], # Sample dates
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

            df = df.dropna(subset=['party type', 'party name']) # party type / name are essential
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
            for col in ["due date", "expected date"]:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            df = df.dropna(subset=["due date", "expected date", "amount"]) # Ensure dates and amount are valid

            if df.empty:
                st.warning("No valid data found after cleaning. Please check your file.")
                st.stop()

            df["allocation date"] = df[["due date", "expected date"]].max(axis=1)
            df["week_start"] = df["allocation date"].dt.to_period("W").dt.start_time

            # CORRECTED: Ensure chronological order for week_range
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
            # Ensure columns in pivot table also follow the order if any are missing from data
            # This can happen if some weeks have no data items but are part of the overall range
            # For this specific setup, pivot_table will only have columns for which data exists.
            # If we want all weeks in a range, we might need to reindex.
            # For now, using existing columns from pivot_table.columns which should be CategoricalIndex.

            if pivot_table.empty and not df.empty: # Data exists, but pivot is empty (e.g. only one type/name, so index is not Multi)
                 st.warning("Could not create a pivot table. This might happen if data structure is not suitable for pivoting as configured (e.g. not enough distinct party types/names).")
                 # Try a simpler pivot or inform user
            
            if not pivot_table.columns.empty:
                net_row_values = pivot_table.sum()
                net_row = pd.DataFrame(
                    [net_row_values.values], # Use .values to ensure data alignment
                    index=pd.MultiIndex.from_tuples([("Net Cashflow", "")]),
                    columns=net_row_values.index # Preserve CategoricalIndex from pivot_table.columns
                )
                final_table = pd.concat([pivot_table, net_row])
            elif not df.empty : # pivot_table columns are empty, means no weekly data was aggregated
                # Create an empty final_table with correct structure for display, or handle message
                st.info("No weekly data to display in the forecast table.")
                # Create a dummy final_table for styling or skip tab1 display
                final_table = pd.DataFrame(columns=['No Data Available']).set_index(pd.MultiIndex.from_tuples([("Net Cashflow", "")]))

            else: # df was empty to begin with, this case is already handled by st.stop()
                final_table = pd.DataFrame() # Should not be reached if df.empty leads to st.stop()

            st.subheader("Financial Overview")
            col1, col2, col3 = st.columns(3)
            total_inflow = df[df['amount'] > 0]['amount'].sum()
            total_outflow = df[df['amount'] < 0]['amount'].sum() # This is negative
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
                     # Use a slightly modified style_table for this specific table if needed
                    st.markdown(style_table_minimal(final_table).to_html(), unsafe_allow_html=True)
                elif "No Data Available" in final_table.columns:
                    st.info("No weekly forecast data to display.")
                else: # final_table is completely empty
                    st.info("No data to display in the forecast table.")


            with tab2:
                st.markdown("#### Net Cashflow Trend")
                if not final_table.empty and ("Net Cashflow", "") in final_table.index and not final_table.columns.empty and not ("No Data Available" in final_table.columns):
                    net_series = final_table.loc[("Net Cashflow", "")]
                    # CORRECTED: Prepare data for Altair
                    net_data = net_series.reset_index()
                    # The value column name is the name of the series, which is ("Net Cashflow", "")
                    # The index column name is final_table.columns.name, which is "week_range"
                    net_data.rename(columns={("Net Cashflow", ""): 'Net_Cashflow_Value', 'week_range': 'Week'}, inplace=True)

                    if not net_data.empty:
                        chart = alt.Chart(net_data).mark_bar().encode(
                            x=alt.X('Week:N', title='Week', sort=None), # Use 'Week' and sort=None due to Categorical
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
                    # xlsxwriter cannot handle CategoricalIndex directly in older versions for sheet names etc.
                    # but writing data should be fine. For safety, convert to string if issues.
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

        except Exception as e:
            st.error(f"An error occurred during processing: {str(e)}")
            import traceback
            st.error(f"Traceback: {traceback.format_exc()}")


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
