# EB Bill Backend — FastAPI

Backend for KSEB Meter Reading Automation: ESP32-CAM uploads meter images → backend stores proof images (Cloudflare R2) → OCR extracts kWh → saves to Supabase PostgreSQL → mobile app shows readings/bills → admin verifies flagged cases.



## Features (Current / Planned)
 Health endpoint  
 Swagger API docs (`/docs`)  
 Upload endpoint (ESP32 → API)  
 Store images to  
Save metadata to Supabase PostgreSQL  
OCR (crop ROI + digit extraction)  
 Admin approve/correct/reject + audit log  
 Monthly bill generation + tariff rules  
 ML prediction + anomaly/leakage detection  

---

## Tech Stack
- FastAPI (Python)
- Supabase PostgreSQL (cloud database)
- Cloudflare R2 (image storage)
- Render (free hosting for backend)
- JWT Auth (access + refresh tokens)

---



## Run this project

git clone <your-repo-url>
cd <folder_name>
python3 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000


## TO update the new pip package use 
python.exe -m pip install --upgrade pip


## TO RUN THE PROJECT 
run_project.bat


