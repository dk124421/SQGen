# 📘 Smart-QGen AI  
### AI-Powered Question Paper & MCQ Generator for Universities

Smart-QGen AI is a powerful **AI-driven examination automation system** built to help
universities, colleges, and educators instantly generate:

✔ Final Semester Question Papers  
✔ Midterm Question Papers  
✔ MCQ Practice Tests  
✔ Topic-Based Objective Questions  
✔ Exam-ready PDF output  

This system uses advanced LLMs through OpenRouter APIs to generate **high-quality academic questions** following strict university formatting rules.  
The project is under active development and more major features will be added soon.

---

## 🚀 Features

### 📝 **1. AI Question Paper Generator**
- Generates **Final Exam** and **Midterm Exam** formats.
- Auto-detects subject type (ML, DBMS, Java, ToC, DSA, CN, etc.).
- Creates:
  - PART-A → Short questions  
  - PART-B → Analytical + Long questions  
  - PART-C → Problem solving / Coding / Numerical  
- Supports **optional syllabus upload** to make papers more accurate.
- Includes diagrams only when relevant (DFA, Trees, ERD, ML pipeline, etc.).
- Includes datasets only when subject type is ML/Data.

### 🎯 **2. MCQ Generator + Practice System**
- Auto-generates high-quality MCQs with:
  - Four options  
  - Correct answer  
  - Explanation  
- Interactive quiz UI  
- Score calculation  
- Progress bar visualization  
- Answer feedback per question  

### 📄 **3. PDF Generator**
- Converts generated papers into **clean, exam-format PDFs**.
- Output is shown inside iframe viewer.
- One-click **download** support.

### 🧠 **4. Subject-Adaptive Question Generation**
The system intelligently adjusts questions based on subject type:
- Coding questions → Java, Python, Web Dev  
- SQL queries → DBMS  
- DFA/TM → ToC  
- Network diagrams → CN  
- Dataset/statistical → ML/AI  
- Algorithm + time complexity → DSA  

### 🖥 **5. Modern Glassmorphic UI**
- Futuristic neon + glass design  
- Fully responsive  
- Built with custom CSS  

---

## 🏗️ Tech Stack

### **Backend**
- **Python 3.14**
- **Django 5**
- **OpenRouter API (LLMs)**  
- **ReportLab** (PDF generation)

### **Frontend**
- HTML5  
- CSS (Glassmorphism + Neon Theme)  
- JavaScript (Fetch API)  

### **Database**
- SQLite (development)

---

## 📌 Repository Structure

Smart-QGen-AI/
│
├── PaperGenerator/
│ ├── models.py
│ ├── views.py
│ └── templates/paper_generator.html
│
├── MCQTest/
│ ├── models.py
│ ├── views.py
│ └── templates/mcq_test.html
│
├── SQGen/
│ ├── settings.py
│ ├── urls.py
│ └── views.py (core logic)
│
├── static/
│ ├── css/style.css
│ └── js/
│ ├── paper.js
│ └── mcq.js
│
└── README.md


## 🔧 Installation & Setup

### 1️⃣ Clone the repository

git clone https://github.com/dk124421/SQGen.git
cd Smart-QGen-AI

shell
Copy code

### 2️⃣ Create virtual environment

python -m venv venv
venv\Scripts\activate

shell
Copy code

### 3️⃣ Install dependencies

pip install -r requirements.txt

makefile
Copy code

### 4️⃣ Add your OpenRouter API Key  
Inside `settings.py`
python
OPENROUTER_API_KEY = "your-key"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

### 5️⃣ Run the server
nginx
Copy code
python manage.py runserver
⚙️ How It Works
1. User Inputs Data
User selects:
Subject
Difficulty
Exam type
Optional syllabus

2. Django prepares a dynamic prompt
The system uses a universal prompt that:
Detects subject type
Generates appropriate questions
Ensures university-exam format

3. OpenRouter LLM generates the paper
Model used:
bash
Copy code
meta-llama/llama-3.3-70b-instruct

4. Django converts output into a PDF

5. PDF displayed in iframe & available for download
📈 Future Additions (Planned)
🔹 1. Unit-wise Question Bank Generator
Generate questions unit-by-unit for syllabus mapping.

🔹 2. Answer Key / Solution Generator
Automatic solutions for descriptive + coding + numerical questions.

🔹 3. Fully Automated MCQ Exam With Timer
Timer-based online exam with scoring algorithms.

🔹 4. Dataset Upload for ML Questions
Users can upload CSV → system generates dataset-based tasks.

🔹 5. Admin Dashboard
Saved papers

Student result analytics

Question bank repository

🔹 6. PDF Theme Customization
College branding
Logo
Custom header

🔹 7. Export to Word (.docx)
🔹 8. API Mode
Allow external apps to generate papers via REST API.

🧪 Current Limitations
⚠ Model sometimes gives extra theory for ML → will be improved
⚠ MCQ parsing may break if LLM formatting changes
⚠ No saved history yet
⚠ No login/auth system

🤝 Contributing
Pull requests are welcome!
If you want to add new features, improve UI, or extend AI prompts, feel free to fork the repo and submit a PR.

📄 License
This project is open-source under the MIT License.