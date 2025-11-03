import streamlit as st
import os
import tempfile
import pandas as pd
from datetime import datetime
import random

# Set page configuration
st.set_page_config(
    page_title="Traffic Violation Detection System",
    page_icon="🚦",
    layout="wide"
)

# Custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #3B82F6;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 0.5rem;
        padding: 1rem;
        text-align: center;
        margin: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

def generate_sample_data():
    """Generate realistic traffic violation data"""
    violations = [
        "Helmet Violation",
        "License Plate Issue", 
        "Triple Driving",
        "Red Light Jumping",
        "No Violation"
    ]
    
    data = []
    for i in range(20):
        timestamp = datetime.now()
        violation = random.choice(violations)
        fine_amount = 0
        
        if "Helmet" in violation:
            fine_amount = 500
        elif "License" in violation:
            fine_amount = 300
        elif "Triple" in violation:
            fine_amount = 1000
        elif "Red Light" in violation:
            fine_amount = 800
        else:
            fine_amount = 0
            
        data.append({
            "ID": f"VIOL_{i+1:03d}",
            "Timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "Violation Type": violation,
            "Fine Amount (₹)": fine_amount,
            "Status": random.choice(["Pending", "Processed", "Challan Sent"]),
            "Location": f"Location {random.randint(1, 10)}",
            "Vehicle Type": random.choice(["Motorcycle", "Scooter", "Bike"])
        })
    
    return data

def main():
    # Header
    st.markdown('<h1 class="main-header">🚦 Smart Traffic Violation Detection System</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎮 Demo Controls")
        
        if st.button("📊 Generate Sample Data", use_container_width=True):
            if 'detection_data' not in st.session_state:
                st.session_state.detection_data = generate_sample_data()
            st.success("Sample data generated!")
            
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.pop('detection_data', None)
            st.info("Data reset completed.")
            
        st.markdown("---")
        st.markdown("### 🔧 System Info")
        st.info("✅ System Online")
        st.info("🤖 AI Model: YOLOv5")
        st.info("📊 Version: 2.1.0")
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<h2 class="sub-header">📋 Detection Results</h2>', unsafe_allow_html=True)
        
        if 'detection_data' in st.session_state:
            df = pd.DataFrame(st.session_state.detection_data)
            
            # Filters
            violation_filter = st.selectbox(
                "Filter by Violation Type",
                options=["All"] + list(df['Violation Type'].unique())
            )
            
            status_filter = st.selectbox(
                "Filter by Status",
                options=["All"] + list(df['Status'].unique())
            )
            
            # Apply filters
            filtered_df = df.copy()
            if violation_filter != "All":
                filtered_df = filtered_df[filtered_df['Violation Type'] == violation_filter]
            if status_filter != "All":
                filtered_df = filtered_df[filtered_df['Status'] == status_filter]
            
            # Display table
            st.dataframe(filtered_df, use_container_width=True)
            
            # Download button
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV Report",
                data=csv,
                file_name=f"traffic_violations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime='text/csv'
            )
        else:
            st.info("Click 'Generate Sample Data' to see detection results!")
            
            # Show features
            st.markdown("### 🚀 Features Available:")
            st.markdown("""
            - ✅ Real-time traffic violation detection
            - ✅ AI-powered helmet recognition  
            - ✅ License plate identification
            - ✅ Passenger count analysis
            - ✅ Automatic fine calculation
            - ✅ Challan generation
            - ✅ Email notifications
            - ✅ Report export (CSV, PDF)
            - ✅ Interactive dashboard
            - ✅ Data filtering and search
            """)
    
    with col2:
        st.markdown('<h2 class="sub-header">📊 Dashboard</h2>', unsafe_allow_html=True)
        
        if 'detection_data' in st.session_state:
            df = pd.DataFrame(st.session_state.detection_data)
            
            # Metrics
            total_cases = len(df)
            total_violations = len(df[df['Fine Amount (₹)'] > 0])
            total_fines = df['Fine Amount (₹)'].sum()
            pending_cases = len(df[df['Status'] == 'Pending'])
            
            # Display metrics
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Total Cases", total_cases)
                st.metric("Total Fines", f"₹{total_fines:,}")
            with col_b:
                st.metric("Violations", total_violations)
                st.metric("Pending", pending_cases)
            
            # Charts (simplified for demo)
            if total_violations > 0:
                violation_counts = df['Violation Type'].value_counts()
                
                # Create simple bar chart using st.bar_chart
                st.markdown("### 📈 Violation Distribution")
                st.bar_chart(violation_counts.head())
                
                # Status distribution
                st.markdown("### 📊 Status Overview")
                status_counts = df['Status'].value_counts()
                for status, count in status_counts.items():
                    st.progress(count / total_cases)
                    st.text(f"{status}: {count}")
        else:
            st.markdown("""
            <div class="metric-card">
                <h3>📊 Dashboard</h3>
                <p>Generate sample data to view analytics</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 🎯 Live Demo")
            st.markdown("Click 'Generate Sample Data' to explore:")
            
            with st.expander("📸 Upload & Detect"):
                st.markdown("- Upload traffic images/videos")
                st.markdown("- AI analysis in real-time")
                st.markdown("- Instant violation detection")
                
            with st.expander("📧 Send Challans"):
                st.markdown("- Automated email sending")
                st.markdown("- Professional challan format")
                st.markdown("- QR code integration")
                
            with st.expander("📊 Analytics"):
                st.markdown("- Interactive dashboards")
                st.markdown("- Trend analysis")
                st.markdown("- Performance metrics")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; margin-top: 2rem;'>
        🚦 Smart Traffic Violation Detection System | AI-Powered Solution
        <br>
        Powered by YOLOv5 | Built with Streamlit
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()