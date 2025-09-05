from django import forms

class ResumeForm(forms.Form):
    job_description = forms.FileField(label="Upload Job Description (.txt/.docx)")
    resume = forms.FileField(label="Upload Resume (.txt/.docx/.pdf)")
