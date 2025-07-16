## pdf2clip

**copy any page of a PDF straight to the macOS clipboard with one click.**
* minimal interface
* quic workflow

### quick start:

**drag‑and‑drop:**
1. grab `dist/pdf2clip.app` (universal 2 binary).  
2. drop it into `/Applications`.  
3. double‑click → pick a PDF → copy.

**source:**
* run through the virtual environment
* rebuild instructions in ```setup.py```

**meant for personal use, your mileage may vary**

### dependencies:
* uses **Tkinter** for GUI
* uses **PyMuPDF** for PDF handling
* uses **pyobjc‑framework‑AppKit** for MacOS interactions
* uses **Pillow** for image handling
* uses **py2app** for ```.app``` packaging.

**dependencies should be handled automatically by py2app**