# Fake Document Detection System – Architecture

This document describes the system architecture for the Fake Document Detection backend.

---

# System Overview

The system analyzes uploaded documents to detect fraud using image processing and machine learning techniques.

Main components:

- FastAPI backend
- Redis message broker
- Celery background workers
- Image processing services
- OCR services
- Fraud detection services

---

# High-Level Architecture

Client
   │
   ▼
FastAPI Backend
   │
   ▼
File Validation Layer
   │
   ▼
Storage (uploads)
   │
   ▼
Redis Task Queue
   │
   ▼
Celery Workers
   │
   ├─ PDF Normalization
   ├─ Image Preprocessing
   ├─ OCR Extraction
   ├─ Fraud Detection
   └─ Result Generation
   │
   ▼
Database / Storage
   │
   ▼
Result API

---

# Component Breakdown

## 1. API Layer

Framework: FastAPI

Responsibilities:
- Handle file uploads
- Validate files
- Trigger background tasks
- Provide task status endpoints
- Return analysis results

Endpoints:

POST /documents/upload  
GET /documents/task/{task_id}  
GET /documents/result/{task_id}

---

## 2. Validation Layer

Ensures uploaded files are safe.

Checks:
- File signature validation (magic bytes)
- File size limit
- Malware scan
- SHA256 hashing

Tools:
- python-magic
- ClamAV

---

## 3. Storage Layer

Files are stored in local storage during development.

Directory structure:

storage/
 ├── uploads/
 ├── normalized/
 └── processed/

Future production options:
- AWS S3
- Google Cloud Storage

---

## 4. Task Queue System

Background processing system.

Components:

Redis
- Message broker
- Stores queued tasks

Celery
- Executes background jobs
- Handles distributed task processing

Example flow:

FastAPI → Redis Queue → Celery Worker

---

## 5. Document Processing Pipeline

Step 1 — Upload Document

User uploads PDF or image.

Step 2 — Validation

Magic byte validation  
File size validation  
Malware scan  

Step 3 — Hash Generation

Generate SHA256 hash.

Step 4 — PDF Normalization

Convert PDF pages to images.

Step 5 — Image Preprocessing

OpenCV processing:

- resize
- grayscale
- noise removal
- contrast enhancement
- thresholding
- deskew

Step 6 — OCR Extraction

Extract text from processed images.

Step 7 — Fraud Detection

Detect document manipulation.

Techniques:
- Error Level Analysis
- Copy-move detection
- Artifact analysis

Step 8 — Fraud Score

Generate risk score.

---

# Worker Architecture

Multiple Celery workers can run simultaneously.

Example:

Worker 1 → PDF normalization  
Worker 2 → Image preprocessing  
Worker 3 → OCR extraction  
Worker 4 → Fraud detection  

This enables horizontal scaling.

---

# Technology Stack

Backend
- Python
- FastAPI

Background Processing
- Celery
- Redis

Image Processing
- OpenCV
- pdf2image

OCR
- Tesseract
- PaddleOCR

Security
- python-magic
- ClamAV

---

# Scalability

System scales using:

- Multiple Celery workers
- Horizontal worker scaling
- Cloud storage
- Load-balanced API

---

# Future Enhancements

- Machine learning fraud detection
- Document layout analysis
- Signature verification
- AI-based tampering detection
