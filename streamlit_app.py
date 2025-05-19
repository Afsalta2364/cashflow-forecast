# --- Main Panel for Results ---
if uploaded_file:
    with st.spinner("🚀 Processing your file... Hold tight!"):
        try:
            # ... (File loading, validation, data processing logic - SAME AS PREVIOUS) ...
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
            initial_row_count = len(df)
            df.dropna(subset=['amount', 'due date', 'expected date'], inplace=True)
            if len(df) < initial_row_count: st.info(f"{initial_row_count - len(df)} rows removed due to missing/invalid critical values.")
            if df.empty: st.error("No valid data remaining after processing."); st.stop()
            df["allocation date"] = df[["due date", "expected date"]].max(axis=1)
            df["week_start"] = df["allocation date"].dt.to_period("W").apply(lambda r: r.start_time)
            df["week_range"] = df["week_start"].apply(format_week_range)
            unique_week_starts = sorted(df["week_start"].unique())
            all_week_ranges_sorted = [format_week_range(ws) for ws in unique_week_starts]
            st.success(f"Data validated: {df.shape[0]} rows ready for forecasting.")
            st.divider()

            # --- Key Metrics Section (SAME AS PREVIOUS) ---
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

            # --- Data Preview (SAME AS PREVIOUS) ---
            with st.container():
                st.subheader("📄 Uploaded Data Preview (First 5 Valid Rows)")
                st.dataframe(df.head(), use_container_width=True, hide_index=True)
            st.divider()

            # --- Prepare Pivot Table Data (SAME AS PREVIOUS) ---
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
                net_cashflow_series = pivot_table.sum(numeric_only=True) # Used for chart conditional rendering
                net_row = pd.DataFrame([net_cashflow_series], index=pd.MultiIndex.from_tuples([("Net Cashflow", "")]))
                final_table = pd.concat([pivot_table, net_row])
            else: 
                final_table = pd.DataFrame(columns=["No Data"])
                net_cashflow_series = pd.Series(dtype='float64') # Ensure it exists as empty for checks

            # --- Main Forecast Display Area (WITH CONDITIONAL CHART RENDERING) ---
            with st.container():
                st.subheader("📊 Detailed Weekly Cashflow Forecast")
                if not final_table.empty and "No Data" not in final_table.columns:
                    st.markdown(style_table(final_table).to_html(), unsafe_allow_html=True)
                    # No <br> here

                    chart_bg_color = '#121212'; view_bg_color = '#121212'
                    chart_text_color = '#9ca3af'; grid_color = '#374151'
                    positive_color = '#10b981'; negative_color = '#ef4444'
                    bar_label_color = '#f3f4f6'; text_color_light_for_title = "#d1d5db"

                    if not net_cashflow_series.empty:
                        net_df = net_cashflow_series.reset_index()
                        net_df.columns = ["Week Range", "Net Cashflow"]
                        if not net_df.empty: # Further check if DataFrame is not empty
                            net_df["Week Range"] = pd.Categorical(net_df["Week Range"], categories=all_week_ranges_sorted, ordered=True)
                            net_df = net_df.sort_values("Week Range")
                            
                            bars = alt.Chart(net_df).mark_bar(cornerRadiusTopLeft=2, cornerRadiusTopRight=2, size=20).encode(
                                x=alt.X("Week Range:N", sort=None, title="Week",
                                        axis=alt.Axis(labelAngle=-45, labelFontSize=8, titleFontSize=10, titleColor=chart_text_color, labelColor=chart_text_color, domainColor=grid_color, tickColor=grid_color, gridColor=grid_color, format='%d %b')),
                                y=alt.Y("Net Cashflow:Q", title="Net Cashflow ($)",
                                        axis=alt.Axis(labelFontSize=8, titleFontSize=10, titleColor=chart_text_color, labelColor=chart_text_color, domainColor=grid_color, tickColor=grid_color, gridColor=grid_color, format="~s")),
                                color=alt.condition(alt.datum["Net Cashflow"] >= 0, alt.value(positive_color), alt.value(negative_color)),
                                tooltip=[alt.Tooltip("Week Range:N", title="Week"), alt.Tooltip("Net Cashflow:Q", title="Amount", format=",.0f")]
                            ).properties(title=alt.TitleParams(text="📈 Weekly Net Cashflow Trend", anchor='middle', fontSize=14, fontWeight=500, color=text_color_light_for_title, dy=-10))
                            text_labels = bars.mark_text(align="center", baseline="middle", dy=alt.expr("datum['Net Cashflow'] >= 0 ? -8 : 8"), fontSize=8, fontWeight=400).encode(
                                text=alt.Text("Net Cashflow:Q", format=",.0f"), color=alt.value(bar_label_color))
                            chart = (bars + text_labels).properties(height=300, background=chart_bg_color).configure_view(
                                strokeOpacity=0, fill=view_bg_color ).configure_axis( gridColor=grid_color, gridOpacity=0.2 ) # or grid=False
                            st.altair_chart(chart, use_container_width=True)
                        # else: # Optionally, if net_df became empty after reset (unlikely if net_cashflow_series wasn't empty)
                        #    st.caption("No data points for Net Cashflow chart after processing.")
                    # else: # If net_cashflow_series itself was empty
                    #    st.caption("No data available for Net Cashflow chart.")
                    
                    st.divider()
                    st.subheader(" summarized Totals by Party Type")
                    if not df.empty: # Original df for summary
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
                            for _, row in other_types_summary.iterrows(): st.markdown(f"- **{row['Party Type']}**: {row['Total Amount']:,.0f}")
                            st.caption("Positive: net inflow, Negative: net outflow.")

                        chart_summary_data = []
                        if customers_total != 0: chart_summary_data.append({"Party Type": "Customers", "Amount": customers_total, "Flow": "Inflow"})
                        if suppliers_total != 0: chart_summary_data.append({"Party Type": "Suppliers", "Amount": suppliers_total, "Flow": "Outflow"})
                        for _, row in other_types_summary.iterrows(): chart_summary_data.append({"Party Type": row["Party Type"], "Amount": row["Total Amount"], "Flow": "Inflow" if row["Total Amount"] >=0 else "Outflow"})
                        
                        if chart_summary_data:
                            summary_chart_df = pd.DataFrame(chart_summary_data)
                            if not summary_chart_df.empty:
                                summary_bars = alt.Chart(summary_chart_df).mark_bar(size=30).encode(
                                    x=alt.X('Amount:Q', title='Total Amount ($)', axis=alt.Axis(labelFontSize=9, titleFontSize=10, titleColor=chart_text_color, labelColor=chart_text_color, domainColor=grid_color, tickColor=grid_color, gridColor=grid_color, format="~s")),
                                    y=alt.Y('Party Type:N', sort='-x', title='Party Type', axis=alt.Axis(labelFontSize=9, titleFontSize=10, titleColor=chart_text_color, labelColor=chart_text_color, domainColor=grid_color, tickColor=grid_color)),
                                    color=alt.condition(alt.datum.Amount >= 0, alt.value(positive_color), alt.value(negative_color)),
                                    tooltip=['Party Type', alt.Tooltip('Amount:Q', format=',.0f')]
                                ).properties(title=alt.TitleParams(text="📊 Summary by Party Type", anchor='middle', fontSize=14, fontWeight=500, color=text_color_light_for_title, dy=-5),
                                             height=alt.Step(40), background=chart_bg_color ).configure_view(strokeOpacity=0, fill=view_bg_color).configure_axis(gridColor=grid_color, gridOpacity=0.2) # or grid=False
                                st.altair_chart(summary_bars, use_container_width=True)
                            # else: # Optionally handle if summary_chart_df is empty
                            #    st.caption("No data points for Party Type Summary chart after processing.")
                        # else: # If chart_summary_data list was empty
                        #    st.caption("No data available for Party Type Summary chart.")
                    else: st.info("No base data for Client/Supplier summary.")

                    st.divider()
                    st.subheader("📤 Export Forecast")
                    # ... (Export logic - SAME AS PREVIOUS) ...
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
                    st.download_button(label="Download Forecast as Excel", data=towrite.getvalue(), file_name="cashflow_forecast.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                else: st.info("ℹ️ No forecast table to display.")
        # ... (Exception handling - SAME AS PREVIOUS) ...
        except pd.errors.ParserError: st.error("❌ Error parsing the uploaded file.")
        except ImportError as ie:
            if "matplotlib" in str(ie).lower(): st.error("❌ Matplotlib is missing. Install with `pip install matplotlib`.")
            else: st.error(f"Import error: {ie}.")
            st.exception(ie)
        except Exception as e:
            st.error(f"An unexpected error occurred during processing.")
            st.exception(e)
else:
    # ... (Welcome message - SAME AS PREVIOUS) ...
    st.info("👈 **Upload your cashflow file using the sidebar to get started!**")
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
