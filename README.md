# ANPR System

## Description
This project is an **Automatic Number Plate Recognition (ANPR) system**, developed by **Shreyansh Gurjar** as a technical assignment.  
The system detects and recognizes vehicle number plates from images or video streams using **YOLOv8** and **OCR** techniques.

---

## Features
- Detects vehicle number plates in images and videos.
- Recognizes characters on number plates using OCR.
- Can process directories of images automatically.
- Generates reports of detected number plates.
- Dedicated Whitelist and Blacklist Section
- Visualization of Statistics
- Preview video of capturing
- Efficient Searching feature
- Easy to manage Plates in Database
- Realtime Alert of existing plates and new plate adding

---

## Technologies Used
- Python 3.11
- [YOLOv8](https://ultralytics.com/) for object detection
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) for text recognition
- OpenCV for image and video processing
- Django for backend
- React JS+Vite


---

----------------------------------# Installation and initialization of Server
 
1. ** Clone the repository **
```bash
git clone https://github.com/shreyanshGurjar04/Maharshi-Industries-project.git

```

2. ** Navigate to ANPR_system **
```bash
cd ANPR_system

```
   
3. ** Make Virtual Environment with following Script **

```bash
python3 -m venv venv

```
4. ** Activate the virtual environment **

```bash
source venv/bin/activate (macos)

.venv\Scripts\activate (Windows)

```
5. ** Install python libraries from requirements.txt **

```bash
pip3 install -r requirements.txt

```
6. ** initialize the backend **

```bash
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver

```

------------------------------------#  Initialization of Frontend

1. ** Navigate to Frontend **

```bash
cd Frontend

```

2. ** Install Dependencies **
```bash
    npm install
```
3. ** Initializing the frontend **
   
```bash
    npm run dev
```

Usage
- Open the frontend in your browser.
- Interact with the ANPR system; images/videos are processed by the backend and results displayed on the frontend.

