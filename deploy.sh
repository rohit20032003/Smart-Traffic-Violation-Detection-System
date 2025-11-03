#!/bin/bash
# Deployment script for Smart Traffic Violation Detection System

echo "Setting up deployment environment..."

# Create deployment directory
mkdir -p traffic_violation_deployment
cd traffic_violation_deployment

# Copy necessary files
cp ../app_demo.py .
cp ../requirements_deploy.txt requirements.txt
cp ../Procfile .
cp ../README_DEPLOYMENT.md README.md

echo "Files copied successfully!"

# Create .gitignore
cat > .gitignore << EOF
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST
*.pyc
*.pyo
*pyd
.Python
.venv/
venv/
ENV/
.env
.venv
env/
.DS_Store
Thumbs.db
output/
runs/
*.log
EOF

echo "Deployment package created successfully!"
echo "To deploy:"
echo "1. Install Heroku CLI"
echo "2. heroku create traffic-violation-detector"
echo "3. git init && git add . && git commit -m 'Initial commit'"
echo "4. git push heroku main"
echo "5. Your app will be available at the Heroku URL"