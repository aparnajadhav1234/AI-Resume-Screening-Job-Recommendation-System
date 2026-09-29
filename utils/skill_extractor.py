"""
Skill Extractor & Resume Section Parser
Identifies contact details, technical skills, education, experience, and projects from raw resume text.
"""

import re
from typing import Dict, List, Any

# Predefined comprehensive set of technical skills
KNOWN_SKILLS = [
    # Programming Languages
    "Python", "Java", "C", "C++", "C#", "JavaScript", "TypeScript", "R", "Go", "Rust", "PHP", "Ruby", "Swift", "Kotlin",
    # Web Development
    "HTML", "CSS", "HTML5", "CSS3", "Flask", "Django", "FastAPI", "React", "Angular", "Vue.js", "Node.js", "Express", "Bootstrap", "Tailwind",
    # Data Science & Machine Learning
    "Machine Learning", "Deep Learning", "NLP", "Natural Language Processing", "Computer Vision", "Data Analysis",
    "Pandas", "NumPy", "Scikit-Learn", "TensorFlow", "PyTorch", "Keras", "OpenCV", "NLTK", "spaCy", "Scipy", "Matplotlib", "Seaborn",
    # Databases & Big Data
    "SQL", "MySQL", "PostgreSQL", "SQLite", "MongoDB", "Redis", "Oracle", "SQL Server",
    # Business Intelligence & Tools
    "Power BI", "Tableau", "Excel", "Git", "GitHub", "GitLab", "Jira",
    # Cloud & DevOps
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Linux", "Unix", "CI/CD", "REST API", "GraphQL", "Microservices", "Selenium"
]


def extract_email(text: str) -> str:
    """Extract email address from resume text using Regex."""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    matches = re.findall(pattern, text)
    return matches[0] if matches else "Not Found"


def extract_phone(text: str) -> str:
    """Extract phone number from resume text using Regex."""
    # Pattern matches forms like +1-555-555-5555, (555) 555-5555, 555-555-5555, 555.555.5555, +91 9876543210
    pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    matches = re.findall(pattern, text)
    if matches:
        # Find the full matched string in text using re.finditer
        for m in re.finditer(pattern, text):
            return m.group(0).strip()
    return "Not Found"


def extract_name(text: str) -> str:
    """Extract candidate name heuristic from top lines of the resume text."""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines:
        return "Candidate Name Not Found"

    for line in lines[:5]:
        # Ignore lines with email, phone, web links, or section headings
        if '@' in line or 'http' in line or re.search(r'\d', line):
            continue
        if len(line.split()) in [2, 3, 4] and not any(kw in line.lower() for kw in ['resume', 'curriculum', 'vitae', 'profile', 'contact', 'summary', 'skills']):
            return line.title()

    return lines[0].title() if lines else "Candidate Name Not Found"


def extract_skills(text: str) -> List[str]:
    """
    Detect technical skills present in the resume text.
    Handles exact case-insensitive matching and word boundary safety (e.g. C vs C++ vs CSS).
    """
    detected_skills = set()
    text_lower = text.lower()

    for skill in KNOWN_SKILLS:
        skill_lower = skill.lower()

        # Special regex handling for skills with symbols like C++, C#, .NET
        if skill_lower == 'c++':
            if re.search(r'\bc\+\+\b|c\+\+', text_lower):
                detected_skills.add(skill)
        elif skill_lower == 'c#':
            if re.search(r'\bc#\b|c#', text_lower):
                detected_skills.add(skill)
        elif skill_lower == 'c':
            # Match standalone 'C' avoiding 'C++', 'C#', 'CSS'
            if re.search(r'\bc\b', text_lower) and not re.search(r'\b(c\+\+|c#|css)\b', text_lower):
                detected_skills.add(skill)
        elif skill_lower == 'r':
            if re.search(r'\br\b', text_lower) and not re.search(r'\b(react|rest)\b', text_lower):
                detected_skills.add(skill)
        else:
            # Word boundary regex for multi-word or standard skills
            escaped_skill = re.escape(skill_lower)
            pattern = r'(?:\b|_)' + escaped_skill + r'(?:\b|_)'
            if re.search(pattern, text_lower):
                detected_skills.add(skill)

    return sorted(list(detected_skills))


def extract_section(text: str, keywords: List[str]) -> str:
    """
    Helper function to extract content lines following specific section headers.
    """
    lines = text.split('\n')
    extracted = []
    recording = False
    count = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check if line matches any section keyword header
        line_lower = stripped.lower()
        if any(kw in line_lower for kw in keywords) and len(stripped) < 40:
            recording = True
            count = 0
            extracted.append(stripped)
            continue

        if recording:
            extracted.append(stripped)
            count += 1
            if count >= 6:  # limit snippet length
                break

    if extracted:
        return "\n".join(extracted)
    return "Not explicitly detailed in resume."


def parse_resume_full(text: str) -> Dict[str, Any]:
    """
    Extracts all structured fields from raw resume text.
    """
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education": extract_section(text, ["education", "academic", "qualification", "university", "college", "degree"]),
        "experience": extract_section(text, ["experience", "work history", "employment", "internship", "professional experience"]),
        "projects": extract_section(text, ["project", "key projects", "academic projects", "personal projects"])
    }
