# # resumes/utils.py
# import fitz  # PyMuPDF
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity

# def extract_text_from_pdf(file_path):
#     doc = fitz.open(file_path)
#     text = ""
#     for page in doc:
#         text += page.get_text()
#     return text.strip()

# def calculate_similarity(resume_text, job_text):
#     vectorizer = TfidfVectorizer(stop_words='english')
#     vectors = vectorizer.fit_transform([resume_text, job_text])
#     return cosine_similarity(vectors[0:1], vectors[1:2])[0][0] * 100




