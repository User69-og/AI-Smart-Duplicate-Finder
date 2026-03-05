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
