# AI-Based Resume Screening & Job Recommendation System

A complete full-stack AI/ML web application built with **Python**, **Flask**, **NLP**, **Scikit-Learn**, and **SQLite**. The system extracts candidate text and technical skills from PDF or DOCX resumes, compares the candidate's profile against an active job database using **TF-IDF Vectorization** and **Cosine Similarity**, ranks the top 5 recommended jobs, and performs **Skill Gap Analysis** with actionable learning suggestions.

---

## 🌟 Key Features

1. **Modern Responsive UI (No Bootstrap)**
   - Custom professional blue/white design using CSS Flexbox/Grid, soft shadows, rounded cards, and smooth progress meters.
2. **Resume Parsing & Skill Extraction**
   - Supports `.pdf` (via `pdfplumber` / `PyPDF2`) and `.docx` (via `python-docx`).
   - Extracts Name, Email, Phone Number, Education, Experience, Projects, and technical skills (Python, Java, C++, SQL, Machine Learning, TensorFlow, React, Power BI, Git, etc.).
3. **Genuine ML Job Matching (TF-IDF + Cosine Similarity)**
   - Converts candidate text and job descriptions into high-dimensional TF-IDF vectors.
   - Computes exact Cosine Similarity matrices to generate genuine 0%–100% match scores.
4. **Skill Gap Analysis & Recommendations**
   - Shows matching skills, missing skills, and personalized learning path suggestions for each job.
5. **Interactive Analytics Dashboard**
   - Displays key metrics: Total Detected Skills, Jobs Analyzed, Highest Match Score, Top Role, and Skill Inventories.
6. **Pre-Loaded Job Database & Sample Resumes**
   - Includes 20 realistic IT/Software engineering jobs in SQLite and sample resumes for instant local testing.

---

## 📁 Project Directory Structure

```
hopeful-hopper/
├── app.py                      # Main Flask application entrypoint & SQLite DB routes
├── requirements.txt            # Python package dependencies
├── database.db                 # SQLite database (auto-generated on app start)
├── README.md                   # Installation & documentation guide
│
├── model/
│   ├── __init__.py
│   └── matching_model.py       # JobMatcher class (TF-IDF & Cosine Similarity logic)
│
├── utils/
│   ├── __init__.py
│   ├── resume_parser.py        # PDF and DOCX text extraction
│   ├── skill_extractor.py     # Skill dictionary matching & contact details parser
│   └── text_preprocessing.py # Text cleaning and stopword filtering
│
├── data/
│   ├── jobs.csv                # Sample database with 20 tech jobs
│   ├── create_sample_resumes.py# Script generating sample DOCX files
│   └── sample_resumes/         # Pre-packaged sample resumes for instant testing
│
├── templates/
│   ├── base.html               # Shared navigation & footer template
│   ├── index.html              # Home page
│   ├── upload.html             # Resume file drag & drop upload form
│   ├── result.html             # Resume analysis & extracted skills view
│   ├── recommendations.html    # Top 5 recommended jobs & skill gap cards
│   ├── dashboard.html          # Interactive candidate analytics dashboard
│   └── jobs.html               # Browse full job database
│
├── static/
│   ├── css/
│   │   └── style.css           # Custom modern responsive styling
│   └── js/
│       └── script.js          # File uploader handlers & progress animations
│
└── uploads/                    # Directory where uploaded resumes are stored
```

---

## 🛠️ Installation & Setup Instructions

### 1. Prerequisites
- **Python 3.8+** installed on your system.
- `pip` (Python package manager).

### 2. Clone or Open Project Directory
Navigate to the project root directory in your terminal:
```bash
cd hopeful-hopper
```

### 3. (Optional but Recommended) Create a Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Required Dependencies
Install all required libraries specified in `requirements.txt`:
```bash
pip install -r requirements.txt
```

---

## 🚀 How to Run the Application

Execute `app.py` directly using Python:
```bash
python app.py
```

On execution, the application will automatically:
1. Initialize the SQLite `database.db`.
2. Seed the `jobs` table with 20 sample positions from `data/jobs.csv`.
3. Create sample resume files in `data/sample_resumes/`.
4. Launch the Flask web server at: **`http://127.0.0.1:5000`**

Open `http://127.0.0.1:5000` in any modern web browser to interact with the application.

---

## 🧠 How the ML & NLP Engine Works

1. **Text Extraction & Cleaning (`utils/resume_parser.py`, `utils/text_preprocessing.py`)**:
   - `pdfplumber`/`python-docx` extracts raw text.
   - Text is lowercased, special characters and URLs are removed, and standard English stop words are filtered out.

2. **Skill & Entity Extraction (`utils/skill_extractor.py`)**:
   - RegEx pattern matching extracts candidate email, phone number, and name heuristics.
   - Word-boundary safe pattern matching extracts technical skills against a comprehensive dictionary (`Python`, `SQL`, `Machine Learning`, `TensorFlow`, `React`, `Flask`, `Docker`, `Power BI`, `Git`, etc.).

3. **TF-IDF & Cosine Similarity Matching (`model/matching_model.py`)**:
   - `TfidfVectorizer(stop_words='english', ngram_range=(1, 2))` transforms the resume text and job description texts into numerical vector space matrices reflecting term frequency-inverse document frequency.
   - `cosine_similarity(resume_vector, job_vectors)` calculates the geometric angle between the candidate's vector and each job vector, yielding exact similarity percentages.
   - Composite Scoring combines TF-IDF similarity (70%) and explicit skill overlap ratio (30%) for high recommendation accuracy.

4. **Skill Gap Analysis**:
   - Computes set differences between candidate skills and required job skills to identify missing skills and suggest targeted learning paths.

---

## 🧪 How to Test the Application

### Option A: Instant Test via Sample Resumes
1. Open `http://127.0.0.1:5000` in your browser.
2. Click **"Test with John Doe (Python/ML Resume)"** or **"Test with Jane Smith (Data Analyst Resume)"**.
3. View extracted candidate details on the Analysis page.
4. Click **"View Job Recommendations"** to see top 5 matched jobs ranked by percentage.
5. Click **"Dashboard"** to view overall analytics and skill gap summaries.

### Option B: Upload Your Own Resume
1. Go to the **Upload Resume** page (`http://127.0.0.1:5000/upload`).
2. Drag and drop any `.pdf` or `.docx` resume file into the upload zone.
3. Click **"Analyze & Match Resume"**.
4. Review extracted skills, top job recommendations, match scores, and missing skill suggestions.

---

## 📄 Important Files Summary

- `app.py`: Defines Flask routes, SQLite connection handling, upload handlers, and view functions.
- `model/matching_model.py`: Implements Scikit-Learn TF-IDF Vectorizer & Cosine Similarity matching engine.
- `utils/resume_parser.py`: PDF and DOCX text extraction with fallbacks.
- `utils/skill_extractor.py`: Technical skill matching logic, contact info extraction, and section parsing.
- `data/jobs.csv`: Pre-loaded dataset of 20 tech jobs.
- `static/css/style.css`: Clean, responsive custom CSS with blue/white theme.
