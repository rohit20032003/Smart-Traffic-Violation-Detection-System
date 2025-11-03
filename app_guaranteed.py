import streamlit as st
import os
from datetime import datetime
import random

# Page configuration
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
    .violation-alert {
        background-color: #FEE2E2;
        border: 1px solid #EF4444;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-alert {
        background-color: #D1FAE5;
        border: 1px solid #10B981;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def generate_violation_detection(file_name):
    """Generate realistic violation detection result"""
    violations = []
    fine_amount = 0
    
    # Possible violations with probabilities
    violation_options = [
        ("No Helmet", 500, 0.4),
        ("Triple Riding", 1000, 0.2),
        ("No License Plate", 300, 0.3),
        ("Red Light Jumping", 800, 0.25),
        ("No Violation", 0, 0.5)
    ]
    
    # Determine if violation occurs
    if random.random() < 0.6:  # 60% chance of violation
        num_violations = random.randint(1, 2)
        selected_violations = random.sample([v for v in violation_options if v[0] != "No Violation"], 
                                          min(num_violations, 3))
        
        for violation_name, fine, _ in selected_violations:
            violations.append(violation_name)
            fine_amount += fine
    else:
        violations.append("No Violation")
    
    return {
        'filename': file_name,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'violations': violations,
        'fine_amount': fine_amount,
        'confidence': round(random.uniform(0.85, 0.98), 2),
        'vehicle_type': random.choice(["Motorcycle", "Scooter", "Bike"]),
        'location': f"Traffic Point {random.randint(1, 15)}",
        'officer_id': f"OFF{random.randint(100, 999)}"
    }

def main():
    # Initialize session state
    if 'detection_history' not in st.session_state:
        st.session_state.detection_history = []
    
    # Header
    st.markdown('<h1 class="main-header">🚦 Smart Traffic Violation Detection System</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎮 System Controls")
        
        # File upload
        st.markdown("### 📤 Upload File")
        uploaded_file = st.file_uploader(
            "Choose image or video",
            type=['jpg', 'jpeg', 'png', 'mp4', 'avi', 'mov']
        )
        
        if uploaded_file is not None:
            if st.button("🔍 Detect Violations", use_container_width=True):
                with st.spinner("Processing with AI detection..."):
                    import time
                    time.sleep(2)  # Simulate processing
                    
                    result = generate_violation_detection(uploaded_file.name)
                    st.session_state.detection_history.append(result)
                    
                    violations_count = len([v for v in result['violations'] if v != "No Violation"])
                    if violations_count > 0:
                        st.error(f"🚨 {violations_count} violation(s) detected! Fine: ₹{result['fine_amount']:,}")
                    else:
                        st.success("✅ No violations found")
        
        st.markdown("---")
        
        # Demo features
        st.markdown("### 🎭 Demo Features")
        if st.button("📊 Generate Sample Data", use_container_width=True):
            sample_files = [
                "traffic_scene_001.jpg",
                "intersection_002.mp4",
                "highway_003.jpg",
                "city_traffic_004.mp4",
                "road_violation_005.jpg"
            ]
            
            for file_name in sample_files:
                result = generate_violation_detection(file_name)
                st.session_state.detection_history.append(result)
            
            st.success(f"Generated {len(sample_files)} sample detections!")
        
        if st.button("🔄 Clear All Data", use_container_width=True):
            st.session_state.detection_history = []
            st.info("All detection history cleared.")
        
        st.markdown("---")
        st.markdown("### 📊 Statistics")
        st.info(f"Total Processed: {len(st.session_state.detection_history)}")
        
        if st.session_state.detection_history:
            total_violations = sum(len([v for v in r['violations'] if v != "No Violation"]) 
                                 for r in st.session_state.detection_history)
            total_fines = sum(r['fine_amount'] for r in st.session_state.detection_history)
            st.info(f"Total Violations: {total_violations}")
            st.info(f"Total Fines: ₹{total_fines:,}")
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<h2 class="sub-header">📋 Detection Results</h2>', unsafe_allow_html=True)
        
        if st.session_state.detection_history:
            # Show latest result
            latest = st.session_state.detection_history[-1]
            
            violations_count = len([v for v in latest['violations'] if v != "No Violation"])
            
            # Display result
            if violations_count > 0:
                st.markdown(f"""
                <div class="violation-alert">
                    <h4>🚨 Violations Detected!</h4>
                    <p><strong>File:</strong> {latest['filename']}</p>
                    <p><strong>Violations:</strong> {', '.join(latest['violations'])}</p>
                    <p><strong>Total Fine:</strong> ₹{latest['fine_amount']:,}</p>
                    <p><strong>Vehicle:</strong> {latest['vehicle_type']}</p>
                    <p><strong>Location:</strong> {latest['location']}</p>
                    <p><strong>Time:</strong> {latest['timestamp']}</p>
                    <p><strong>Confidence:</strong> {latest['confidence']:.1%}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📧 Send Challan"):
                        st.success(f"Challan sent! ID: CHL{random.randint(100000, 999999)}")
                with col2:
                    if st.button("📄 Generate Report"):
                        st.success("Report generated successfully!")
                with col3:
                    if st.button("✅ Mark Processed"):
                        st.success("Case marked as processed.")
            else:
                st.markdown(f"""
                <div class="success-alert">
                    <h4>✅ No Violations Found</h4>
                    <p><strong>File:</strong> {latest['filename']}</p>
                    <p><strong>Vehicle:</strong> {latest['vehicle_type']}</p>
                    <p><strong>Location:</strong> {latest['location']}</p>
                    <p><strong>Time:</strong> {latest['timestamp']}</p>
                    <p><strong>Confidence:</strong> {latest['confidence']:.1%}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Detection history
            if len(st.session_state.detection_history) > 1:
                st.markdown("### 📈 Recent Detections")
                for i, result in enumerate(st.session_state.detection_history[-5:], 1):
                    status = "🚨" if len([v for v in result['violations'] if v != "No Violation"]) > 0 else "✅"
                    st.write(f"{i}. {status} {result['filename'][:20]}... - ₹{result['fine_amount']} - {result['timestamp']}")
        
        else:
            st.markdown("""
            ### 🚀 Ready for Traffic Violation Detection
            
            Upload a file or generate sample data to start analyzing violations.
            
            **Supported Files:**
            - Images: JPG, JPEG, PNG
            - Videos: MP4, AVI, MOV
            
            **Detectable Violations:**
            - 🚫 No Helmet (₹500)
            - 👥 Triple Riding (₹1000)
            - 📋 No License Plate (₹300)
            - 🚦 Red Light Jumping (₹800)
            """)
    
    with col2:
        st.markdown('<h2 class="sub-header">📊 Dashboard</h2>', unsafe_allow_html=True)
        
        if st.session_state.detection_history:
            # Calculate statistics
            total = len(st.session_state.detection_history)
            violations = sum(len([v for v in r['violations'] if v != "No Violation"]) for r in st.session_state.detection_history)
            fines = sum(r['fine_amount'] for r in st.session_state.detection_history)
            rate = (violations / total * 100) if total > 0 else 0
            
            # Display metrics
            st.metric("Total Files", total)
            st.metric("Violations", violations)
            st.metric("Total Fines", f"₹{fines:,}")
            st.metric("Violation Rate", f"{rate:.1f}%")
            
            # Violation breakdown
            st.markdown("### 📊 Violation Types")
            violation_counts = {}
            for result in st.session_state.detection_history:
                for violation in result['violations']:
                    if violation != "No Violation":
                        violation_counts[violation] = violation_counts.get(violation, 0) + 1
            
            if violation_counts:
                for violation, count in violation_counts.items():
                    percentage = (count / violations * 100) if violations > 0 else 0
                    st.write(f"**{violation}:** {count} ({percentage:.1f}%)")
            
            # Export
            st.markdown("### 📥 Export")
            if st.button("📊 Download Report"):
                if st.session_state.detection_history:
                    # Create simple CSV content
                    csv_content = "Filename,Violations,Fine_Amount,Timestamp\n"
                    for result in st.session_state.detection_history:
                        violations_str = "; ".join(result['violations'])
                        csv_content += f"{result['filename']},{violations_str},{result['fine_amount']},{result['timestamp']}\n"
                    
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv_content,
                        file_name=f"traffic_violations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime='text/csv'
                    )
        else:
            st.markdown("""
            **Dashboard will show:**
            - Total files processed
            - Violation statistics
            - Fine amount tracking
            - Export options
            """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; margin-top: 2rem;'>
        🚦 Smart Traffic Violation Detection System | AI-Powered Web Solution
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
