import streamlit as st
import os
import cv2
import torch
import glob
import time
import requests
from pathlib import Path
import tempfile
import base64
from io import BytesIO
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Import YOLOv5 utilities
from models.experimental import attempt_load
from utils.datasets import LoadImages, LoadStreams
from utils.general import check_img_size, check_requirements, non_max_suppression, scale_coords
from utils.plots import plot_one_box
from utils.torch_utils import select_device

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
</style>
""", unsafe_allow_html=True)

class TrafficDetector:
    def __init__(self):
        self.device = select_device()
        self.half = self.device.type != 'cpu'
        self.model = None
        self.names = None
        self.colors = None
        self.model_loaded = False
        
    def load_model(self, weights_path='./runs/train/finalModel/weights/best.pt'):
        try:
            with st.spinner("Loading YOLO model..."):
                if not os.path.exists(weights_path):
                    st.error(f"Model weights not found at {weights_path}")
                    return False
                    
                self.model = attempt_load(weights_path, map_location=self.device)
                self.stride = int(self.model.stride.max())
                self.imgsz = check_img_size(448, s=self.stride)
                
                if self.half:
                    self.model.half()
                    
                self.names = self.model.module.names if hasattr(self.model, 'module') else self.model.names
                self.colors = [[255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 0], [255, 0, 255], [0, 255, 255]]
                
                if self.device.type != 'cpu':
                    self.model(torch.zeros(1, 3, self.imgsz, self.imgsz).to(self.device).type_as(next(self.model.parameters())))
                    
                self.model_loaded = True
                return True
        except Exception as e:
            st.error(f"Failed to load model: {str(e)}")
            return False
    
    def detect_license_plate(self, image_path):
        """Extract license plate using external API"""
        try:
            regions = ['mx', 'in']
            with open(image_path, 'rb') as fp:
                response = requests.post(
                    'https://api.platerecognizer.com/v1/plate-reader/',
                    data=dict(regions=regions),
                    files=dict(upload=fp),
                    headers={'Authorization': 'Token 5cb2b9e847d8f063dc54b2fc7eac9c769c3ac4c5'}
                )
                result = response.json()
                if 'results' in result and result['results']:
                    return result['results'][0]['plate']
        except Exception as e:
            st.warning(f"License plate detection failed: {str(e)}")
        return "Not detected"
    
    def process_image(self, image_file):
        """Process a single image for detection"""
        if not self.model_loaded:
            return None, None, None, None
            
        try:
            # Save uploaded image temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_file.write(image_file.getvalue())
                temp_path = temp_file.name
            
            # Load image dataset
            dataset = LoadImages(temp_path, img_size=self.imgsz, stride=self.stride)
            
            results = []
            detections = []
            
            for path, img, im0s, _ in dataset:
                img = torch.from_numpy(img).to(self.device)
                img = img.half() if self.half else img.float()
                img /= 255.0
                if img.ndimension() == 3:
                    img = img.unsqueeze(0)
                
                # Inference
                pred = self.model(img, augment=False)[0]
                pred = non_max_suppression(pred, 0.25, 0.45, classes=None, agnostic_nms=False)
                
                # Process detections
                for det in pred:
                    if len(det):
                        det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0s.shape).round()
                        
                        for *xyxy, conf, cls in det:
                            c = int(cls)
                            label = f'{self.names[c]} {conf:.2f}'
                            plot_one_box(xyxy, im0s, label=label, color=self.colors[c], line_thickness=3)
                            
                            # Extract rider region for detailed analysis
                            if self.names[c] == 'Rider':
                                x1, y1, x2, y2 = int(xyxy[0])-10, int(xyxy[1])-10, int(xyxy[2])+10, int(xyxy[3])+10
                                try:
                                    roi = im0s[max(0, y1):min(im0s.shape[0], y2), max(0, x1):min(im0s.shape[1], x2)]
                                    rider_path = 'temp_rider.jpg'
                                    cv2.imwrite(rider_path, roi)
                                    
                                    # Analyze rider details
                                    helmet_status, lp_status, lp_number, passenger_count = self.analyze_rider(rider_path)
                                    detections.append({
                                        'bbox': [int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])],
                                        'helmet_status': helmet_status,
                                        'lp_status': lp_status,
                                        'lp_number': lp_number,
                                        'passenger_count': passenger_count,
                                        'confidence': float(conf)
                                    })
                                    
                                    # Clean up
                                    if os.path.exists(rider_path):
                                        os.remove(rider_path)
                                        
                                except Exception as e:
                                    st.error(f"Error processing rider region: {str(e)}")
            
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
            return im0s, results, detections
            
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")
            return None, None, None
    
    def analyze_rider(self, rider_image_path):
        """Analyze individual rider for helmet, license plate, and passengers"""
        try:
            dataset = LoadImages(rider_image_path, img_size=self.imgsz, stride=self.stride)
            
            helmet_status = None
            lp_status = None
            lp_number = None
            passenger_count = 0
            
            for _, img, im0s, _ in dataset:
                img = torch.from_numpy(img).to(self.device)
                img = img.half() if self.half else img.float()
                img /= 255.0
                if img.ndimension() == 3:
                    img = img.unsqueeze(0)
                
                pred = self.model(img, augment=False)[0]
                pred = non_max_suppression(pred, 0.25, 0.45, classes=None, agnostic_nms=False)
                
                for det in pred:
                    if len(det):
                        det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0s.shape).round()
                        
                        for *xyxy, conf, cls in det:
                            c = int(cls)
                            class_name = self.names[c]
                            
                            if class_name == "Helmet":
                                helmet_status = True
                                passenger_count += 1
                            elif class_name == "No Helmet":
                                helmet_status = False
                                passenger_count += 1
                            elif class_name == "LP":
                                lp_status = True
                                # Extract license plate region for OCR
                                x1, y1, x2, y2 = int(xyxy[0])-50, int(xyxy[1])-50, int(xyxy[2])+50, int(xyxy[3])+50
                                try:
                                    lp_roi = im0s[max(0, y1):min(im0s.shape[0], y2), max(0, x1):min(im0s.shape[1], x2)]
                                    lp_path = 'temp_lp.jpg'
                                    cv2.imwrite(lp_path, lp_roi)
                                    lp_number = self.detect_license_plate(lp_path)
                                    if os.path.exists(lp_path):
                                        os.remove(lp_path)
                                except:
                                    lp_number = "Detection failed"
            
            return helmet_status, lp_status, lp_number, passenger_count
            
        except Exception as e:
            st.error(f"Error analyzing rider: {str(e)}")
            return None, None, None, 0

def main():
    # Initialize session state
    if 'detector' not in st.session_state:
        st.session_state.detector = TrafficDetector()
    if 'detections' not in st.session_state:
        st.session_state.detections = []
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    
    # Main header
    st.markdown('<h1 class="main-header">🚦 Smart Traffic Violation Detection System</h1>', unsafe_allow_html=True)
    
    # Sidebar for controls
    with st.sidebar:
        st.markdown('<h2 class="sub-header">Controls</h2>', unsafe_allow_html=True)
        
        # Model loading
        if st.button("Load Detection Model"):
            with st.spinner("Loading model..."):
                if st.session_state.detector.load_model():
                    st.success("Model loaded successfully!")
                else:
                    st.error("Failed to load model")
        
        # Upload options
        st.markdown("### Upload Options")
        uploaded_file = st.file_uploader(
            "Choose an image/video file",
            type=['jpg', 'jpeg', 'png', 'mp4', 'avi', 'mov'],
            help="Upload an image or video file for traffic violation detection"
        )
        
        if uploaded_file is not None:
            if st.button("Start Detection"):
                process_uploaded_file(uploaded_file)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<h2 class="sub-header">Detection Results</h2>', unsafe_allow_html=True)
        
        if st.session_state.analysis_complete:
            display_detection_results()
        else:
            st.info("Upload an image or video and click 'Start Detection' to begin analysis.")
    
    with col2:
        st.markdown('<h2 class="sub-header">Violation Summary</h2>', unsafe_allow_html=True)
        
        if st.session_state.analysis_complete:
            display_violation_summary()
        else:
            st.info("Detection results will appear here after analysis.")
    
    # Reports section
    if st.session_state.analysis_complete:
        st.markdown('<h2 class="sub-header">Generate Reports</h2>', unsafe_allow_html=True)
        generate_reports_section()

def process_uploaded_file(uploaded_file):
    """Process the uploaded file for detection"""
    try:
        st.session_state.detections = []
        st.session_state.analysis_complete = False
        
        if uploaded_file.type.startswith('image/'):
            # Process image
            image = st.session_state.detector.process_image(uploaded_file)
            if image is not None:
                st.session_state.analysis_complete = True
                st.success("Image analysis completed!")
            else:
                st.error("Failed to process image")
                
        elif uploaded_file.type.startswith('video/'):
            # Process video (simplified for demo)
            st.info("Video processing is not implemented in this demo version.")
            
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")

def display_detection_results():
    """Display detection results in the main area"""
    if not st.session_state.detector.model_loaded:
        st.warning("Please load the detection model first.")
        return
    
    # Display processed image if available
    st.image("temp_result.jpg" if os.path.exists("temp_result.jpg") else None, 
             caption="Detection Results", use_column_width=True)
    
    # Display detections table
    if st.session_state.detections:
        df = pd.DataFrame(st.session_state.detections)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No detections found in the uploaded file.")

def display_violation_summary():
    """Display violation summary and statistics"""
    if not st.session_state.detections:
        st.info("No violations detected.")
        return
    
    # Calculate violation statistics
    total_riders = len(st.session_state.detections)
    helmet_violations = sum(1 for d in st.session_state.detections if d['helmet_status'] == False)
    lp_violations = sum(1 for d in st.session_state.detections if d['lp_status'] != True)
    passenger_violations = sum(1 for d in st.session_state.detections if d['passenger_count'] >= 3)
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Riders", total_riders)
    with col2:
        st.metric("Helmet Violations", helmet_violations)
    with col3:
        st.metric("License Plate Issues", lp_violations)
    with col4:
        st.metric("Passenger Violations", passenger_violations)
    
    # Violation pie chart
    if total_riders > 0:
        violations_data = {
            'Violation Type': ['No Helmet', 'License Plate Issues', 'Passenger Violations'],
            'Count': [helmet_violations, lp_violations, passenger_violations]
        }
        
        fig = px.pie(violations_data, values='Count', names='Violation Type',
                     title="Violation Distribution")
        st.plotly_chart(fig, use_container_width=True)

def generate_reports_section():
    """Generate and download reports"""
    if not st.session_state.detections:
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Generate CSV Report"):
            generate_csv_report()
    
    with col2:
        if st.button("Generate PDF Summary"):
            generate_pdf_summary()
    
    with col3:
        if st.button("Send Challan"):
            send_challan_section()

def generate_csv_report():
    """Generate CSV report of detections"""
    try:
        df = pd.DataFrame(st.session_state.detections)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"traffic_violation_report_{timestamp}.csv"
        
        df.to_csv(filename, index=False)
        st.success(f"CSV report generated: {filename}")
        
        with open(filename, 'rb') as file:
            st.download_button(
                label="Download CSV",
                data=file,
                file_name=filename,
                mime='text/csv'
            )
    except Exception as e:
        st.error(f"Error generating CSV report: {str(e)}")

def generate_pdf_summary():
    """Generate PDF summary report"""
    st.info("PDF generation feature will be implemented with proper PDF library integration.")

def send_challan_section():
    """Send challenge via email"""
    st.info("Email functionality requires proper SMTP configuration.")

if __name__ == "__main__":
    main()