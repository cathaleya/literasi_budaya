# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "PyMuPDF",
# ]
# ///

import fitz  # PyMuPDF
import os

pdf_path = "Buku_Saku_Literasi_Budaya_Gabungan.pdf"
output_dir = "flipbook_frontend/pages"

print(f"Membuka {pdf_path}...")
try:
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    print(f"Ditemukan {total_pages} halaman.")
    
    # We want to optimize the resolution for web viewing. 
    # Zoom of 2.0 roughly gives a good quality image without being excessively huge.
    zoom_x = 2.0
    zoom_y = 2.0
    mat = fitz.Matrix(zoom_x, zoom_y)
    
    for i in range(total_pages):
        page = doc.load_page(i)
        pix = page.get_pixmap(matrix=mat)
        
        # Save as JPG for smaller file size
        output_file = os.path.join(output_dir, f"page_{i+1}.jpg")
        pix.save(output_file)
        
        if (i+1) % 10 == 0 or (i+1) == total_pages:
            print(f"Berhasil mengekstrak {i+1} dari {total_pages} halaman...")
            
    print("Selesai mengekstrak semua halaman!")
except Exception as e:
    print(f"Error: {e}")
