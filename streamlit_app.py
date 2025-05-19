import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO
# import matplotlib # Pandas styling might use it, but not explicitly called. xlsxwriter handles Excel.
import numpy as np
# openpyxl is used implicitly by pd.read_excel for .xlsx, so it's a runtime dependency.

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
        background-color: #121212;
    }

    /* --- Main Title Area --- */
    .main-title-container {
        padding: 25px 20px; background: #1f2937; border-radius: 8px;
        margin-bottom: 30px; text-align: center; border: 1px solid #374151;
    }
    .main-title { font-size: 2.4em; color: #ffffff; font-weight: 600; letter-spacing: 0.5px; }
    .main-subtitle { font-size: 1.1em; color: #9ca3af; margin-top: 5px; }

    /* --- Subheader Styling (st.subheader) --- */
    h2 {
        color: #d1d5db; border-bottom: 1px solid #4b5563; padding-bottom: 8px;
        margin-top: 35px; margin-bottom: 20px; font-weight: 500;
        font-size: 1.4em; text-align: left;
    }

    /* --- Sidebar --- */
    section[data-testid="stSidebar"] { background-color: #1f2937; border-right: 1px solid #374151; }
    section[data-testid="stSidebar"] h1 {
        color: #60a5fa !important; font-weight: 500 !important; text-align: center !important;
        border-bottom: 1px solid #3b82f6 !important; padding-bottom: 10px !important;
        font-size: 1.3em !important; margin-top: 5px !important;
    }
    .streamlit-expanderHeader {
        font-size: 1.0em !important; font-weight: normal !important; color: #d1d5db !important;
        padding: 8px 0px !important;
    }
    .streamlit-expanderHeader:hover { color: #93c5fd !important; }
    section[data-testid="stSidebar"] .stFileUploader label { color: #d1d5db !important; font-size: 0.95em !important; }
    section[data-testid="stSidebar"] .stButton>button {
        background-color: #3b82f6; color: white !important; border: none; border-radius: 6px;
        padding: 8px 16px; font-size: 0.9em;
    }
    section[data-testid="stSidebar"] .stButton>button:hover { background-color: #2563eb; }

    /* --- Metric Cards --- */
    div[data-testid="stMetric"] {
        background-color: #1f2937; border: 1px solid #374151; border-radius: 8px;
        padding: 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06);
        height: 100%; /* Ensures cards in a row have same height */
    }
    .stMetric > div > div:nth-child(1) { /* Metric Label */
        color: #9ca3af; font-size: 0.85em; font-weight: 400; margin-bottom: 6px;
        text-transform: uppercase; letter-spacing: 0.5px;
    }
    .stMetric > div > div:nth-child(2) { /* Metric Value */
        color: #f3f4f6; font-size: 1.9em; font-weight: 600;
    }
    .stMetric > div > div:nth-child(3) { /* Metric Delta */
        font-size: 0.9em; font-weight: 500;
    }
    .stMetric [data-testid="stMetricDelta"] svg { visibility: visible !important; } /* Ensure delta arrow is visible */

    /* --- Main Buttons --- */
    .stDownloadButton>button {
        background-color: #10b981; color: white !important; border: none; border-radius: 6px;
        font-weight: 500; padding: 10px 22px; font-size: 0.95em;
    }
    .stDownloadButton>button:hover { background-color: #059669; }

    /* --- Alert Messages --- */
    div[data-testid="stAlert"] { border-radius: 6px; border-width: 1px; border-style: solid; padding: 12px 15px; font-size: 0.9em;}
    div[data-testid="stAlert"][data-baseweb="alert-success"] { background-color: rgba(16, 185, 129, 0.15); border-color: #10b981; color: #a7f3d0; }
    div[data-testid="stAlert"][data-baseweb="alert-success"] svg { fill: #a7f3d0; }
    div[data-testid="stAlert"][data-baseweb="alert-info"] { background-color: rgba(59, 130, 246, 0.15); border-color: #3b82f6; color: #bfdbfe; }
    div[data-testid="stAlert"][data-baseweb="alert-info"] svg { fill: #bfdbfe; }
    div[data-testid="stAlert"][data-baseweb="alert-warning"] { background-color: rgba(245, 158, 11, 0.15); border-color: #f59e0b; color: #fde68a; }
    div[data-testid="stAlert"][data-baseweb="alert-warning"] svg { fill: #fde68a; }
    div[data-testid="stAlert"][data-baseweb="alert-error"] { background-color: rgba(239, 68, 68, 0.15); border-color: #ef4444; color: #fecaca; }
    div[data-testid="stAlert"][data-baseweb="alert-error"] svg { fill: #fecaca; }

    /* --- Dataframe Styling Wrappers --- */
    .stDataFrame { border: 1px solid #374151; border-radius: 6px; overflow: hidden; }
    /* Center HTML tables rendered via st.markdown */
    div.stMarkdown > div[data-testid="element-container"] > div {
        display: flex; justify-content: center; width: 100%;
    }
    /* Add margin to HTML tables rendered via st.markdown */
    div.stMarkdown > div[data-testid="element-container"] > div > table {
        margin-bottom: 20px; /* Increased margin after table */
    }

    /* Hide Streamlit footer */
    .stApp > footer { visibility: hidden; }
    /* Custom horizontal rule */
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
    """Formats a start date into a 'Day Mon - Day Mon' week range string."""
    end_date = start_date + pd.Timedelta(days=6)
    return f"{start_date.day} {start_date.strftime('%b')} - {end_date.day} {end_date.strftime('%b')}"

def style_table(df_to_style): # NEW "3D/Elevated" Style
    """Applies custom styling to a Pandas DataFrame for HTML display."""
    numeric_cols = df_to_style.select_dtypes(include=np.number).columns.tolist()
    text_color_light = "#c7d2fe"; text_color_faint = "#6b7280"
    bg_base = "#1e293b"; bg_header_gradient_start = "#334155"; bg_header_gradient_end = "#2a364a"
    bg_index_cols = "#1a2332"; bg_net_cashflow = "#334155" # Slightly darker than header for emphasis
    border_color_soft = "rgba(71, 85, 105, 0.5)"; shadow_light = "rgba(200, 200, 255, 0.05)"; shadow_dark = "rgba(0, 0, 0, 0.2)"

    # Define column widths (adjust as needed)
    data_col_min_width = '110px'
    index_col_party_type_width = '100px'
    index_col_party_name_width = '120px'
    index_col_week_range_literal_width = '90px' # For index name 'week_range' if it were one

    styled_df = df_to_style.style.format(
        # Format numbers with commas, show '-' for zero
        lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) and x != 0 else ("-" if isinstance(x, (int, float)) and x == 0 else x),
        na_rep="-" # Represent NaNs as '-'
    ) \
        .set_caption(f"<span style='font-size: 1.1em; font-weight:500; color: {text_color_light}; display:block; margin-bottom:10px; text-align:center;'>📋 Weekly Cashflow Breakdown</span>") \
        .set_properties(**{
            'font-size': '9.5pt', 'border': 'none', # Individual cell borders handled by set_table_styles
            'font-family': "'Inter', 'Segoe UI', sans-serif", 'color': text_color_light,
            'width': 'auto', 'margin-left': 'auto', 'margin-right': 'auto', # Center table
            'border-radius': '8px', 'box-shadow': f'5px 5px 10px {shadow_dark}, -2px -2px 5px {shadow_light}',
            'background-color': bg_base, 'overflow': 'hidden' # Ensure border-radius clips content
        }) \
        .set_table_styles([
            # General table layout
            {'selector': '', 'props': [('border-collapse', 'separate'), ('border-spacing', '0px'), ('width', 'auto'), ('min-width', '65%'), ('max-width', '90%')]},
            {'selector': 'caption', 'props': [('caption-side', 'top'), ('padding-top', '10px')]}, # Padding above caption
            # All header cells (th)
            {'selector': 'th', 'props': [('text-align', 'center'), ('vertical-align', 'middle'), ('padding', '12px 8px'), ('font-weight', '500'), ('font-size', '9.5pt'), ('color', text_color_light), ('border-bottom', f'1px solid {border_color_soft}')]},
            # Column headers and index names (top level headers)
            {'selector': 'th.col_heading, th.index_name', 'props': [('background', f'linear-gradient(to bottom, {bg_header_gradient_start}, {bg_header_gradient_end})'), ('border-right', f'1px solid {border_color_soft}')]},
            {'selector': 'th.col_heading:last-child, th.index_name:last-child', 'props': [('border-right', 'none')]}, # No right border on last header
            # Specific width for data column headers
            {'selector': 'th.col_heading', 'props': [('min-width', data_col_min_width), ('max-width', data_col_min_width)]},
             # Width for the 'Week Range' literal header if index is named 'week_range' (for pivot index name)
            {'selector': 'th.index_name', 'props': [('min-width', index_col_week_range_literal_width), ('max-width', index_col_week_range_literal_width)]},
            # Row headers (index cells)
            {'selector': 'th.row_heading', 'props': [('background-color', bg_index_cols), ('border-right', f'1px solid {border_color_soft}')]},
            {'selector': 'th.row_heading.level0', 'props': [('font-weight', '500'), ('color', '#a5b4fc'), ('min-width', index_col_party_type_width), ('max-width', index_col_party_type_width)]}, # Party Type
            {'selector': 'th.row_heading.level1', 'props': [('min-width', index_col_party_name_width), ('max-width', index_col_party_name_width)]}, # Party Name
            # Data cells (td)
            {'selector': 'td', 'props': [('background-color', bg_base), ('text-align', 'center'), ('vertical-align', 'middle'), ('padding', '12px 8px'), ('border-bottom', f'1px solid {border_color_soft}'), ('border-right', f'1px solid {border_color_soft}'), ('min-width', data_col_min_width), ('max-width', data_col_min_width)]},
            {'selector': 'td:last-child', 'props': [('border-right', 'none')]}, # No right border on last data cell in a row
            # Last row styling (remove bottom border)
            {'selector': 'tr:last-child td, tr:last-child th.row_heading', 'props': [('border-bottom', 'none')]},
        ])

    # Style for zero or NaN values (make them fainter)
    def color_zero_values(val):
        return f'color: {text_color_faint};' if (isinstance(val, (int,float)) and val == 0) or pd.isna(val) else f'color: {text_color_light};'

    data_cols_to_style = [col for col in df_to_style.columns if df_to_style[col].dtype in [np.int64, np.float64, 'int64', 'float64']] # More explicit
    if data_cols_to_style:
        styled_df = styled_df.applymap(color_zero_values, subset=pd.IndexSlice[:, data_cols_to_style])

    # Conditional background color for numeric values (heatmap-like)
    if numeric_cols: # Ensure there are numeric columns to style
        valid_numeric_cols_for_subset = [col for col in numeric_cols if col in df_to_style.columns]
        if valid_numeric_cols_for_subset: # Ensure subset is valid
            try:
                def highlight_cells_for_dark(s): # s is a Series (a column)
                    styles = [''] * len(s)
                    # Calculate max_abs_val for normalization, ignore NaNs
                    s_numeric = pd.to_numeric(s, errors='coerce').dropna()
                    if s_numeric.empty: return styles # No numeric values to style
                    max_abs_val = s_numeric.abs().max()
                    if pd.isna(max_abs_val) or max_abs_val == 0: max_abs_val = 1 # Avoid division by zero

                    for i, val_orig in s.items(): # Iterate over original series to get original index
                        idx_loc = s.index.get_loc(i) # Get positional index
                        val = pd.to_numeric(val_orig, errors='coerce')
                        if pd.isna(val): continue # Skip NaNs for styling

                        if val > 0:
                            opacity = min(0.4, 0.1 + (val / max_abs_val) * 0.3) # Scale opacity
                            styles[idx_loc] = f'background-color: rgba(34, 139, 34, {opacity:.2f}); box-shadow: inset 0 0 3px rgba(200,255,200,0.1);'
                        elif val < 0:
                            opacity = min(0.4, 0.1 + (abs(val) / max_abs_val) * 0.3) # Scale opacity
                            styles[idx_loc] = f'background-color: rgba(178, 34, 34, {opacity:.2f}); box-shadow: inset 0 0 3px rgba(255,200,200,0.1);'
                    return styles
                styled_df = styled_df.apply(highlight_cells_for_dark, subset=valid_numeric_cols_for_subset, axis=0)
            except Exception as e:
                st.warning(f"Could not apply custom cell highlights: {e}. This might be due to non-numeric data in expected numeric columns.")

    # Style the "Net Cashflow" row
    def style_net_cashflow_row(row):
        # Check if the row's name (index) matches the specific MultiIndex for "Net Cashflow"
        if row.name == ("Net Cashflow", ""): # Assuming Party Name is blank for Net Cashflow row
            return [f'font-weight: 500; background-color: {bg_net_cashflow}; color: {text_color_light}; font-size:10pt; text-align:center; vertical-align:middle; border-top: 2px solid {border_color_soft}; border-bottom:none; border-left:none; border-right:none;'] * len(row)
        return [''] * len(row) # Default no style
    styled_df = styled_df.apply(style_net_cashflow_row, axis=1)

    return styled_df

# --- Sidebar for Inputs ---
with st.sidebar:
    st.markdown("<h1>Inputs & Settings</h1>", unsafe_allow_html=True)
    st.markdown("---") # Visually separates sections
    with st.expander("📥 Download Sample Template", expanded=False):
        sample_data = pd.DataFrame({
            "Party Type": ["Supplier", "Customer", "Supplier", "Internal"],
            "Party Name": ["ABC Ltd", "XYZ Inc", "DEF Supplies", "Loan Repay"],
            "Due Date": ["2024-07-15", "2024-07-10", "2024-07-20", "2024-07-25"],
            "Expected Date": ["2024-07-20", "2024-07-14", "2024-07-22", "2024-07-25"],
            "Amount": [-10000, 12000, -5000, -2500]
        })
        # Ensure dates are strings in the format Excel expects for easy import
        sample_data["Due Date"] = pd.to_datetime(sample_data["Due Date"]).dt.strftime('%Y-%m-%d')
        sample_data["Expected Date"] = pd.to_datetime(sample_data["Expected Date"]).dt.strftime('%Y-%m-%d')
        st.download_button(
            label="Download Template CSV",
            data=sample_data.to_csv(index=False).encode('utf-8'),
            file_name="cashflow_template.csv",
            mime="text/csv",
            help="Use this template to structure your cashflow data. Ensure 'Amount' is numeric and dates are in YYYY-MM-DD format."
        )
    st.markdown("---")
    uploaded_file = st.file_uploader(
        "Upload Cashflow Data (CSV or Excel)",
        type=["csv", "xlsx"],
        help="Upload your CSV or Excel file with columns: Party Type, Party Name, Due Date, Expected Date, Amount."
    )
    st.markdown("---")
    st.caption("Developed with ❤️ by AI")

# --- Main Panel for Results ---
if uploaded_file:
    with st.spinner("🚀 Processing your file... Hold tight!"):
        try:
            # --- 1. File Load and Normalization ---
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file, sheet_name=0, engine='openpyxl') # Specify engine
            else:
                st.error("Unsupported file type. Please upload a CSV or XLSX file.")
                st.stop()

            st.success(f"File `{uploaded_file.name}` loaded successfully!")

            # Clean column names (remove BOM, strip whitespace, convert to lowercase)
            df.columns = df.columns.str.replace('\ufeff', '', regex=False).str.strip().str.lower()

            # --- 2. Data Validation ---
            required_cols = {"party type", "party name", "due date", "expected date", "amount"}
            missing_cols = required_cols - set(df.columns)
            if missing_cols:
                st.error(f"Missing required columns in the uploaded file: {', '.join(missing_cols)}. Please check the sample template.")
                st.stop()

            # Convert 'amount' to numeric, coercing errors
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            if df['amount'].isnull().any():
                st.warning("Some 'Amount' values were non-numeric and have been ignored (treated as NaN).")

            # Convert date columns to datetime, coercing errors
            for col in ["due date", "expected date"]:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                if df[col].isnull().any():
                    st.warning(f"Some '{col.title()}' values were not valid dates and have been ignored (treated as NaN).")

            # Drop rows with NaN in critical columns after conversion
            initial_row_count = len(df)
            df.dropna(subset=['amount', 'due date', 'expected date', 'party type', 'party name'], inplace=True) # Added party type/name
            if len(df) < initial_row_count:
                st.info(f"{initial_row_count - len(df)} rows were removed due to missing or invalid critical values (Amount, Dates, Party Type/Name).")

            if df.empty:
                st.error("No valid data remaining after processing. Please check your file content and format.")
                st.stop()

            # --- 3. Feature Engineering for Weekly Aggregation ---
            # Use the later of due date or expected date for allocation
            df["allocation date"] = df[["due date", "expected date"]].max(axis=1)
            # Determine the start of the week (Monday) for each allocation date
            df["week_start"] = df["allocation date"].dt.to_period("W").apply(lambda r: r.start_time)
            # Create a formatted week range string for display
            df["week_range"] = df["week_start"].apply(format_week_range)

            # Get unique sorted week ranges for consistent ordering in pivot table and charts
            unique_week_starts = sorted(df["week_start"].unique())
            all_week_ranges_sorted = [format_week_range(ws) for ws in unique_week_starts]

            st.success(f"Data validated: {df.shape[0]} rows are ready for forecasting.")
            st.divider()

            # --- 4. Key Metrics Section ---
            st.subheader("🚀 At a Glance: Forecast Summary")
            total_inflow = df[df['amount'] > 0]['amount'].sum()
            total_outflow_val = df[df['amount'] < 0]['amount'].sum() # This will be negative
            net_overall_cashflow = df['amount'].sum()

            forecast_start_week_display, forecast_end_week_display, num_forecast_weeks = "N/A", "N/A", 0
            if all_week_ranges_sorted:
                forecast_start_week_display = all_week_ranges_sorted[0]
                forecast_end_week_display = all_week_ranges_sorted[-1]
                num_forecast_weeks = len(all_week_ranges_sorted)

            cols1 = st.columns(3)
            cols1[0].metric(label="Total Inflow", value=f"{total_inflow:,.0f}", help="Sum of all positive cashflow amounts.")
            cols1[1].metric(label="Total Outflow", value=f"{total_outflow_val:,.0f}", help="Sum of all negative cashflow amounts. Displayed as a negative value.")

            delta_for_net, delta_color_for_net, help_text_net = None, "off", "Overall net change in cash position."
            if abs(total_outflow_val) > 0 : # If there is any outflow
                net_perc_of_outflow = (net_overall_cashflow / abs(total_outflow_val)) * 100 if abs(total_outflow_val) != 0 else 0
                delta_for_net = f"{net_perc_of_outflow:.1f}% vs Outflow Mag."
                delta_color_for_net = "normal" if net_overall_cashflow >= 0 else "inverse"
                help_text_net += f" Net cashflow ({net_overall_cashflow:,.0f}) is {net_perc_of_outflow:.1f}% of the magnitude of total outflow ({abs(total_outflow_val):,.0f})."
            elif net_overall_cashflow > 0: # Only inflows, no outflows
                delta_for_net, delta_color_for_net, help_text_net = "Pure Inflow", "normal", help_text_net + " All transactions are inflows."
            elif net_overall_cashflow == 0 and total_inflow == 0 and total_outflow_val == 0: # No transactions
                delta_for_net, help_text_net = "Zero Balance", help_text_net + " No cash movements recorded."
            # If net_overall_cashflow < 0 and total_outflow_val is 0, it implies an issue or only negative adjustments not captured as typical outflows.
            # The first condition (abs(total_outflow_val) > 0) would catch most scenarios with outflows.

            cols1[2].metric(label="Net Cashflow (Overall)", value=f"{net_overall_cashflow:,.0f}", delta=delta_for_net, delta_color=delta_color_for_net, help=help_text_net)

            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True) # Spacer

            cols2 = st.columns(3)
            cols2[0].metric(label="Forecast Start Week", value=forecast_start_week_display, help="The first week included in this forecast period.")
            cols2[1].metric(label="Forecast End Week", value=forecast_end_week_display, help="The last week included in this forecast period.")
            cols2[2].metric(label="No. of Forecast Weeks", value=str(num_forecast_weeks), help="Total number of unique weeks covered by the forecast.")
            st.divider()

            # --- 5. Data Preview ---
            with st.container(): # Using container for grouping
                st.subheader("📄 Uploaded Data Preview (First 5 Valid Rows)")
                st.dataframe(df[['party type', 'party name', 'due date', 'expected date', 'amount', 'allocation date', 'week_range']].head(), use_container_width=True, hide_index=True)
            st.divider()

            # --- 6. Prepare Pivot Table Data ---
            # Create a master list of all unique party type/name combinations and all unique week ranges
            all_parties = df[["party type", "party name"]].drop_duplicates().reset_index(drop=True)
            all_weeks_df = pd.DataFrame({"week_range": all_week_ranges_sorted})

            final_table = pd.DataFrame(columns=["No Data"]) # Initialize
            net_cashflow_series = pd.Series(dtype='float64') # Initialize

            if not all_parties.empty and not all_weeks_df.empty:
                # Cross join to ensure all parties are represented in all weeks
                all_cross = pd.merge(all_parties, all_weeks_df, how="cross")
                # Group actual data by party and week
                grouped = df.groupby(["party type", "party name", "week_range"], as_index=False)["amount"].sum()
                # Merge with the cross join to fill in zeros for missing party/week combinations
                complete_df = pd.merge(all_cross, grouped, on=["party type", "party name", "week_range"], how="left").fillna(0)
            else: # Handle case where there might be no parties or no weeks (e.g., after filtering)
                complete_df = pd.DataFrame(columns=["party type", "party name", "week_range", "amount"])


            if not complete_df.empty:
                # Ensure 'week_range' is categorical for correct pivot table column order
                complete_df['week_range'] = pd.Categorical(complete_df['week_range'], categories=all_week_ranges_sorted, ordered=True)

                pivot_table = complete_df.pivot_table(
                    index=["party type", "party name"],
                    columns="week_range",
                    values="amount",
                    aggfunc="sum",
                    fill_value=0, # Fill missing party/week amounts with 0
                    dropna=False    # Keep all weeks even if a party has no transactions
                )

                if not pivot_table.empty:
                    # Calculate net cashflow for each week
                    net_cashflow_series = pivot_table.sum(numeric_only=True) # Sums each column (week)
                    # Create a DataFrame for the net cashflow row with a MultiIndex
                    net_row_df = pd.DataFrame([net_cashflow_series], index=pd.MultiIndex.from_tuples([("Net Cashflow", "")])) # Party Name level is blank
                    net_row_df.index.names = ["party type", "party name"] # Match index names for concat
                    # Append net cashflow row to the pivot table
                    final_table = pd.concat([pivot_table, net_row_df])
            
            # --- 7. Main Forecast Display Area ---
            with st.container():
                st.subheader("📊 Detailed Weekly Cashflow Forecast")
                if not final_table.empty and "No Data" not in final_table.columns:
                    # Display the styled table
                    st.markdown(style_table(final_table).to_html(), unsafe_allow_html=True)

                    # Chart Theming Variables
                    chart_bg_color = '#121212'       # Match page background
                    view_bg_color = '#121212'        # Match page background for view property
                    chart_text_color = '#9ca3af'     # Subdued text color for axes/labels
                    grid_color = '#374151'           # Grid line color
                    positive_color = '#10b981'       # Green for positive cashflow
                    negative_color = '#ef4444'       # Red for negative cashflow
                    bar_label_color = '#f3f4f6'      # Bright color for text on bars
                    text_color_light_for_title = "#d1d5db" # Brighter text for titles

                    # --- Weekly Net Cashflow Trend Chart ---
                    if not net_cashflow_series.empty:
                        net_df = net_cashflow_series.reset_index()
                        net_df.columns = ["Week Range", "Net Cashflow"]

                        if not net_df.empty and not net_df["Net Cashflow"].isnull().all():
                            # Ensure 'Week Range' is categorical for correct Altair chart sorting
                            net_df["Week Range"] = pd.Categorical(net_df["Week Range"], categories=all_week_ranges_sorted, ordered=True)
                            net_df = net_df.sort_values("Week Range") # Sort by the categorical order

                            bars = alt.Chart(net_df).mark_bar(
                                cornerRadiusTopLeft=2, cornerRadiusTopRight=2, size=20 # Bar appearance
                            ).encode(
                                x=alt.X("Week Range:N", sort=None, title="Week", axis=alt.Axis(labelAngle=-45, labelFontSize=8, titleFontSize=10, titleColor=chart_text_color, labelColor=chart_text_color, domainColor=grid_color, tickColor=grid_color, gridColor=grid_color, format='%d %b')), # Nominal, use pre-sorted order
                                y=alt.Y("Net Cashflow:Q", title="Net Cashflow ($)", axis=alt.Axis(labelFontSize=8, titleFontSize=10, titleColor=chart_text_color, labelColor=chart_text_color, domainColor=grid_color, tickColor=grid_color, gridColor=grid_color, format="~s")), # Quantitative, SI prefix format
                                color=alt.condition(
                                    alt.datum["Net Cashflow"] >= 0,
                                    alt.value(positive_color),  # Positive values
                                    alt.value(negative_color)   # Negative values
                                ),
                                tooltip=[
                                    alt.Tooltip("Week Range:N", title="Week"),
                                    alt.Tooltip("Net Cashflow:Q", title="Amount", format=",.0f") # Formatted tooltip
                                ]
                            ).properties(
                                title=alt.TitleParams(text="📈 Weekly Net Cashflow Trend", anchor='middle', fontSize=14, fontWeight=500, color=text_color_light_for_title, dy=-10)
                            )

                            # Add text labels on bars
                            text_labels = bars.mark_text(
                                align="center",
                                baseline="middle",
                                dy=alt.expr("datum['Net Cashflow'] >= 0 ? -8 : 8"), # Adjust position based on value
                                fontSize=8,
                                fontWeight=400
                            ).encode(
                                text=alt.Text("Net Cashflow:Q", format=",.0f"), # Formatted text
                                color=alt.value(bar_label_color)
                            )

                            chart = (bars + text_labels).properties(
                                height=300,
                                background=chart_bg_color
                            ).configure_view(
                                strokeOpacity=0, # No border around the chart view
                                fill=view_bg_color  # Background of the chart plotting area
                            ).configure_axis(
                                gridColor=grid_color,
                                gridOpacity=0.2 # Fainter grid lines
                            )
                            st.altair_chart(chart, use_container_width=True)
                    
                    st.divider()
                    # --- Summarized Totals by Party Type ---
                    st.subheader(" summarized Totals by Party Type")
                    if not df.empty:
                        summary_by_type = df.groupby("party type")["amount"].sum().reset_index()
                        summary_by_type.columns = ["Party Type", "Total Amount"]

                        # Specific handling for "customer" and "supplier" (case-insensitive)
                        customers_total = summary_by_type[summary_by_type["Party Type"].str.lower().str.contains("customer", case=False)]["Total Amount"].sum()
                        suppliers_total = summary_by_type[summary_by_type["Party Type"].str.lower().str.contains("supplier", case=False)]["Total Amount"].sum()
                        
                        # Other party types (not customer or supplier)
                        other_types_summary = summary_by_type[
                            ~summary_by_type["Party Type"].str.lower().str.contains("customer|supplier", case=False, regex=True)
                        ]

                        col_summary1, col_summary2 = st.columns(2)
                        with col_summary1:
                            st.metric(label="TOTAL FROM CUSTOMERS", value=f"{customers_total:,.0f}")
                        with col_summary2:
                            st.metric(label="TOTAL TO SUPPLIERS", value=f"{suppliers_total:,.0f}")
                        
                        if not other_types_summary.empty:
                            st.markdown("##### Other Party Type Totals:")
                            for _, row in other_types_summary.iterrows():
                                st.markdown(f"- **{row['Party Type']}**: {row['Total Amount']:,.0f}")
                            st.caption("Positive amounts indicate net inflow from that party type; negative amounts indicate net outflow.")

                        # Data for summary chart
                        chart_summary_data = []
                        if customers_total != 0: chart_summary_data.append({"Party Type": "Customers", "Amount": customers_total, "Flow": "Inflow"})
                        if suppliers_total != 0: chart_summary_data.append({"Party Type": "Suppliers", "Amount": suppliers_total, "Flow": "Outflow"}) # Suppliers are typically outflows
                        for _, row in other_types_summary.iterrows():
                            chart_summary_data.append({"Party Type": row["Party Type"], "Amount": row["Total Amount"], "Flow": "Inflow" if row["Total Amount"] >=0 else "Outflow"})
                        
                        if chart_summary_data:
                            summary_chart_df = pd.DataFrame(chart_summary_data)
                            if not summary_chart_df.empty and not summary_chart_df["Amount"].isnull().all():
                                summary_bars = alt.Chart(summary_chart_df).mark_bar(size=30).encode(
                                    x=alt.X('Amount:Q', title='Total Amount ($)', axis=alt.Axis(labelFontSize=9, titleFontSize=10, titleColor=chart_text_color, labelColor=chart_text_color, domainColor=grid_color, tickColor=grid_color, gridColor=grid_color, format="~s")),
                                    y=alt.Y('Party Type:N', sort='-x', title='Party Type', axis=alt.Axis(labelFontSize=9, titleFontSize=10, titleColor=chart_text_color, labelColor=chart_text_color, domainColor=grid_color, tickColor=grid_color)),
                                    color=alt.condition(alt.datum.Amount >= 0, alt.value(positive_color), alt.value(negative_color)),
                                    tooltip=['Party Type', alt.Tooltip('Amount:Q', format=',.0f')]
                                ).properties(
                                    title=alt.TitleParams(text="📊 Summary by Party Type", anchor='middle', fontSize=14, fontWeight=500, color=text_color_light_for_title, dy=-5),
                                    height=alt.Step(40), # Bar height adjusts with number of categories
                                    background=chart_bg_color
                                ).configure_view(
                                    strokeOpacity=0, fill=view_bg_color
                                ).configure_axis(
                                    gridColor=grid_color, gridOpacity=0.2
                                )
                                st.altair_chart(summary_bars, use_container_width=True)
                    else:
                        st.info("No base data available to generate Client/Supplier summary.")

                    # --- 8. Export Forecast ---
                    st.divider()
                    st.subheader("📤 Export Forecast")
                    towrite = BytesIO()
                    export_table = final_table.copy() # Work with a copy
                    # If index is MultiIndex, reset it to make Party Type and Party Name actual columns for export
                    if isinstance(export_table.index, pd.MultiIndex):
                        export_table = export_table.reset_index()

                    with pd.ExcelWriter(towrite, engine="xlsxwriter") as writer:
                        export_table.to_excel(writer, sheet_name="Cashflow Forecast", index=False)
                        workbook  = writer.book
                        worksheet = writer.sheets["Cashflow Forecast"]

                        # Header format
                        header_format = workbook.add_format({
                            'bold': True, 'text_wrap': True, 'valign': 'top',
                            'fg_color': '#334155', 'font_color': '#FFFFFF', # Dark header, light text
                            'border': 1, 'border_color': '#4b5563'
                        })
                        # Apply header format
                        for col_num, value in enumerate(export_table.columns.values):
                            worksheet.write(0, col_num, value, header_format)
                        
                        # Set column widths (approximate)
                        worksheet.set_column(0, 0, 20) # Party Type
                        worksheet.set_column(1, 1, 25) # Party Name
                        if len(export_table.columns) > 2:
                             worksheet.set_column(2, len(export_table.columns) -1 , 18) # Week columns

                        # Money format for numeric columns (excluding party type/name)
                        money_format = workbook.add_format({'num_format': '#,##0', 'font_color': text_color_light, 'bg_color': bg_base, 'border':1, 'border_color': border_color_soft})
                        # Net cashflow row format
                        net_cashflow_row_format = workbook.add_format({'num_format': '#,##0', 'bold': True, 'font_color': text_color_light, 'bg_color': bg_net_cashflow, 'border':1, 'border_color': border_color_soft, 'top_color': border_color_soft, 'top':2})


                        for row_num in range(len(export_table)):
                            is_net_cashflow_row = False
                            if "party type" in export_table.columns and export_table.iloc[row_num]["party type"] == "Net Cashflow":
                                is_net_cashflow_row = True

                            for col_idx, col_name in enumerate(export_table.columns):
                                cell_value = export_table.iloc[row_num, col_idx]
                                current_format = money_format
                                if is_net_cashflow_row:
                                    current_format = net_cashflow_row_format

                                is_party_col = col_name.lower() in ["party type", "party name"]
                                if not is_party_col and pd.api.types.is_number(cell_value):
                                    worksheet.write_number(row_num + 1, col_idx, cell_value, current_format)
                                else: # Text columns or other types
                                    text_format_props = {'font_color': text_color_light, 'bg_color': bg_base, 'border':1, 'border_color': border_color_soft}
                                    if is_net_cashflow_row and is_party_col: # Special for "Net Cashflow" label cells
                                        text_format_props['bg_color'] = bg_net_cashflow
                                        text_format_props['bold'] = True
                                        text_format_props['top'] = 2
                                        text_format_props['top_color'] = border_color_soft
                                    
                                    cell_text_format = workbook.add_format(text_format_props)
                                    if pd.isna(cell_value): cell_value = "" # Handle NaN for text cells
                                    worksheet.write_string(row_num + 1, col_idx, str(cell_value), cell_text_format)


                    st.download_button(
                        label="Download Forecast as Excel",
                        data=towrite.getvalue(),
                        file_name="cashflow_forecast.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.info("ℹ️ No forecast table to display. This might be due to no data after filtering or an issue in processing.")

        except pd.errors.ParserError:
            st.error("❌ Error parsing the uploaded file. Please ensure it's a valid CSV or Excel file.")
        except ImportError as ie:
            if "matplotlib" in str(ie).lower():
                st.error("❌ A required library (matplotlib) for styling might be missing. If you are running this locally, please install it: `pip install matplotlib`.")
            elif "openpyxl" in str(ie).lower():
                 st.error("❌ A required library (openpyxl) for reading Excel files is missing. If you are running this locally, please install it: `pip install openpyxl`.")
            else:
                st.error(f"An import error occurred: {ie}. Some functionalities might be affected.")
            st.exception(ie) # Provide full traceback for debugging
        except Exception as e:
            st.error(f"An unexpected error occurred during processing: {e}")
            st.exception(e) # Provide full traceback for debugging

else:
    # --- Initial Landing Page Content ---
    st.info("👈 **Upload your cashflow file using the sidebar to get started!**")
    st.markdown("---")
    with st.expander("💡 How to Use This Dashboard", expanded=True):
        st.markdown("""
            Welcome to your interactive Weekly Cashflow Forecast Dashboard! This tool helps you visualize your projected financial health based on your uploaded data.

            #### **Steps to Get Started:**
            1.  **📥 Prepare Your Data:**
                *   Ensure your data is in a CSV or Excel (`.xlsx`) file.
                *   The file must contain the following columns (case-insensitive headers):
                    *   `Party Type` (e.g., Customer, Supplier, Internal)
                    *   `Party Name` (e.g., Acme Corp, Vendor X)
                    *   `Due Date` (Transaction due date, format: YYYY-MM-DD or parsable by Pandas)
                    *   `Expected Date` (Transaction expected payment/receipt date, format: YYYY-MM-DD)
                    *   `Amount` (Numeric value; positive for inflows, negative for outflows)
                *   You can download a sample template from the sidebar to see the structure.

            2.  **📤 Upload Your File:**
                *   Use the file uploader in the sidebar to select your prepared CSV or Excel file.
                *   The dashboard will automatically process the data.

            3.  **📊 View & Analyze Results:**
                *   **At a Glance Metrics:** Key figures like total inflow, outflow, and net cashflow.
                *   **Detailed Weekly Forecast Table:** A breakdown of cashflows by party and week.
                *   **Weekly Net Cashflow Trend Chart:** A visual representation of net cashflow over time.
                *   **Summary by Party Type:** Aggregated totals for customers, suppliers, and other categories.

            4.  **💾 Download Forecast:**
                *   Export the detailed weekly forecast table to an Excel file for offline use or sharing.

            ---
            ✨ **Tips for Best Results:**
            *   Use consistent date formats (YYYY-MM-DD is recommended).
            *   Ensure the 'Amount' column contains only numeric values.
            *   Clearly distinguish between 'Party Type' (e.g., "Customer") and 'Party Name' (e.g., "Specific Customer Inc.").
            ---
            If you encounter any issues, double-check your file format against the sample template and ensure all required columns are present with valid data.
            """)
    st.balloons()
