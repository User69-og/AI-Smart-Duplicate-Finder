import streamlit as st
import os
import hashlib
from collections import defaultdict

st.set_page_config(page_title="Smart Duplicate File Finder", layout="wide")

st.title("🧠 Smart Duplicate File Finder")
st.write("Browser-based tool to find duplicate files and reclaim storage space.")

def file_hash(path, block_size=65536):
    hasher = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            hasher.update(block)
    return hasher.hexdigest()

def find_duplicates(folder):
    size_map = defaultdict(list)

    for root, _, files in os.walk(folder):
        for name in files:
            path = os.path.join(root, name)
            try:
                size = os.path.getsize(path)
                size_map[size].append(path)
            except:
                pass

    duplicates = defaultdict(list)
    total_wasted_space = 0

    for size, files in size_map.items():
        if len(files) > 1:
            hash_map = defaultdict(list)
            for file in files:
                try:
                    h = file_hash(file)
                    hash_map[h].append(file)
                except:
                    pass

            for group in hash_map.values():
                if len(group) > 1:
                    duplicates[group[0]].extend(group)
                    total_wasted_space += size * (len(group) - 1)

    return duplicates, total_wasted_space

folder_path = st.text_input("📁 Enter folder path to scan")

if st.button("🔍 Scan for Duplicates"):
    if not folder_path or not os.path.exists(folder_path):
        st.error("Please enter a valid folder path.")
    else:
        with st.spinner("Scanning files..."):
            duplicates, wasted_space = find_duplicates(folder_path)

        if not duplicates:
            st.success("🎉 No duplicate files found!")
        else:
            st.warning(f"⚠️ Duplicate Groups Found: {len(duplicates)}")
            st.info(f"💾 Potential Space Saved: {wasted_space / (1024*1024):.2f} MB")

            for i, group in enumerate(duplicates.values(), 1):
                st.subheader(f"Duplicate Group {i}")
                for file in group:
                    st.code(file)
