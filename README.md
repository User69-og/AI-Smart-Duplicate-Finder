# AI Smart Duplicate File Finder 🚀

**SanDisk Hackathon | Track 1: AI / ML**

An intelligent storage optimization system that detects exact and semantic duplicates across various file formats — and safely removes them in one click.

---

## 🏗 Iteration 1: Core Prototype

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
- Risk classification (Low / Moderate / High).

### 🛠 Tech Stack

- **Language:** Python
- **UI:** Tkinter
- **AI/ML Logic:** Scikit-learn, ImageHash, Pillow
- **Parsers:** python-docx, openpyxl, python-pptx

---

## 🏗 Iteration 2: Advanced Storage Intelligence

### New Features

- **Image Similarity Engine:** Added `ImageHash` integration using perceptual hashing (pHash) to detect visually similar images regardless of resolution or format.
- **PDF Intelligence:** Integrated `PyPDF2` to extract and analyze text from PDF documents for semantic matching.
- **Advanced NLP:** Implemented `scikit-learn` TF-IDF Vectorization with an N-gram range (1, 2) for higher accuracy in document similarity.
- **Smart Decision Logic:** Enhanced recommendation engine with weighted scoring for "Final" versions vs. "Backup/Copy" indicators.

### Updated Tech Stack

- **New Dependencies:** `scikit-learn`, `ImageHash`, `PyPDF2`, `Pillow`

---

## 🏗 Iteration 3: Full AI/ML Pipeline + Complete UX

### New Features

#### 🤖 Deep AI Mode
- **Sentence Transformers (all-MiniLM-L6-v2):** Encodes documents into semantic vector embeddings to detect content duplicates even when phrasing differs entirely.
- **FAISS Vector Index:** Near-instant approximate nearest-neighbour search across thousands of document embeddings.
- **CLIP Neural Vision (ViT-B/32):** OpenAI's vision model encodes images into semantic space — finds visually duplicate images even across crops, colour changes, or resolutions.
- **CLIP + pHash Fusion:** Combines neural and perceptual scores for a more robust image similarity decision.

#### 🎵 Audio Duplicate Detection
- **MFCC Fingerprinting via `librosa`:** Extracts Mel-Frequency Cepstral Coefficients from audio files and computes cosine similarity to detect duplicate tracks across `.mp3`, `.wav`, `.flac`, `.ogg`, `.m4a` — even across bitrate differences.

#### 🗑️ One-Click Safe Deletion
- Checkboxes on every detected duplicate file in the results.
- "Delete Selected" button moves files to the **Recycle Bin** via `send2trash` — no permanent data loss.
- Exact-duplicate extras are pre-ticked automatically.

#### 📊 Scan Summary Dashboard
- Live stat cards rendered after every scan: **Files Scanned**, **Duplicates Found**, **Space Wasted**, **Exact Groups**, **Near Clusters**.

#### 💾 Export Report
- Save results as a `.txt` human-readable report or a `.csv` spreadsheet with full metadata (file path, size, modified date, similarity reason, recommended action).

#### 🖼️ File Preview Panel
- Click any file in the results to see: image thumbnail, document text snippet, or file metadata (size, modified, type) in a live side panel.

#### 🎚️ Similarity Threshold Slider
- Tune detection sensitivity live from **0.50 → 1.00** before running a scan — balance recall vs. precision for any use case.

#### 🏷️ Confidence Score Badges
- Every cluster now displays a `🎯 87% similar` badge so users understand *why* files were flagged.

#### 📂 Auto-Categorised Clusters
- Results are automatically labelled by file category: 🖼️ Images / 📝 Documents / 🎵 Audio / 📄 PDF.

#### ⚙️ Stage Progress Labels
- Real-time stage indicator shows which pipeline step is active: `📂 Scanning → 🔐 Hashing → 📝 Text AI → 🖼️ Image AI → 🎵 Audio AI → 🔗 Clustering`.

---

## 🏗 Iteration 4: Multi-Modal Acoustic Intelligence (Current Version)

### 🆕 New: Advanced Audio Fingerprinting

- **Acoustic DNA (Chromaprint):** Integrated `pyacoustid` for robust audio fingerprinting. The system can now identify the same song/recording even if one is a high-quality `.wav` and the other is a low-bitrate `.mp3`.
- **Enhanced MFCC Fallback:** Uses `librosa` to extract Mel-Frequency Cepstral Coefficients, Chroma STFT, and Beat Tracking for a secondary "texture-based" audio comparison.
- **Dual-Metric Similarity:** Combines Bit-Error Rate (BER) for fingerprints and Rescaled Cosine Similarity for spectral features.
- **Format-Agnostic Audio Detection:** Seamlessly compares across `.mp3`, `.wav`, `.flac`, `.ogg`, `.m4a`, `.aac`, and `.wma` — identifying the same audio content regardless of container or compression.

### 🔧 Enhanced Neural Pipeline

- **CLIP Vision Refinement:** Fine-tuned similarity fusion between CLIP embeddings and perceptual hashing for more accurate near-duplicate image detection.
- **FAISS Index Optimization:** Improved vector search performance for large document collections with automatic index rebuilding.

### 🛡️ Enterprise Safety & UX Polish

- **Safe Delete Confirmation:** Added confirmation dialog with storage savings preview before moving files to Recycle Bin via `send2trash`.
- **Audio Metadata Preview:** Expanded preview panel to display audio duration, bitrate, sample rate, and channels for music files.
- **Confidence Score Enhancement:** Badges now show dual metrics for audio files (🎵 92% Fingerprint + 87% Spectral).
- **Performance Optimizations:** Lazy loading for neural models and improved memory management during large scans.

---

## 🚀 Evolution History

| Iteration | Key Focus | Core Technologies |
|-----------|-----------|-------------------|
| **v1** | Foundation | SHA-256 Hashing, Basic Tkinter UI |
| **v2** | Multi-Format | PDF/Office Parsing, TF-IDF Text Similarity |
| **v3** | Deep AI | CLIP Vision, Sentence Transformers, FAISS |
| **v4** | **Acoustic AI** | **Chromaprint, Librosa MFCC, Dual-Metric Audio, Safe-Delete Logic** |

---

## 🛠 Tech Stack

| Category | Libraries |
|----------|-----------|
| **AI/ML** | `scikit-learn`, `sentence-transformers`, `faiss-cpu`, `torch`, `openai-clip` |
| **Audio Intelligence** | `librosa`, `pyacoustid` (Chromaprint), `soundfile` |
| **Computer Vision** | `Pillow`, `imagehash`, `torchvision` |
| **Document Parsing** | `PyPDF2`, `python-docx`, `openpyxl`, `python-pptx` |
| **UI & Safety** | `tkinter`, `send2trash` |

---

## ▶️ Getting Started

```bash
pip install -r requirements.txt
python desktop_app.py