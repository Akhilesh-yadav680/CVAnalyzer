# Resume Screening System

A Django-based web application that automates candidate evaluation by matching resumes with job descriptions. It scores and ranks candidates, helping recruiters save time and select the best-fit applicants efficiently.

## Features
- Upload resumes (PDF/DOCX)
- Enter job descriptions
- Automated resume-job matching
- Candidate scoring and ranking
- Simple, user-friendly interface

## Tech Stack
- Django (Python)
- HTML, CSS, JavaScript
- SQLite (default)
- Optional NLP: NLTK, SpaCy

## Installation
```bash
git clone <https://github.com/Akhilesh-yadav680/CVAnalyzer>
cd resume_screening
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
