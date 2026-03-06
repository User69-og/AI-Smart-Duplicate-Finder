🧠 AI Smart Duplicate File Finder

SanDisk Hackathon | Track 1: AI / ML

An intelligent, multi-modal storage optimization system that goes beyond bit-for-bit matching. It identifies exact, near, and semantic duplicates across text, images, and audio using a sophisticated four-tier AI pipeline.
🏗 Iteration 4: Multi-Modal Acoustic Intelligence (Current)
🆕 New: Advanced Audio Fingerprinting

    Acoustic DNA (Chromaprint): Integrated pyacoustid to generate robust audio fingerprints. It identifies identical recordings even across different bitrates or formats (e.g., comparing a .wav master to a mobile-compressed .mp3).

    Enhanced MFCC Fallback: Utilizes librosa to extract Mel-Frequency Cepstral Coefficients (MFCCs), Chroma STFT, and Spectral Centroids. This allows the AI to "hear" similarities in texture and timbre even if the files aren't binary matches.

    Dual-Metric Similarity: Implements a hybrid scoring system using Bit-Error Rate (BER) for fingerprints and Rescaled Cosine Similarity for spectral feature vectors.

🤖 Deep AI & Neural Vision

    Sentence Transformers (all-MiniLM-L6-v2): Encodes documents into semantic vector space, detecting duplicates even when the wording is significantly altered.

    FAISS Vector Indexing: Powered by Facebook AI Similarity Search for lightning-fast approximate nearest-neighbor lookups.

    CLIP Neural Vision (ViT-B/32): OpenAI’s vision model identifies visually duplicate images across different crops, resolutions, or color profiles.

🛡️ Enterprise-Grade UX & Safety

    One-Click Safe Delete: Uses send2trash to ensure all deletions are non-destructive (moved to Recycle Bin).

    Live Analytics Dashboard: Real-time stat cards for Files Scanned, Space Wasted, and Redundancy Risk Classification.

    Confidence Badges: Every cluster is labeled with a 🎯 Similarity Score (e.g., 92% Match).

    File Preview Suite: Instant side-panel previews for image thumbnails, text snippets, and audio metadata.

🚀 Project Evolution
Iteration 3: Full AI/ML Pipeline + Complete UX

    Neural Integration: Sentence Transformers and FAISS added for semantic document clustering.

    Vision AI: Implementation of CLIP for cross-modal image similarity.

    UX Overhaul: Added the Similarity Threshold Slider, Stage Progress Labels, and Auto-categorized clusters.

Iteration 2: Advanced Storage Intelligence

    Multi-Format Extraction: Added PyPDF2, python-docx, and openpyxl to "read" inside various file types.

    Advanced NLP: Implemented scikit-learn TF-IDF Vectorization with an N-gram range (1, 2).

    Extended Images: Integrated ImageHash for perceptual hashing (pHash).

Iteration 1: Prototype Foundation

    Exact Matching: Cryptographic SHA-256 binary hashing.

    Recommendation Engine: Initial weighted scoring model based on file size, timestamps, and naming signals (e.g., "final" vs "copy").

    UI Foundation: Basic Tkinter-based desktop interface.

🛠 Tech Stack

    Acoustic AI: librosa, pyacoustid, soundfile

    Neural Vision: openai-clip, torch, torchvision, ImageHash

    Deep NLP: sentence-transformers, faiss-cpu, scikit-learn

    File Parsers: PyPDF2, python-docx, openpyxl, python-pptx

    UI/Safety: tkinter, send2trash, Pillow

📦 Getting Started

    Install Dependencies:
    Bash

    pip install -r requirements.txt

    Note: Audio fingerprinting requires the fpcalc binary installed on your system PATH.

    Run the Application:
    Bash

    python desktop_app.py

🎯 Hackathon Pitch

    "Storage is cheap, but finding what's wasting it is hard. Our tool provides Acoustic, Visual, and Semantic Intelligence to identify duplicate content regardless of file format. It is the intelligent decision-making layer SanDisk users need to optimize high-capacity drives with total safety and AI precision."