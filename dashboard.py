import streamlit as st
import pandas as pd
import plotly.express as px
from preprocess import read_and_process_file
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import numpy as np
import datetime
import streamlit as st
from io import BytesIO

def show_dashboard():
    theme_mode = st.sidebar.radio("Choose Theme", ["Light", "Dark"])
    if theme_mode == "Dark":
            st.markdown("""
            <style>
            .stApp {
                background-color: #0e1117;
                color: white;
            }
            .stMarkdown, .css-1v3fvcr {
                color: white !important;
            }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            .stApp {
                background-color: #f3f6f9;
                color: #212121;
            }
            </style>
        """, unsafe_allow_html=True)

    # --- Header Row with Logo and Time ---
    col1, col2 = st.columns([1, 3])

    with col1:
        try:
            st.image(r'assets\xcmg-logo.png', width=250)  # Adjust size as needed
        except:
            st.warning("⚠️ Logo not found. Please upload 'logo.png' to assets folder.")

    with col2:
        now = datetime.datetime.now()
        st.markdown(f"""
            <div style='text-align:right; font-size:20px; padding-top:10px;'>
                📅 <b>{now.strftime('%A, %d %B %Y')}</b><br>
                🕒 <span id="clock">{now.strftime('%H:%M:%S')}</span>
            </div>
        """, unsafe_allow_html=True)

        # Optional: Update clock using JavaScript (optional, not reactive on change)
        st.markdown("""
            <script>
            setInterval(() => {
                const now = new Date();
                document.getElementById("clock").textContent =
                    now.toLocaleTimeString();
            }, 1000);
            </script>
        """, unsafe_allow_html=True)

    st.markdown("## 🏭 Industrial Energy Management System")
            
    # 🌈 Custom CSS for styling
    st.markdown("""
        <style>
        body {
            background-color: #f0f2f6;
            font-family: 'Segoe UI', sans-serif;
        }
        .stApp {
            padding: 10px;
        }
        h2, h3 {
            color: #003366;
        }
        div[data-testid="stSidebar"] {
            background-color: #e8f0fe;
        }
        </style>
    """, unsafe_allow_html=True)
    
    
    uploaded_file = st.file_uploader("📁 Upload your industry sheet", type=["csv", "xlsx", "json", "txt"])
    
    if uploaded_file:
        df, error = read_and_process_file(uploaded_file)
        if error:
            st.error(error)
        elif df is not None:
           # Prepare filtered device list early
            filtered_device_list = [
                d for d in sorted(df["Device"].unique())
                if d.lower() not in ["sno", "s.no", "s. no.", "serial", "c", "cwk"]
                and "water" not in d.lower()
            ]

            # Filters section
            with st.sidebar:
                st.header(":mag: Filters")
                selected_device = st.selectbox("Select Device", ["All"] + filtered_device_list)
                date_range = st.date_input("Date Range", [])

            filtered_df = df.copy()
            if selected_device != "All":
                filtered_df = filtered_df[filtered_df["Device"] == selected_device]
            if len(date_range) == 2:
                start, end = date_range
                filtered_df = filtered_df[
                    (filtered_df["Timestamp"].dt.date >= start) & 
                    (filtered_df["Timestamp"].dt.date <= end)
                ]

            st.success("✅ Data processed successfully")
            st.dataframe(filtered_df)
    

        def convert_df_to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Processed Data')
            processed_data = output.getvalue()
            return processed_data

        excel_data = convert_df_to_excel(filtered_df)
        st.download_button(
            label="📥 Download Processed Excel",
            data=excel_data,
            file_name="processed_consumption.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


            # 📦 Energy Tiles
        st.markdown("### 🔋 Device Energy Overview")
        tiles = filtered_df.groupby("Device")["Consumption_kwh"].sum().reset_index()
        tiles = tiles[tiles["Consumption_kwh"] > 0]
        cols = st.columns(min(4, len(tiles)))
        for idx, row in tiles.iterrows():
            with cols[idx % len(cols)]:
                st.markdown(f"""
                    <div style='padding:20px; margin-bottom:24px; border-radius:10px; background:#f9f9f9;text-align:center; box-shadow:0 4px 8px rgba(0,0,0,0.1);transition:0.3s;'>
                        <h3 style='color:#0073e6'>{row["Device"]}</h3>
                        <h2 style='color:#28a745; font-size:30px'>{row["Consumption_kwh"]:.2f} kWh</h2>
                    </div>
                """, unsafe_allow_html=True)

        total_energy = filtered_df["Consumption_kwh"].sum()
        st.markdown(f"""
            <div style='margin-top:20px; padding:20px; background:#fff4e6; border-left:5px solid #ffa500;
                        border-radius:8px; font-size:18px;'>
                ⚡ <strong>Total Energy Consumption:</strong> <span style='color:#d35400;'>{total_energy:.2f} kWh</span>
            </div>
        """, unsafe_allow_html=True)

            
        # Chart
        # 📊 Charts
        st.markdown("### 📊 Energy Usage Visualizations")
        with st.expander("📊 Show/Hide Charts"):
            col1, col2 = st.columns(2)

            with col1:
                    show_line = st.checkbox("📈 Line Chart", value=True, key=f"line_chart_checkbox_inner_{selected_device}")
                    show_area = st.checkbox("📉 Area Chart", value=False, key=f"area_chart_checkbox_inner_{selected_device}")
                    show_daily = st.checkbox("📆 Daily Total Line Chart", value=False, key=f"daily_total_line_chart_checkbox_inner_{selected_device}")

            with col2:
                show_column = st.checkbox("📊 Column Chart", value=False, key=f"column_chart_checkbox_inner_{selected_device}")
                show_bar = st.checkbox("🔝 Top 5 Bar Chart", value=True, key=f"top5_bar_chart_checkbox_inner_{selected_device}")
                show_pie = st.checkbox("🥧 Pie Chart", value=False, key=f"pie_chart_checkbox_inner_{selected_device}")
                show_donut = st.checkbox("🍩 Donut Chart", value=False, key=f"donut_chart_checkbox_inner_{selected_device}")

                    # Show selected charts
            if show_line:
                fig_line = px.line(filtered_df, x="Timestamp", y="Consumption_kwh", color="Device",
                                   title="Line Chart: Energy Consumption Over Time", markers=True)
                st.plotly_chart(fig_line, use_container_width=True)

            if show_column:
                fig_column = px.bar(filtered_df, x="Timestamp", y="Consumption_kwh", color="Device",
                                    title="Column Chart: Hourly/Device Usage")
                st.plotly_chart(fig_column, use_container_width=True)

            if show_area:
                fig_area = px.area(filtered_df, x="Timestamp", y="Consumption_kwh", color="Device",
                                   title="Area Chart: Consumption Distribution")
                st.plotly_chart(fig_area, use_container_width=True)

            top_df = df[df["Device"].isin(filtered_device_list)]
            if show_bar:
                top_devices = top_df.groupby("Device")["Consumption_kwh"].sum().nlargest(5).reset_index()
                fig_bar = px.bar(top_devices, x="Device", y="Consumption_kwh", title="Bar Chart: Top 5 Devices")
                st.plotly_chart(fig_bar, use_container_width=True)

            pie_data = top_df.groupby("Device")["Consumption_kwh"].sum().reset_index()
            if show_pie:
                fig_pie = px.pie(pie_data, names="Device", values="Consumption_kwh", title="Pie Chart: Device Contribution %")
                st.plotly_chart(fig_pie, use_container_width=True)

            if show_donut:
                fig_donut = px.pie(pie_data, names="Device", values="Consumption_kwh", hole=0.4,
                                   title="Donut Chart: Device Contribution")
                st.plotly_chart(fig_donut, use_container_width=True)

            if show_daily:
                daily_total = df.groupby(df["Timestamp"].dt.date)["Consumption_kwh"].sum().reset_index()
                daily_total.columns = ["Date", "Consumption_kwh"]
                fig_daily_line = px.line(daily_total, x="Date", y="Consumption_kwh",
                                             title="Line Chart: Daily Total Consumption")
                st.plotly_chart(fig_daily_line, use_container_width=True)

        st.markdown("### 📈 Consumption Chart")
        fig = px.line(filtered_df, x="Timestamp", y="Consumption_kwh", color="Device", markers=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("### 🔝 Top 5 Consuming Devices")
        top_devices = filtered_df.groupby("Device")["Consumption_kwh"].sum().nlargest(5).reset_index()
        fig_top = px.bar(top_devices, x="Device", y="Consumption_kwh", title="Top 5 Devices")
        st.plotly_chart(fig_top, use_container_width=True)

        st.markdown("### 📆 Daily Total Consumption")
        daily = filtered_df.groupby(filtered_df["Timestamp"].dt.date)["Consumption_kwh"].sum().reset_index()
        fig_daily = px.line(daily, x="Timestamp", y="Consumption_kwh", title="Daily Total Consumption", markers=True)
        st.plotly_chart(fig_daily, use_container_width=True)

        st.markdown("### 🧯 Device Contribution (%)")
        device_pie = filtered_df.groupby("Device")["Consumption_kwh"].sum().reset_index()
        fig_pie = px.pie(device_pie, names="Device", values="Consumption_kwh", title="Device-wise Energy Contribution")
        st.plotly_chart(fig_pie, use_container_width=True)
            

            # ---------------------------------
            # 🔮 ML Prediction Section
            # ---------------------------------
        st.markdown("## 🔮 Predict Future Consumption")
        ml_df = filtered_df.copy()

        if ml_df.empty:
            st.warning("Not enough data for prediction.")
        else:
            ml_df["Day"] = ml_df["Timestamp"].dt.dayofyear
            ml_df["Device_encoded"] = LabelEncoder().fit_transform(ml_df["Device"])

            X = ml_df[["Day", "Device_encoded"]]
            y = ml_df["Consumption_kwh"]

            model = LinearRegression()
            model.fit(X, y)

            st.markdown("### 📆 Predict for how many future days?")
            future_days = st.slider("Days", 1, 30, 7, key="future_days_slider")

            last_day = ml_df["Day"].max()
            future_X = pd.DataFrame({
                "Day": np.arange(last_day + 1, last_day + future_days + 1),
                "Device_encoded": LabelEncoder().fit_transform([selected_device] * future_days) 
                                  if selected_device != "All" else [0] * future_days
            })

            predicted = model.predict(future_X)
            future_df = pd.DataFrame({
                "Day": future_X["Day"],
                "Predicted_Consumption_kwh": predicted
            })

            st.markdown("### 📈 Predicted Usage")
            st.line_chart(future_df.set_index("Day")["Predicted_Consumption_kwh"])
            st.dataframe(future_df)