import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import random
import time
from datetime import datetime, timedelta
import json

# Page configuration
st.set_page_config(
    page_title="Battery Management System",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .status-good { color: #28a745; font-weight: bold; }
    .status-warning { color: #ffc107; font-weight: bold; }
    .status-danger { color: #dc3545; font-weight: bold; }
    
    .sidebar-header {
        font-size: 1.3rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'cells_data' not in st.session_state:
    st.session_state.cells_data = {}
if 'bench_name' not in st.session_state:
    st.session_state.bench_name = ""
if 'group_num' not in st.session_state:
    st.session_state.group_num = 1
if 'historical_data' not in st.session_state:
    st.session_state.historical_data = []

# Sidebar for navigation and configuration
st.sidebar.markdown('<div class="sidebar-header">🔋 Battery Management System</div>', unsafe_allow_html=True)

page = st.sidebar.selectbox(
    "Navigate to:",
    ["🏠 Dashboard", "⚙️ Configuration", "📊 Analysis", "🎛️ Control Panel", "📈 Real-time Monitor"]
)

# Cell type configurations
CELL_CONFIGS = {
    "lfp": {"nominal": 3.2, "min": 2.8, "max": 3.6, "color": "#28a745"},
    "nmc": {"nominal": 3.6, "min": 3.2, "max": 4.0, "color": "#007bff"},
    "lto": {"nominal": 2.4, "min": 1.5, "max": 2.8, "color": "#ffc107"},
    "lco": {"nominal": 3.7, "min": 3.0, "max": 4.2, "color": "#dc3545"}
}

def get_cell_status(voltage, cell_type):
    """Determine cell status based on voltage"""
    config = CELL_CONFIGS.get(cell_type.lower(), CELL_CONFIGS["lfp"])
    if voltage < config["min"]:
        return "🔴 Critical", "status-danger"
    elif voltage > config["max"]:
        return "⚠️ Overcharged", "status-warning"
    elif config["min"] <= voltage <= config["max"]:
        return "✅ Normal", "status-good"
    else:
        return "⚠️ Warning", "status-warning"

def generate_mock_data(cell_type, base_voltage, base_current):
    """Generate realistic mock data for demonstration"""
    return {
        "voltage": round(base_voltage + random.uniform(-0.1, 0.1), 2),
        "current": round(base_current + random.uniform(-0.5, 0.5), 2),
        "temp": round(random.uniform(25, 45), 1),
        "timestamp": datetime.now()
    }

# Configuration Page
if page == "⚙️ Configuration":
    st.markdown('<div class="main-header">⚙️ System Configuration</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🏷️ System Information")
        bench_name = st.text_input("Bench Name:", value=st.session_state.bench_name, placeholder="e.g., Lab-Bench-A1")
        group_num = st.number_input("Group Number:", min_value=1, max_value=100, value=st.session_state.group_num)
        
        st.subheader("🔋 Default Cell Configuration")
        default_cell_type = st.selectbox("Default Cell Type:", list(CELL_CONFIGS.keys()), index=0)
        
        # Display cell type specifications
        config = CELL_CONFIGS[default_cell_type]
        st.info(f"""
        **{default_cell_type.upper()} Specifications:**
        - Nominal Voltage: {config['nominal']}V
        - Min Voltage: {config['min']}V  
        - Max Voltage: {config['max']}V
        """)
    
    with col2:
        st.subheader("📱 Cell Setup")
        num_cells = st.slider("Number of Cells:", min_value=1, max_value=16, value=8)
        
        cells_data = {}
        
        for i in range(num_cells):
            with st.expander(f"Cell {i+1} Configuration", expanded=False):
                col_a, col_b = st.columns(2)
                with col_a:
                    cell_type = st.selectbox(f"Type:", list(CELL_CONFIGS.keys()), 
                                           key=f"type_{i}", index=list(CELL_CONFIGS.keys()).index(default_cell_type))
                with col_b:
                    current = st.number_input(f"Current (A):", value=0.0, step=0.1, key=f"current_{i}")
                
                config = CELL_CONFIGS[cell_type]
                voltage = config["nominal"]
                capacity = round(voltage * current, 2)
                temp = round(random.uniform(25, 40), 1)
                
                cell_key = f"cell_{i+1}_{cell_type}"
                cells_data[cell_key] = {
                    "voltage": voltage,
                    "current": current,
                    "temp": temp,
                    "capacity": capacity,
                    "min_voltage": config["min"],
                    "max_voltage": config["max"],
                    "cell_type": cell_type
                }
        
        if st.button("💾 Save Configuration", type="primary"):
            st.session_state.cells_data = cells_data
            st.session_state.bench_name = bench_name
            st.session_state.group_num = group_num
            st.success("✅ Configuration saved successfully!")
            st.balloons()

# Dashboard Page
elif page == "🏠 Dashboard":
    st.markdown('<div class="main-header">🏠 Battery Management Dashboard</div>', unsafe_allow_html=True)
    
    if not st.session_state.cells_data:
        st.warning("⚠️ Please configure your battery system first in the Configuration tab.")
        st.stop()
    
    # System Overview
    col1, col2, col3, col4 = st.columns(4)
    
    cells_data = st.session_state.cells_data
    total_cells = len(cells_data)
    avg_voltage = np.mean([cell["voltage"] for cell in cells_data.values()])
    total_current = sum([cell["current"] for cell in cells_data.values()])
    avg_temp = np.mean([cell["temp"] for cell in cells_data.values()])
    
    with col1:
        st.metric("🔋 Total Cells", total_cells)
    with col2:
        st.metric("⚡ Avg Voltage", f"{avg_voltage:.2f}V")
    with col3:
        st.metric("🔌 Total Current", f"{total_current:.2f}A")
    with col4:
        st.metric("🌡️ Avg Temperature", f"{avg_temp:.1f}°C")
    
    st.markdown("---")
    
    # Cells Overview Table
    st.subheader("📊 Cells Status Overview")
    
    # Create DataFrame for display
    display_data = []
    for cell_name, data in cells_data.items():
        status, status_class = get_cell_status(data["voltage"], data["cell_type"])
        display_data.append({
            "Cell": cell_name,
            "Type": data["cell_type"].upper(),
            "Voltage (V)": data["voltage"],
            "Current (A)": data["current"],
            "Temperature (°C)": data["temp"],
            "Capacity (Wh)": data["capacity"],
            "Status": status
        })
    
    df = pd.DataFrame(display_data)
    st.dataframe(df, use_container_width=True)
    
    # Voltage Distribution Chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Voltage Distribution")
        fig = px.bar(
            df, 
            x="Cell", 
            y="Voltage (V)", 
            color="Type",
            title="Cell Voltage Comparison"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🌡️ Temperature Monitoring")
        fig = px.scatter(
            df, 
            x="Cell", 
            y="Temperature (°C)", 
            size="Current (A)",
            color="Type",
            title="Temperature vs Current"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

# Control Panel Page
elif page == "🎛️ Control Panel":
    st.markdown('<div class="main-header">🎛️ Control Panel</div>', unsafe_allow_html=True)
    
    if not st.session_state.cells_data:
        st.warning("⚠️ Please configure your battery system first.")
        st.stop()
    
    st.subheader("⚡ Real-time Cell Control")
    
    # Control interface for each cell
    cells_data = st.session_state.cells_data.copy()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        for cell_name, data in cells_data.items():
            with st.expander(f"🔋 {cell_name.replace('_', ' ').title()}", expanded=True):
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    new_voltage = st.slider(
                        "Voltage (V)", 
                        min_value=float(data["min_voltage"]), 
                        max_value=float(data["max_voltage"]), 
                        value=float(data["voltage"]),
                        step=0.1,
                        key=f"voltage_{cell_name}"
                    )
                
                with col_b:
                    new_current = st.slider(
                        "Current (A)", 
                        min_value=-10.0, 
                        max_value=10.0, 
                        value=float(data["current"]),
                        step=0.1,
                        key=f"current_{cell_name}"
                    )
                
                with col_c:
                    new_temp = st.slider(
                        "Temperature (°C)", 
                        min_value=0.0, 
                        max_value=60.0, 
                        value=float(data["temp"]),
                        step=0.5,
                        key=f"temp_{cell_name}"
                    )
                
                # Update values
                cells_data[cell_name]["voltage"] = new_voltage
                cells_data[cell_name]["current"] = new_current
                cells_data[cell_name]["temp"] = new_temp
                cells_data[cell_name]["capacity"] = round(new_voltage * new_current, 2)
                
                # Status indicator
                status, status_class = get_cell_status(new_voltage, data["cell_type"])
                st.markdown(f'<span class="{status_class}">{status}</span>', unsafe_allow_html=True)
    
    with col2:
        st.subheader("🎯 Quick Actions")
        
        if st.button("🔄 Apply Changes", type="primary"):
            st.session_state.cells_data = cells_data
            st.success("✅ Changes applied successfully!")
        
        if st.button("🔀 Randomize Values"):
            for cell_name, data in cells_data.items():
                config = CELL_CONFIGS[data["cell_type"]]
                cells_data[cell_name].update(generate_mock_data(
                    data["cell_type"], 
                    config["nominal"], 
                    data["current"]
                ))
            st.session_state.cells_data = cells_data
            st.rerun()
        
        if st.button("⚠️ Emergency Stop", type="secondary"):
            for cell_name in cells_data:
                cells_data[cell_name]["current"] = 0.0
                cells_data[cell_name]["capacity"] = 0.0
            st.session_state.cells_data = cells_data
            st.error("🛑 Emergency stop activated!")
        
        st.subheader("📊 System Status")
        total_power = sum([cell["capacity"] for cell in cells_data.values()])
        st.metric("Total Power", f"{total_power:.2f} Wh")
        
        # System health indicator
        healthy_cells = sum([1 for cell in cells_data.values() 
                           if get_cell_status(cell["voltage"], cell["cell_type"])[0] == "✅ Normal"])
        health_percentage = (healthy_cells / len(cells_data)) * 100
        
        st.metric("System Health", f"{health_percentage:.1f}%")
        
        if health_percentage >= 80:
            st.success("🟢 System Running Optimally")
        elif health_percentage >= 60:
            st.warning("🟡 System Needs Attention")
        else:
            st.error("🔴 Critical System Issues")

# Analysis Page
elif page == "📊 Analysis":
    st.markdown('<div class="main-header">📊 Battery Analysis</div>', unsafe_allow_html=True)
    
    if not st.session_state.cells_data:
        st.warning("⚠️ Please configure your battery system first.")
        st.stop()
    
    cells_data = st.session_state.cells_data
    
    # Advanced Analytics
    tab1, tab2, tab3 = st.tabs(["📈 Performance Analysis", "🔍 Cell Comparison", "📋 Reports"])
    
    with tab1:
        st.subheader("Performance Metrics")
        
        # Create performance DataFrame
        perf_data = []
        for cell_name, data in cells_data.items():
            efficiency = (data["voltage"] / CELL_CONFIGS[data["cell_type"]]["max"]) * 100
            power_density = data["capacity"] / data["temp"] if data["temp"] > 0 else 0
            
            perf_data.append({
                "Cell": cell_name,
                "Efficiency (%)": round(efficiency, 1),
                "Power Density": round(power_density, 3),
                "Energy Output": data["capacity"],
                "Temperature Factor": data["temp"]
            })
        
        perf_df = pd.DataFrame(perf_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.scatter(
                perf_df, 
                x="Efficiency (%)", 
                y="Power Density",
                size="Energy Output",
                hover_data=["Cell"],
                title="Efficiency vs Power Density"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.box(
                perf_df, 
                y="Efficiency (%)",
                title="Efficiency Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Cell-by-Cell Comparison")
        
        # Radar chart for multi-dimensional comparison
        selected_cells = st.multiselect(
            "Select cells to compare:",
            list(cells_data.keys()),
            default=list(cells_data.keys())[:4]
        )
        
        if selected_cells:
            fig = go.Figure()
            
            for cell_name in selected_cells:
                data = cells_data[cell_name]
                config = CELL_CONFIGS[data["cell_type"]]
                
                # Normalize values for radar chart
                values = [
                    (data["voltage"] / config["max"]) * 100,
                    min((data["current"] + 10) / 20 * 100, 100),  # Normalize current
                    (data["temp"] / 60) * 100,  # Normalize temperature
                    min((data["capacity"] + 10) / 20 * 100, 100),  # Normalize capacity
                ]
                
                fig.add_trace(go.Scatterpolar(
                    r=values + [values[0]],  # Close the polygon
                    theta=['Voltage', 'Current', 'Temperature', 'Capacity', 'Voltage'],
                    fill='toself',
                    name=cell_name
                ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )
                ),
                showlegend=True,
                title="Multi-dimensional Cell Comparison"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("System Reports")
        
        # Generate comprehensive report
        report_data = {
            "System Info": {
                "Bench Name": st.session_state.bench_name,
                "Group Number": st.session_state.group_num,
                "Total Cells": len(cells_data),
                "Report Generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "Performance Summary": {
                "Average Voltage": f"{np.mean([cell['voltage'] for cell in cells_data.values()]):.2f}V",
                "Total Current": f"{sum([cell['current'] for cell in cells_data.values()]):.2f}A",
                "Average Temperature": f"{np.mean([cell['temp'] for cell in cells_data.values()]):.1f}°C",
                "Total Capacity": f"{sum([cell['capacity'] for cell in cells_data.values()]):.2f}Wh"
            }
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.json(report_data)
        
        with col2:
            if st.button("📄 Export Report"):
                st.download_button(
                    label="💾 Download JSON Report",
                    data=json.dumps(report_data, indent=2),
                    file_name=f"battery_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            if st.button("📊 Generate CSV"):
                df = pd.DataFrame([
                    {
                        "Cell": cell_name,
                        "Type": data["cell_type"],
                        **data
                    }
                    for cell_name, data in cells_data.items()
                ])
                
                csv = df.to_csv(index=False)
                st.download_button(
                    label="💾 Download CSV Data",
                    data=csv,
                    file_name=f"battery_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

# Real-time Monitor Page
elif page == "📈 Real-time Monitor":
    st.markdown('<div class="main-header">📈 Real-time Monitoring</div>', unsafe_allow_html=True)
    
    if not st.session_state.cells_data:
        st.warning("⚠️ Please configure your battery system first.")
        st.stop()
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("🔄 Auto Refresh", value=True)
    refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 1, 10, 3)
    
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()
    
    # Real-time data simulation
    cells_data = st.session_state.cells_data.copy()
    
    # Update with simulated real-time data
    for cell_name, data in cells_data.items():
        config = CELL_CONFIGS[data["cell_type"]]
        updated_data = generate_mock_data(data["cell_type"], data["voltage"], data["current"])
        cells_data[cell_name].update(updated_data)
    
    # Create real-time charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚡ Live Voltage Monitoring")
        
        voltages = [data["voltage"] for data in cells_data.values()]
        cell_names = list(cells_data.keys())
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=cell_names,
            y=voltages,
            mode='lines+markers',
            name='Voltage',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Real-time Voltage Levels",
            xaxis_title="Cells",
            yaxis_title="Voltage (V)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🌡️ Live Temperature Monitoring")
        
        temperatures = [data["temp"] for data in cells_data.values()]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=cell_names,
            y=temperatures,
            mode='lines+markers',
            name='Temperature',
            line=dict(color='#ff7f0e', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Real-time Temperature Levels",
            xaxis_title="Cells",
            yaxis_title="Temperature (°C)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Alert system
    st.subheader("🚨 Alert System")
    
    alerts = []
    for cell_name, data in cells_data.items():
        status, status_class = get_cell_status(data["voltage"], data["cell_type"])
        if "Critical" in status or "Overcharged" in status:
            alerts.append(f"⚠️ {cell_name}: {status}")
        if data["temp"] > 45:
            alerts.append(f"🌡️ {cell_name}: High temperature ({data['temp']}°C)")
    
    if alerts:
        for alert in alerts:
            st.error(alert)
    else:
        st.success("✅ All systems operating normally")
    
    # Store historical data
    current_snapshot = {
        "timestamp": datetime.now(),
        "data": cells_data.copy()
    }
    st.session_state.historical_data.append(current_snapshot)
    
    # Keep only last 100 snapshots
    if len(st.session_state.historical_data) > 100:
        st.session_state.historical_data = st.session_state.historical_data[-100:]

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        🔋 Advanced Battery Management System | Built with Streamlit
    </div>
    """, 
    unsafe_allow_html=True
)