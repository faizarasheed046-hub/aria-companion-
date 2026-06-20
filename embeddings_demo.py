from sentence_transformers import SentenceTransformer, util

# Load a small, fast embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# --- EXPERIMENT 1: Similar sentences ---
sentence1 = "I had a really bad day and have no one to talk to"
sentence2 = "I feel overwhelmed n want to cry"
sentence3 = "I love eating pizza on a Friday night"

emb1 = model.encode(sentence1)
emb2 = model.encode(sentence2)
emb3 = model.encode(sentence3)

sim_12 = util.cos_sim(emb1, emb2).item()
sim_13 = util.cos_sim(emb1, emb3).item()

print("=== EXPERIMENT 1: Similarity scores ===")
print(f"'{sentence1}'")
print(f"vs '{sentence2}'")
print(f"→ Similarity: {sim_12:.2f}\n")

print(f"'{sentence1}'")
print(f"vs '{sentence3}'")
print(f"→ Similarity: {sim_13:.2f}\n")

# --- EXPERIMENT 2: CV vs Job Description ---
cv_snippet = """
Experienced in Python, machine learning, scikit-learn,
data preprocessing, and building classification models.
"""

jd_match = """
Looking for a Python developer with ML experience,
familiar with data pipelines and classification algorithms.
"""

jd_no_match = """
Seeking a graphic designer with expertise in Adobe Photoshop,
Illustrator, and brand identity creation.
"""

cv_emb = model.encode(cv_snippet)
jd1_emb = model.encode(jd_match)
jd2_emb = model.encode(jd_no_match)

match_score = util.cos_sim(cv_emb, jd1_emb).item()
nomatch_score = util.cos_sim(cv_emb, jd2_emb).item()

print("=== EXPERIMENT 2: CV vs Job Description ===")
print(f"CV vs ML Engineer JD  → {match_score:.2f}")
print(f"CV vs Designer JD     → {nomatch_score:.2f}")
print(f"\nMatch score as percentage:")
print(f"ML Engineer role:  {match_score*100:.1f}%")
print(f"Designer role:     {nomatch_score*100:.1f}%")