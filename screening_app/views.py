from django.shortcuts import render, redirect
from .forms import ResumeForm
import os
from django.conf import settings
import pandas as pd
from docx import Document
from pdfminer.high_level import extract_text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.utils.text import slugify

# --- Function to read uploaded files ---
def read_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extract_text(file_path)
    elif ext == '.docx':
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    elif ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# --- Function to calculate similarity score ---
def calculate_score(resume_text, jd_text):
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf = vectorizer.fit_transform([resume_text, jd_text])
    score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return round(score * 100, 2)  # Score in %

# --- Index view (upload page) ---
def index(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            jd_file = request.FILES['job_description']
            resume_file = request.FILES['resume']

            # Ensure media folder exists
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

            # Sanitize filenames
            jd_filename = slugify(os.path.splitext(jd_file.name)[0]) + os.path.splitext(jd_file.name)[1]
            resume_filename = slugify(os.path.splitext(resume_file.name)[0]) + os.path.splitext(resume_file.name)[1]

            jd_path = os.path.join(settings.MEDIA_ROOT, jd_filename)
            resume_path = os.path.join(settings.MEDIA_ROOT, resume_filename)

            # Save Job Description
            with open(jd_path, 'wb+') as f:
                for chunk in jd_file.chunks():
                    f.write(chunk)

            # Save Resume
            with open(resume_path, 'wb+') as f:
                for chunk in resume_file.chunks():
                    f.write(chunk)

            # Store paths in session
            request.session['jd_path'] = jd_path
            request.session['resume_path'] = resume_path

            # ✅ Redirect to result view instead of rendering blank result
            return redirect('result')
    else:
        form = ResumeForm()
    return render(request, 'screening_app/index.html', {'form': form})

# --- Result view (score & Excel storage) ---
def result(request):
    jd_path = request.session.get('jd_path')
    resume_path = request.session.get('resume_path')

    if not jd_path or not resume_path:
        return render(request, 'screening_app/index.html', {
            'form': ResumeForm(),
            'error': 'Please upload both Job Description and Resume.'
        })

    # Read texts
    jd_text = read_file(jd_path)
    resume_text = read_file(resume_path)

    # Calculate score
    score = calculate_score(resume_text, jd_text)

    # Save results in Excel
    excel_file = os.path.join(settings.BASE_DIR, 'resumes_data.xlsx')
    if os.path.exists(excel_file):
        df = pd.read_excel(excel_file)
    else:
        df = pd.DataFrame(columns=['Resume', 'Job Description', 'Score'])

    df = pd.concat([df, pd.DataFrame([{
        'Resume': os.path.basename(resume_path),
        'Job Description': os.path.basename(jd_path),
        'Score': score
    }])], ignore_index=True)

    df.to_excel(excel_file, index=False)

    return render(request, 'screening_app/result.html', {   # ✅ plural filename
        'score': score,
        'resume_name': os.path.basename(resume_path)
    })
