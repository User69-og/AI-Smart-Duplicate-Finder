# AI Smart Duplicate File Finder 🚀

**SanDisk Hackathon | Track 1: AI / ML**

An intelligent storage optimization system that detects exact and semantic duplicates across various file formats.

## 🏗 Iteration 1: Current Prototype

### Core Intelligence

- **Exact Duplicate Detection:** SHA-256 binary hashing.
- **Semantic Similarity:** Cosine similarity for `.docx`, `.pptx`, `.xlsx`, and `.txt`.
- **Image Intelligence:** Perceptual hashing (pHash) with Hamming distance for visual similarity.
- **Smart Clustering:** Graph-based clustering using connected components to group related files.

### 🧠 The Recommendation Engine

The system uses a weighted scoring model to suggest the best file to **KEEP** based on:

- **File Metadata:** Size and last modified timestamps.
- **Filename Signals:** Keywords like "final", "backup", or "copy".

### 📊 Storage Analytics

- Redundancy level calculation.
- Potential storage savings (SSD optimization metric).
- Risk classification (Low/Moderate/High).

## 🛠 Tech Stack

- **Language:** Python
- **UI:** Tkinter
- **AI/ML Logic:** Scikit-learn, ImageHash, Pillow
- **Parsers:** python-docx, openpyxl, python-pptx


## 🏗 Iteration 2: Advanced Storage Intelligence (Current)
### New Features
* **Image Similarity Engine:** Added `ImageHash` integration using perceptual hashing (pHash) to detect visually similar images regardless of resolution or format.
* **PDF Intelligence:** Integrated `PyPDF2` to extract and analyze text from PDF documents for semantic matching.
* **Advanced NLP:** Implemented `scikit-learn` TF-IDF Vectorization with an N-gram range (1,2) for higher accuracy in document similarity.
* **Smart Decision Logic:** Enhanced recommendation engine with weighted scoring for "Final" versions vs. "Backup/Copy" indicators.

### Updated Tech Stack
* **New Dependencies:** `scikit-learn`, `ImageHash`, `PyPDF2`, `Pillow`.