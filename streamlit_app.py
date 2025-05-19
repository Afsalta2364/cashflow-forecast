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
st.markdown(f"""
<style>
    /* ... (keep original CSS styles) ... */
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
    return f"{start_date.strftime('%d %b')} - {end_date.strftime('%d %b')}"

def style_table_minimal(df_to_style):
    styled_df = df_to_style.style.format(
        lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) and x != 0 else "—",
        na_rep="—"
    ).set_properties(**{
        'font-size': '10pt', 
        'border': f'1px solid {MIN_COLOR_BORDER}',
        'font-family': "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
        'color': MIN_COLOR_TEXT_PRIMARY,
    }).set_table_styles([
        {'selector': 'th', 'props': [
            ('text-align', 'left'), 
            ('padding', '10px 12px'),
            ('background-color', '#F8F9FA'),
            ('border-bottom', f'1px solid {MIN_COLOR_TEXT_FAINT}')]},
        {'selector': 'td', 'props': [
            ('text-align', 'center'), 
            ('padding', '10px 12px'),
            ('border-bottom', f'1px solid {MIN_COLOR_BORDER}')]},
        {'selector': 'tr:last-child td', 'props': [('border-bottom', 'none')]},
    ])
    
    # Color formatting for numeric values
    numeric_cols = df_to_style.select_dtypes(include=np.number).columns.tolist()
    def color_values(val):
        if isinstance(val, (int, float)):
            if val > 0: return f'color: {MIN_COLOR_POSITIVE};'
            if val < 0: return f'color: {MIN_COLOR_NEGATIVE};'
        return ''
    styled_df = styled_df.map(color_values, subset=numeric_cols)
    
    # Net cashflow row styling
    if not df_to_style.empty and ("Net Cashflow", "") in df_to_style.index:
        styled_df = styled_df.map_index(
            lambda v: f'font-weight: 600; background-color: #F1F3F5;' 
            if v == ("Net Cashflow", "") else '', axis=0
        )
    
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
        help="CSV or Excel file with required columns"
    )

# --- Main Content ---
if uploaded_file:
    with st.spinner("Processing data..."):
        try:
            # Load and validate data
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file, engine='openpyxl')
            
            # Clean and validate columns
            required_cols = {"party type", "party name", "due date", "expected date", "amount"}
            df.columns = df.columns.str.lower().str.strip()
            missing_cols = required_cols - set(df.columns)
            if missing_cols:
                st.error(f"Missing columns: {', '.join(missing_cols)}")
                st.stop()
            
            # Clean data
            df = df.dropna(subset=['party type', 'party name'])
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
            for col in ["due date", "expected date"]:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            df = df.dropna(subset=["due date", "expected date"])
            
            # Date calculations
            df["allocation date"] = df[["due date", "expected date"]].max(axis=1)
            df["week_start"] = df["allocation date"].dt.to_period("W").dt.start_time
            df["week_range"] = df["week_start"].apply(format_week_range)
            
            # Create pivot table
            pivot_table = df.pivot_table(
                index=["party type", "party name"],
                columns="week_range",
                values="amount",
                aggfunc="sum",
                fill_value=0
            )
            
            # Add net cashflow row
            net_row = pd.DataFrame(
                [pivot_table.sum()], 
                index=pd.MultiIndex.from_tuples([("Net Cashflow", "")])
            final_table = pd.concat([pivot_table, net_row])
            
            # --- Display Results ---
            st.subheader("Financial Overview")
            col1, col2, col3 = st.columns(3)
            with col1:
                total_inflow = df[df['amount'] > 0]['amount'].sum()
                st.metric("Total Inflow", f"${total_inflow:,.0f}")
            with col2:
                total_outflow = df[df['amount'] < 0]['amount'].sum()
                st.metric("Total Outflow", f"${abs(total_outflow):,.0f}")
            with col3:
                net = total_inflow + total_outflow
                st.metric("Net Cashflow", f"${net:,.0f}", 
                         delta_color="inverse" if net < 0 else "normal")
            
            # Tabs display
            tab1, tab2, tab3 = st.tabs(["Forecast Table", "Trend Analysis", "Raw Data"])
            
            with tab1:
                st.write("Weekly Cashflow Forecast")
                st.markdown(style_table_minimal(final_table).to_html(), 
                            unsafe_allow_html=True)
            
            with tab2:
                # Net cashflow trend chart
                net_data = final_table.loc[("Net Cashflow", "")].reset_index()
                chart = alt.Chart(net_data).mark_bar().encode(
                    x=alt.X('week_range:N', title='Week'),
                    y=alt.Y('Net Cashflow:Q', title='Amount'),
                    color=alt.condition(
                        alt.datum.Net_Cashflow > 0,
                        alt.value(MIN_COLOR_POSITIVE),
                        alt.value(MIN_COLOR_NEGATIVE)
                    )
                ).properties(height=300)
                st.altair_chart(chart, use_container_width=True)
            
            with tab3:
                st.dataframe(df, use_container_width=True)
                # Export button
                towrite = BytesIO()
                with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer:
                    final_table.to_excel(writer, sheet_name="Forecast")
                st.download_button(
                    label="Export to Excel",
                    data=towrite.getvalue(),
                    file_name="cashflow_forecast.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

else:
    st.info("Please upload a file using the sidebar to begin analysis")
    with st.expander("How to use this dashboard"):
        st.markdown("""
        1. **Download** the template CSV
        2. **Format your data** with required columns
        3. **Upload** your CSV or Excel file
        4. **Analyze** cashflow trends and forecasts
        """)
