import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO
import matplotlib
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
    /* ... (keep the same CSS styles as original) ... */
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
    data_col_min_width = '110px'; index_col_party_type_width = '100px'
    index_col_party_name_width = '120px'; index_col_week_range_literal_width = '90px'

    styled_df = df_to_style.style.format(
        lambda x: f"{x:,.0f}" if x != 0 else "-", na_rep="-"
    ).set_caption(f"<span style='font-size: 1.1em; font-weight:500; color: {text_color_light}; display:block; margin-bottom:8px; text-align:center;'>📋 Weekly Cashflow Breakdown</span>") \
    .set_properties(**{
        'font-size': '9pt', 'border': 'none',
        'font-family': "'Inter', 'Segoe UI', sans-serif",
        'color': text_color_light, 'width': 'auto',
        'margin-left': 'auto', 'margin-right': 'auto'
    }).set_table_styles([
        {'selector': '', 'props': [
            ('border-collapse', 'collapse'), ('width', 'auto'),
            ('min-width', '60%'), ('max-width', '95%')]},
        {'selector': 'caption', 'props': [('caption-side', 'top')]},
        {'selector': 'th', 'props': [
            ('text-align', 'center'), ('vertical-align', 'middle'),
            ('padding', '10px 8px'), ('border', f'1px solid {border_color}'),
            ('font-weight', '500'), ('font-size', '9pt'),
            ('color', text_color_light)
        ]},
        {'selector': 'th.col_heading', 'props': [
            ('background-color', bg_header),
            ('min-width', data_col_min_width), ('max-width', data_col_min_width)
        ]},
        {'selector': 'th.index_name', 'props': [
            ('background-color', bg_header),
            ('min-width', index_col_week_range_literal_width), ('max-width', index_col_week_range_literal_width)
        ]},
        {'selector': 'th.row_heading', 'props': [
            ('background-color', bg_index_cols),
            ('font-weight', 'normal'),
        ]},
        {'selector': 'td', 'props': [
            ('background-color', bg_data_cells),
            ('text-align', 'center'), ('vertical-align', 'middle'),
            ('padding', '10px 8px'), ('border', f'1px solid {border_color}'),
            ('min-width', data_col_min_width), ('max-width', data_col_min_width)
        ]},
        {'selector': 'th.row_heading.level0', 'props': [
            ('font-weight', '500'), ('color', '#81a1c1'),
            ('min-width', index_col_party_type_width), ('max-width', index_col_party_type_width)
        ]},
        {'selector': 'th.row_heading.level1', 'props': [
            ('min-width', index_col_party_name_width), ('max-width', index_col_party_name_width)
        ]},
    ])

    def color_zero_values(val):
        return f'color: {text_color_faint};' if val == 0 or pd.isna(val) else f'color: {text_color_light};'
    data_cols_to_style = [col for col in df_to_style.columns if df_to_style[col].dtype in ['int64', 'float64', np.number]]
    if data_cols_to_style:
        styled_df = styled_df.applymap(color_zero_values, subset=data_cols_to_style)

    if numeric_cols:
        valid_numeric_cols_for_subset = [col for col in numeric_cols if col in df_to_style.columns]
        if valid_numeric_cols_for_subset:
            try:
                def subtle_gradient_for_dark(s):
                    styles = [''] * len(s)
                    max_abs_val = s.abs().max()
                    if pd.isna(max_abs_val) or max_abs_val == 0: max_abs_val = 1
                    for i, val in s.items():
                        idx_loc = s.index.get_loc(i)
                        if val > 0:
                            opacity = min(0.3, 0.05 + (val / max_abs_val) * 0.25)
                            styles[idx_loc] = f'background-color: rgba(16, 185, 129, {opacity})'
                        elif val < 0:
                            opacity = min(0.3, 0.05 + (abs(val) / max_abs_val) * 0.25)
                            styles[idx_loc] = f'background-color: rgba(239, 68, 68, {opacity})'
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
            label="Download Template CSV", 
            data=sample_data.to_csv(index=False).encode('utf-8'),
            file_name="cashflow_template.csv", 
            mime="text/csv"
        )
    st.markdown("---")
    uploaded_file = st.file_uploader(
        "Upload Cashflow Data (CSV or Excel)", 
        type=["csv", "xlsx"],
        help="Upload your CSV or Excel file with cashflow entries."
    )
    st.markdown("---")
    st.caption("Developed with ❤️")

# --- Main Panel for Results ---
if uploaded_file:
    with st.spinner("🚀 Processing your file... Hold tight!"):
        try:
            # Load and validate data
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file, sheet_name=0, engine='openpyxl')
            else:
                st.error("Unsupported file type.")
                st.stop()
            
            df.columns = df.columns.str.replace('\ufeff', '', regex=False).str.strip().str.lower()
            required_cols = {"party type", "party name", "due date", "expected date", "amount"}
            missing_cols = required_cols - set(df.columns)
            if missing_cols:
                st.error(f"Missing required columns: {', '.join(missing_cols)}.")
                st.stop()

            # Data cleaning
            df['party type'] = df['party type'].fillna('Unknown')
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            for col in ["due date", "expected date"]:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            
            initial_row_count = len(df)
            df.dropna(subset=['amount', 'due date', 'expected date'], inplace=True)
            if len(df) < initial_row_count:
                st.info(f"{initial_row_count - len(df)} rows removed due to missing/invalid values.")
            if df.empty:
                st.error("No valid data remaining after processing.")
                st.stop()

            # Process dates
            df["allocation date"] = df[["due date", "expected date"]].max(axis=1)
            df["week_start"] = df["allocation date"].dt.to_period("W").apply(lambda r: r.start_time)
            df["week_range"] = df["week_start"].apply(format_week_range)
            unique_week_starts = sorted(df["week_start"].unique())
            all_week_ranges_sorted = [format_week_range(ws) for ws in unique_week_starts]

            # Key metrics
            st.subheader("🚀 At a Glance: Forecast Summary")
            total_inflow = df[df['amount'] > 0]['amount'].sum()
            total_outflow = df[df['amount'] < 0]['amount'].sum()
            net_cashflow = total_inflow + total_outflow
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Inflow", f"${total_inflow:,.0f}")
            col2.metric("Total Outflow", f"${total_outflow:,.0f}")
            col3.metric("Net Cashflow", f"${net_cashflow:,.0f}", 
                        delta=f"{net_cashflow/total_outflow*100:.1f}%" if total_outflow != 0 else "N/A")

            # Pivot table
            all_parties = df[["party type", "party name"]].drop_duplicates()
            all_weeks_df = pd.DataFrame({"week_range": all_week_ranges_sorted})
            
            if not all_parties.empty and not all_weeks_df.empty:
                all_cross = pd.merge(all_parties, all_weeks_df, how="cross")
                grouped = df.groupby(["party type", "party name", "week_range"], as_index=False)["amount"].sum()
                complete_df = pd.merge(all_cross, grouped, on=["party type", "party name", "week_range"], how="left").fillna(0)
                complete_df['week_range'] = pd.Categorical(complete_df['week_range'], categories=all_week_ranges_sorted, ordered=True)
                pivot_table = complete_df.pivot_table(index=["party type", "party name"], columns="week_range", values="amount", aggfunc="sum", fill_value=0)
                net_row = pd.DataFrame([pivot_table.sum()], index=pd.MultiIndex.from_tuples([("Net Cashflow", "")]))
                final_table = pd.concat([pivot_table, net_row])
                
                # Display styled table
                st.subheader("📊 Detailed Weekly Cashflow Forecast")
                st.markdown(style_table(final_table).to_html(), unsafe_allow_html=True)

                # Net cashflow chart
                net_df = pivot_table.sum().reset_index()
                net_df.columns = ["Week", "Net Cashflow"]
                chart = alt.Chart(net_df).mark_bar().encode(
                    x=alt.X('Week:N', sort=all_week_ranges_sorted),
                    y='Net Cashflow:Q',
                    color=alt.condition(
                        alt.datum["Net Cashflow"] > 0,
                        alt.value("#10B981"),  # Green
                        alt.value("#EF4444")   # Red
                    )
                ).properties(height=300)
                st.altair_chart(chart, use_container_width=True)

                # Export
                st.subheader("📤 Export Forecast")
                towrite = BytesIO()
                with pd.ExcelWriter(towrite, engine="xlsxwriter") as writer:
                    final_table.to_excel(writer, sheet_name="Forecast")
                st.download_button(
                    label="Download Excel Report",
                    data=towrite.getvalue(),
                    file_name="cashflow_forecast.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
else:
    st.info("👈 Upload your cashflow file using the sidebar to get started!")
    with st.expander("💡 How to Use This Dashboard"):
        st.markdown("""
        ## User Guide
        1. **Download Template**: Use the sidebar to get a sample CSV
        2. **Format Your Data**:
           - Include columns: Party Type, Party Name, Due Date, Expected Date, Amount
           - Amounts: Positive for inflows, negative for outflows
        3. **Upload Your File**: Use the sidebar uploader
        4. **Analyze Results**: View forecasts, charts, and export reports
        """)
    st.balloons()
