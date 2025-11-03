import streamlit as st
import os
import tempfile
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import random

# Page configuration
st.set_page_config(
    page_title="Smart Traffic Violation Detection System",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #3B82F6;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #D1FAE5;
        border: 1px solid #10B981;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #FEF3C7;
        border: 1px solid #F59E0B;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #FEE2E2;
        border: 1px solid #EF4444;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
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

# Sample data for demo
def generate_sample_detections():
    """Generate sample detection data for demo purposes"""
    sample_data = []
    violation_types = ['Helmet Not Wearing', 'License Plate Issues', 'Triple Driving', 'Red Light Jumping']
    
    for i in range(random.randint(5, 15)):
        helmet_status = random.choice(['Wearing', 'Not Wearing', 'Not Found'])
        lp_status = random.choice(['Visible', 'Not Visible', 'Not Found'])
        passengers = random.randint(1, 4)
        
        # Determine violations
        violations = []
        if helmet_status == 'Not Wearing':
            violations.append('Helmet Violation')
        if lp_status != 'Visible':
            violations.append('License Plate Issue')
        if passengers >= 3:
            violations.append('Triple Driving')
        
        sample_data.append({
            'ID': f'DET_{i+1:03d}',
            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Helmet Status': helmet_status,
            'License Plate Status': lp_status,
            'Passenger Count': passengers,
            'Violations': ', '.join(violations) if violations else 'No Violations',
            'Fine Amount (Rs)': random.randint(500, 2000),
            'Status': random.choice(['Pending', 'Processed', 'Challan Sent'])
        })
    
    return sample_data

def main():
    # Initialize session state
    if 'detections' not in st.session_state:
        st.session_state.detections = []
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    
    # Main header
    st.markdown('<h1 class="main-header">🚦 Smart Traffic Violation Detection System</h1>', unsafe_allow_html=True)
    
    # Sidebar for controls
    with st.sidebar:
        st.markdown('<h2 class="sub-header">Controls</h2>', unsafe_allow_html=True)
        
        # System status
        st.markdown("### System Status")
        st.success("🟢 System Online")
        st.info("Model: YOLOv5 Traffic Detector")
        st.info("Version: 2.1.0")
        
        # Upload options
        st.markdown("### Upload Options")
        uploaded_file = st.file_uploader(
            "Choose an image/video file",
            type=['jpg', 'jpeg', 'png', 'mp4', 'avi', 'mov'],
            help="Upload an image or video file for traffic violation detection"
        )
        
        if uploaded_file is not None:
            if st.button("🎯 Start Detection", use_container_width=True):
                process_uploaded_file_demo(uploaded_file)
        
        st.markdown("---")
        
        # Demo options
        st.markdown("### Demo Features")
        if st.button("📊 Generate Sample Data", use_container_width=True):
            with st.spinner("Generating sample detection data..."):
                st.session_state.detections = generate_sample_detections()
                st.session_state.analysis_complete = True
                st.success("Sample data generated!")
        
        if st.button("🔄 Reset Data", use_container_width=True):
            st.session_state.detections = []
            st.session_state.analysis_complete = False
            st.info("Data reset completed.")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<h2 class="sub-header">Detection Results</h2>', unsafe_allow_html=True)
        
        if st.session_state.analysis_complete and st.session_state.detections:
            display_detection_results()
        else:
            display_welcome_screen()
    
    with col2:
        st.markdown('<h2 class="sub-header">Dashboard</h2>', unsafe_allow_html=True)
        
        if st.session_state.analysis_complete and st.session_state.detections:
            display_dashboard()
        else:
            display_welcome_dashboard()

def display_welcome_screen():
    """Display welcome screen when no data is available"""
    st.markdown("""
    <div class="metric-card">
        <h3>🎯 Ready for Detection</h3>
        <p>Upload an image/video file or generate sample data to see the system in action.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Supported Features:")
    st.markdown("""
    - ✅ Helmet Detection & Violation Identification
    - ✅ License Plate Recognition
    - ✅ Passenger Count Analysis
    - ✅ Traffic Rule Violation Detection
    - ✅ Automated Fine Calculation
    - ✅ Challan Generation & Email
    - ✅ Report Generation (CSV, PDF)
    - ✅ Real-time Dashboard
    """)

def display_welcome_dashboard():
    """Display welcome dashboard"""
    st.markdown("""
    <div class="metric-card">
        <h3>📊 Dashboard</h3>
        <p>Analytics and statistics will appear here after detection.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### System Information:")
    st.info("🔧 CPU: Intel Core i7")
    st.info("🖥️ GPU: NVIDIA GTX 1060")
    st.info("💾 Memory: 16GB RAM")
    st.info("📡 Model: YOLOv5 Custom")

def display_detection_results():
    """Display detection results in the main area"""
    df = pd.DataFrame(st.session_state.detections)
    
    # Filter options
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        violation_filter = st.multiselect(
            "Filter by Violation Type",
            options=df['Violations'].unique(),
            default=[]
        )
    
    with col_filter2:
        status_filter = st.multiselect(
            "Filter by Status",
            options=df['Status'].unique(),
            default=[]
        )
    
    # Apply filters
    filtered_df = df.copy()
    if violation_filter:
        filtered_df = filtered_df[filtered_df['Violations'].isin(violation_filter)]
    if status_filter:
        filtered_df = filtered_df[filtered_df['Status'].isin(status_filter)]
    
    # Display results
    st.dataframe(filtered_df, use_container_width=True, height=400)
    
    # Download options
    col1, col2, col3 = st.columns(3)
    with col1:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"traffic_violations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime='text/csv'
        )
    
    with col2:
        if st.button("📧 Send Challans"):
            send_challans_demo()
    
    with col3:
        if st.button("📊 Generate Report"):
            generate_report_demo()

def display_dashboard():
    """Display dashboard with statistics and charts"""
    df = pd.DataFrame(st.session_state.detections)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Detections", len(df))
    with col2:
        violations_count = len(df[df['Violations'] != 'No Violations'])
        st.metric("Violations Found", violations_count)
    with col3:
        total_fine = df['Fine Amount (Rs)'].sum()
        st.metric("Total Fines (Rs)", f"{total_fine:,}")
    with col4:
        pending_count = len(df[df['Status'] == 'Pending'])
        st.metric("Pending Actions", pending_count)
    
    # Charts
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Violation distribution pie chart
        violation_counts = {}
        for violations in df['Violations']:
            for violation in violations.split(', '):
                if violation != 'No Violations':
                    violation_counts[violation] = violation_counts.get(violation, 0) + 1
        
        if violation_counts:
            fig_pie = px.pie(
                values=list(violation_counts.values()),
                names=list(violation_counts.keys()),
                title="Violation Distribution"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col_chart2:
        # Status distribution bar chart
        status_counts = df['Status'].value_counts()
        fig_bar = px.bar(
            x=status_counts.index,
            y=status_counts.values,
            title="Case Status Distribution",
            labels={'x': 'Status', 'y': 'Count'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Timeline chart
    if len(df) > 1:
        df['Date'] = pd.to_datetime(df['Timestamp']).dt.date
        daily_counts = df.groupby('Date').size().reset_index(name='Count')
        
        fig_line = px.line(
            daily_counts,
            x='Date',
            y='Count',
            title="Detections Over Time"
        )
        st.plotly_chart(fig_line, use_container_width=True)

def process_uploaded_file_demo(uploaded_file):
    """Process uploaded file with demo functionality"""
    try:
        # Show file info
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / 1024:.1f} KB",
            "File type": uploaded_file.type
        }
        
        st.success(f"✅ File '{uploaded_file.name}' uploaded successfully!")
        
        # Simulate processing
        with st.spinner("🔄 Processing file with AI model..."):
            import time
            time.sleep(3)  # Simulate processing time
            
            # Generate sample detection results
            st.session_state.detections = generate_sample_detections()
            st.session_state.analysis_complete = True
            
            st.success(f"✅ Analysis completed! Found {len(st.session_state.detections)} detections.")
        
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")

def send_challans_demo():
    """Demo function for sending challans"""
    st.info("📧 Challan sending feature requires email configuration.")
    st.info("This would integrate with your existing email system using yagmail.")
    
    # Show demo preview
    pending_cases = [d for d in st.session_state.detections if d['Status'] == 'Pending']
    if pending_cases:
        st.success(f"✅ Would send {len(pending_cases)} challans via email.")

def generate_report_demo():
    """Demo function for generating reports"""
    st.info("📊 Report generation feature.")
    st.info("This would generate comprehensive PDF reports with charts and statistics.")
    
    # Show demo stats
    total_violations = len([d for d in st.session_state.detections if d['Violations'] != 'No Violations'])
    st.success(f"✅ Report would include {total_violations} violation cases with detailed analysis.")

if __name__ == "__main__":
    main()