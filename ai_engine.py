import os
import hashlib
import re
from collections import defaultdict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from docx import Document
from openpyxl import load_workbook
from pptx import Presentation
from PIL import Image
import imagehash
import PyPDF2


TEXT_EXTENSIONS = {".txt", ".docx", ".xlsx", ".pptx", ".pdf"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".gif"}


# -------------------------------------------------
# SHA256 HASH
# -------------------------------------------------

def sha256_hash(path):

    hasher = hashlib.sha256()

    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)

        return hasher.hexdigest()

    except:
        return None


# -------------------------------------------------
# TEXT CLEANING
# -------------------------------------------------

def clean_text(text):

    text = text.lower()

    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-z0-9 ]', ' ', text)

    return text


# -------------------------------------------------
# TEXT EXTRACTION
# -------------------------------------------------

def extract_text(path):

    ext = os.path.splitext(path)[1].lower()

    try:

        if ext == ".docx":

            doc = Document(path)

            return clean_text(" ".join(p.text for p in doc.paragraphs))


        if ext == ".xlsx":

            wb = load_workbook(path, read_only=True, data_only=True)

            text = []

            for sheet in wb:
                for row in sheet.iter_rows(values_only=True):
                    for cell in row:
                        if cell:
                            text.append(str(cell))

            return clean_text(" ".join(text))


        if ext == ".pptx":

            prs = Presentation(path)

            text = []

            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        text.append(shape.text)

            return clean_text(" ".join(text))


        if ext == ".pdf":

            reader = PyPDF2.PdfReader(path)

            text = []

            for page in reader.pages:

                t = page.extract_text()

                if t:
                    text.append(t)

            return clean_text(" ".join(text))


        if ext == ".txt":

            with open(path, "r", encoding="utf8", errors="ignore") as f:

                return clean_text(f.read())

    except:
        return ""

    return ""


# -------------------------------------------------
# IMAGE HASH
# -------------------------------------------------

def image_hash(path):

    try:

        img = Image.open(path)

        return imagehash.phash(img)

    except:

        return None


# -------------------------------------------------
# CLUSTERING
# -------------------------------------------------

def cluster_pairs(pairs):

    graph = defaultdict(set)

    for a, b in pairs:

        graph[a].add(b)
        graph[b].add(a)

    visited = set()
    clusters = []

    for node in graph:

        if node not in visited:

            stack = [node]
            cluster = []

            while stack:

                n = stack.pop()

                if n not in visited:

                    visited.add(n)
                    cluster.append(n)

                    stack.extend(graph[n] - visited)

            clusters.append(cluster)

    return clusters


# -------------------------------------------------
# SMART RECOMMENDATION
# -------------------------------------------------

def score_file(path):

    score = 0
    reasons = []

    try:

        size = os.path.getsize(path)

        score += size
        reasons.append("larger file size")

        modified = os.path.getmtime(path)

        score += modified
        reasons.append("more recent modification")

        name = os.path.basename(path).lower()

        if "final" in name:
            score += 10000000000
            reasons.append("marked as final version")

        if "latest" in name or "v2" in name:
            score += 5000000000
            reasons.append("version indicator")

        if "copy" in name or "backup" in name:
            score -= 5000000000
            reasons.append("likely duplicate copy")

    except:
        pass

    return score, reasons


def recommend_cluster(cluster):

    scored = []

    for f in cluster:

        s, reasons = score_file(f)

        scored.append((f, s, reasons))

    scored.sort(key=lambda x: x[1], reverse=True)

    keep_file = scored[0]

    remove_files = scored[1:]

    return keep_file, remove_files


# ============================================================
# STANDARD MODE
# ============================================================

def analyze_folder(folder):

    files = []

    for root, _, names in os.walk(folder):

        for n in names:

            files.append(os.path.join(root, n))


    # SIZE FILTER

    size_groups = defaultdict(list)

    for f in files:

        try:

            size = os.path.getsize(f)

            size_groups[size].append(f)

        except:

            pass


    # EXACT DUPLICATES

    hash_groups = defaultdict(list)

    for size, group in size_groups.items():

        if len(group) < 2:
            continue

        for f in group:

            h = sha256_hash(f)

            if h:
                hash_groups[h].append(f)

    exact_duplicates = [g for g in hash_groups.values() if len(g) > 1]


    # TF-IDF SIMILARITY

    near_pairs = []

    text_files = [f for f in files if os.path.splitext(f)[1].lower() in TEXT_EXTENSIONS]

    texts = []
    valid_files = []

    for f in text_files:

        txt = extract_text(f)

        if len(txt) > 200:   # avoid short header-only docs

            texts.append(txt)

            valid_files.append(f)


    if len(texts) > 1:

        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1,2)
        )

        tfidf_matrix = vectorizer.fit_transform(texts)

        similarity_matrix = cosine_similarity(tfidf_matrix)


        for i in range(len(valid_files)):

            for j in range(i + 1, len(valid_files)):

                if similarity_matrix[i][j] >= 0.80:  # stricter threshold

                    near_pairs.append((valid_files[i], valid_files[j]))


    clusters = cluster_pairs(near_pairs)

    return exact_duplicates, clusters


# ============================================================
# CROSS FORMAT MODE
# ============================================================

def analyze_cross_format(folder):

    files = []

    for root, _, names in os.walk(folder):

        for n in names:

            files.append(os.path.join(root, n))


    near_pairs = []


    text_files = [f for f in files if os.path.splitext(f)[1].lower() in TEXT_EXTENSIONS]


    texts = []
    valid_files = []

    for f in text_files:

        txt = extract_text(f)

        if len(txt) > 200:

            texts.append(txt)

            valid_files.append(f)


    if len(texts) > 1:

        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1,2)
        )

        tfidf_matrix = vectorizer.fit_transform(texts)

        similarity_matrix = cosine_similarity(tfidf_matrix)


        for i in range(len(valid_files)):

            for j in range(i + 1, len(valid_files)):

                if similarity_matrix[i][j] >= 0.80:

                    near_pairs.append((valid_files[i], valid_files[j]))


    # IMAGE SIMILARITY

    image_files = [f for f in files if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS]

    hashes = {}

    for f in image_files:

        hashes[f] = image_hash(f)


    for i in range(len(image_files)):

        for j in range(i + 1, len(image_files)):

            f1 = image_files[i]

            f2 = image_files[j]

            h1 = hashes[f1]

            h2 = hashes[f2]

            if h1 and h2:

                similarity = 1 - ((h1 - h2) / 64)

                if similarity >= 0.8:

                    near_pairs.append((f1, f2))


    clusters = cluster_pairs(near_pairs)

    return clusters