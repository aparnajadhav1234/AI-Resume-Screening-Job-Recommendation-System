"""
Job Matching & Recommendation Model
Uses TF-IDF Vectorization and Cosine Similarity to compute candidate-job match percentages
and performs Skill Gap Analysis.
"""

from typing import List, Dict, Any
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils.text_preprocessing import clean_text, remove_stopwords


class JobMatcher:
    def __init__(self):
        # Initialize TF-IDF Vectorizer with English stop words and sublinear TF scaling
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            sublinear_tf=True
        )

    def calculate_matches(
        self,
        resume_text: str,
        jobs_list: List[Dict[str, Any]],
        candidate_skills: List[str],
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Calculates similarity scores between candidate resume text and all jobs in the database.
        Returns top N job recommendations with match percentages and skill gap details.
        """
        if not jobs_list:
            return []

        # Combine job title, required skills, and description to form rich document representation
        job_documents = []
        for job in jobs_list:
            doc = f"{job['job_title']} {job['required_skills']} {job['description']}"
            job_documents.append(remove_stopwords(doc))

        # Preprocess candidate resume text
        processed_resume = remove_stopwords(resume_text)

        # Append candidate document to job documents array for unified TF-IDF vector space transform
        all_documents = [processed_resume] + job_documents

        # Fit and transform TF-IDF matrix
        tfidf_matrix = self.vectorizer.fit_transform(all_documents)

        # Compute cosine similarity between resume (index 0) and all job documents (index 1 onwards)
        resume_vector = tfidf_matrix[0:1]
        job_vectors = tfidf_matrix[1:]
        similarity_scores = cosine_similarity(resume_vector, job_vectors)[0]

        # Prepare recommendations
        recommendations = []
        candidate_skills_set = set(s.lower() for s in candidate_skills)

        for i, score in enumerate(similarity_scores):
            job = jobs_list[i]

            # Parse required skills from comma-separated string in job description
            raw_req_skills = [s.strip() for s in job['required_skills'].split(',') if s.strip()]

            # Determine matching vs missing skills
            matching_skills = []
            missing_skills = []

            for req in raw_req_skills:
                if req.lower() in candidate_skills_set or any(req.lower() in cs for cs in candidate_skills_set):
                    matching_skills.append(req)
                else:
                    missing_skills.append(req)

            # Bonus skill match boost for explicit skill overlap (normalized weighting)
            skill_match_ratio = len(matching_skills) / len(raw_req_skills) if raw_req_skills else 0.0

            # Composite match score: 70% TF-IDF textual similarity + 30% direct skill overlap
            raw_match_pct = (score * 0.70) + (skill_match_ratio * 0.30)
            match_percentage = min(100.0, max(0.0, round(raw_match_pct * 100, 1)))

            # Generate Learning Path Suggestions based on missing skills
            suggestions = []
            if missing_skills:
                for skill in missing_skills[:4]:
                    suggestions.append(f"Learn and build a project using {skill} to increase your candidate match score.")
            else:
                suggestions.append("Outstanding match! You already possess all key technical skills listed for this position.")

            rec_item = {
                "job_id": job['id'],
                "job_title": job['job_title'],
                "company": job['company'],
                "location": job['location'],
                "experience_level": job['experience_level'],
                "required_skills": job['required_skills'],
                "description": job['description'],
                "match_percentage": match_percentage,
                "matching_skills": matching_skills,
                "missing_skills": missing_skills,
                "suggestions": suggestions
            }
            recommendations.append(rec_item)

        # Sort recommendations by match percentage in descending order
        recommendations.sort(key=lambda x: x['match_percentage'], reverse=True)

        return recommendations[:top_n]
