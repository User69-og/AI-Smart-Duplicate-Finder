import os
import re
import math
from collections import defaultdict, Counter
from docx import Document
from openpyxl import load_workbook
from pptx import Presentation
from PIL import Image
import imagehash

TEXT_EXTENSIONS = {
    ".txt", ".md", ".csv", ".log",
    ".docx", ".xlsx", ".pptx"
}

IMAGE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".bmp", ".gif"
}

# -----------------------------
# TEXT EXTRACTION
# -----------------------------

def extract_text(path):

    ext = os.path.splitext(path)[1].lower()

    try:

        if ext == ".docx":
            doc = Document(path)
            return " ".join(p.text for p in doc.paragraphs)

        if ext == ".xlsx":
            wb = load_workbook(path, read_only=True, data_only=True)

            text = []

            for sheet in wb:
                for row in sheet.iter_rows(values_only=True):
                    for cell in row:
                        if cell:
                            text.append(str(cell))

            return " ".join(text)

        if ext == ".pptx":

            prs = Presentation(path)

            text = []

            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        text.append(shape.text)

            return " ".join(text)

        if ext == ".txt":
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

    except:
        return ""

    return ""


# -----------------------------
# TEXT SIMILARITY
# -----------------------------

def preprocess(text):

    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    return text.split()


def cosine_similarity(t1, t2):

    tokens1 = preprocess(t1)
    tokens2 = preprocess(t2)

    if not tokens1 or not tokens2:
        return 0

    vec1 = Counter(tokens1)
    vec2 = Counter(tokens2)

    intersection = set(vec1) & set(vec2)

    numerator = sum(vec1[x] * vec2[x] for x in intersection)

    sum1 = sum(v ** 2 for v in vec1.values())
    sum2 = sum(v ** 2 for v in vec2.values())

    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if denominator == 0:
        return 0

    return numerator / denominator


# -----------------------------
# IMAGE SIMILARITY
# -----------------------------

def image_hash(path):

    try:
        img = Image.open(path)
        return imagehash.phash(img)

    except:
        return None


def image_similarity(hash1, hash2):

    if hash1 is None or hash2 is None:
        return 0

    distance = hash1 - hash2

    similarity = 1 - (distance / 64)

    return similarity


# -----------------------------
# CLUSTERING
# -----------------------------

def cluster_pairs(pairs):

    graph = defaultdict(set)

    for f1, f2 in pairs:
        graph[f1].add(f2)
        graph[f2].add(f1)

    visited = set()
    clusters = []

    for node in graph:

        if node not in visited:

            stack = [node]
            cluster = []

            while stack:

                current = stack.pop()

                if current not in visited:
                    visited.add(current)
                    cluster.append(current)
                    stack.extend(graph[current] - visited)

            clusters.append(cluster)

    return clusters


# -----------------------------
# SMART RECOMMENDATION
# -----------------------------

def score_file(path):

    score = 0
    explanation = []

    try:

        size = os.path.getsize(path)
        score += size
        explanation.append("larger file size")

        modified = os.path.getmtime(path)
        score += modified
        explanation.append("recently modified")

        name = os.path.basename(path).lower()

        if "final" in name:
            score += 10000000000
            explanation.append("marked as final version")

        if "copy" in name or "backup" in name:
            score -= 5000000000
            explanation.append("likely duplicate copy")

    except:
        pass

    return score, explanation


def recommend_cluster(cluster):

    scored = []

    for f in cluster:
        s, exp = score_file(f)
        scored.append((f, s, exp))

    scored.sort(key=lambda x: x[1], reverse=True)

    keep = scored[0]
    remove = scored[1:]

    return keep, remove


# =====================================================
# STANDARD MODE (same format)
# =====================================================

def analyze_folder(folder):

    files = []

    for root, _, names in os.walk(folder):
        for n in names:
            files.append(os.path.join(root, n))

    near_pairs = []

    for i in range(len(files)):
        for j in range(i + 1, len(files)):

            f1 = files[i]
            f2 = files[j]

            ext1 = os.path.splitext(f1)[1].lower()
            ext2 = os.path.splitext(f2)[1].lower()

            if ext1 != ext2:
                continue

            if ext1 in TEXT_EXTENSIONS:

                sim = cosine_similarity(
                    extract_text(f1),
                    extract_text(f2)
                )

                if sim >= 0.50:
                    near_pairs.append((f1, f2))

            if ext1 in IMAGE_EXTENSIONS:

                h1 = image_hash(f1)
                h2 = image_hash(f2)

                sim = image_similarity(h1, h2)

                if sim >= 0.80:
                    near_pairs.append((f1, f2))

    clusters = cluster_pairs(near_pairs)

    return clusters


# =====================================================
# CROSS FORMAT MODE
# =====================================================

def analyze_cross_format(folder):

    files = []

    for root, _, names in os.walk(folder):
        for n in names:
            files.append(os.path.join(root, n))

    near_pairs = []

    # TEXT FILES

    text_files = [
        f for f in files
        if os.path.splitext(f)[1].lower() in TEXT_EXTENSIONS
    ]

    for i in range(len(text_files)):
        for j in range(i + 1, len(text_files)):

            f1 = text_files[i]
            f2 = text_files[j]

            sim = cosine_similarity(
                extract_text(f1),
                extract_text(f2)
            )

            if sim >= 0.60:
                near_pairs.append((f1, f2))

    # IMAGE FILES

    image_files = [
        f for f in files
        if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS
    ]

    hashes = {}

    for f in image_files:
        hashes[f] = image_hash(f)

    for i in range(len(image_files)):
        for j in range(i + 1, len(image_files)):

            f1 = image_files[i]
            f2 = image_files[j]

            sim = image_similarity(hashes[f1], hashes[f2])

            if sim >= 0.80:
                near_pairs.append((f1, f2))

    clusters = cluster_pairs(near_pairs)

    return clusters