"""
Sample Resume Generator
Generates sample PDF and DOCX resume files for instant local testing.
"""

import os
import docx

def create_sample_docx(filepath: str):
    """Creates a sample DOCX resume for John Doe (Python & ML Engineer)."""
    doc = docx.Document()
    
    doc.add_heading('John Doe', level=0)
    doc.add_paragraph('Email: john.doe@example.com | Phone: (555) 234-5678 | Location: New York, NY')
    doc.add_paragraph('GitHub: github.com/johndoe | LinkedIn: linkedin.com/in/johndoe')
    
    doc.add_heading('Professional Summary', level=1)
    doc.add_paragraph(
        'Passionate Python Developer and Machine Learning enthusiast with hands-on experience building '
        'web applications with Flask and Django, developing predictive models with Scikit-Learn and Pandas, '
        'and writing clean SQL database queries. Seeking a challenging role as a Python Developer or AI/ML Engineer.'
    )
    
    doc.add_heading('Technical Skills', level=1)
    doc.add_paragraph('Programming Languages: Python, Java, SQL, C++, HTML, CSS, JavaScript')
    doc.add_paragraph('Frameworks & Web: Flask, Django, REST API, React')
    doc.add_paragraph('ML & Data Science: Machine Learning, Deep Learning, NLP, Pandas, NumPy, Scikit-Learn, TensorFlow, Power BI')
    doc.add_paragraph('Developer Tools: Git, GitHub, Docker, VS Code, Linux')
    
    doc.add_heading('Work Experience', level=1)
    doc.add_heading('Software Engineering Intern - Alpha Tech Labs', level=2)
    doc.add_paragraph('June 2023 - Present')
    p = doc.add_paragraph()
    p.add_run('- Developed backend REST APIs using Python and Flask integrated with SQLite databases.\n')
    p.add_run('- Built automated data extraction scripts using Pandas and NumPy to process client logs.\n')
    p.add_run('- Utilized Git and GitHub for team code reviews and version control.')
    
    doc.add_heading('Education', level=1)
    doc.add_paragraph('Bachelor of Science in Computer Science - State University (Graduated 2023)')
    
    doc.add_heading('Academic Projects', level=1)
    p2 = doc.add_paragraph()
    p2.add_run('AI Resume Classifier & Job Matcher:\n')
    p2.add_run('Implemented NLP text preprocessing, TF-IDF vectorization, and Cosine Similarity in Python to rank candidates against job descriptions.\n\n')
    p2.add_run('Customer Sentiment Analysis:\n')
    p2.add_run('Trained a Scikit-Learn Machine Learning model to analyze product reviews with 92% accuracy.')
    
    doc.save(filepath)
    print(f"Created sample DOCX resume at {filepath}")


def create_sample_docx_jane(filepath: str):
    """Creates a sample DOCX resume for Jane Smith (Data Analyst)."""
    doc = docx.Document()
    
    doc.add_heading('Jane Smith', level=0)
    doc.add_paragraph('Email: jane.smith@example.com | Phone: (555) 987-6543 | Location: San Francisco, CA')
    
    doc.add_heading('Professional Summary', level=1)
    doc.add_paragraph(
        'Detail-oriented Data Analyst skilled in SQL, Python, Pandas, NumPy, Power BI, and Tableau. '
        'Adept at transforming raw operational data into actionable business intelligence dashboards.'
    )
    
    doc.add_heading('Technical Skills', level=1)
    doc.add_paragraph('Data Analysis & Tools: SQL, Python, Pandas, NumPy, Power BI, Excel, Tableau, Git')
    doc.add_paragraph('Web & DB: HTML, CSS, JavaScript, PostgreSQL, MySQL, SQLite')
    
    doc.add_heading('Work Experience', level=1)
    doc.add_heading('Junior Data Analyst - DataViz Solutions', level=2)
    doc.add_paragraph('Jan 2023 - Present')
    doc.add_paragraph('- Designed interactive Power BI dashboards for executive decision making.')
    doc.add_paragraph('- Wrote complex SQL queries to extract metrics from multi-terabyte databases.')
    
    doc.add_heading('Education', level=1)
    doc.add_paragraph('Bachelor of Science in Information Technology - City College (2022)')
    
    doc.save(filepath)
    print(f"Created sample DOCX resume at {filepath}")


if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "sample_resumes")
    os.makedirs(out_dir, exist_ok=True)
    create_sample_docx(os.path.join(out_dir, "sample_resume_john_doe.docx"))
    create_sample_docx_jane(os.path.join(out_dir, "sample_resume_jane_smith.docx"))
