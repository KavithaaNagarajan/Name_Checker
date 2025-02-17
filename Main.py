import streamlit as st
import os
from pdf2image import convert_from_path
import pytesseract
import cv2
import numpy as np
import tempfile

# Set Poppler path (Poppler should be installed on your machine for PDF-to-image conversion)
poppler_path = r"C:\Program Files\poppler-24.08.0\Library\bin"  # Update this to your Poppler path
os.environ["PATH"] += os.pathsep + poppler_path

# Set Tesseract OCR path (Windows users must specify the path)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(image):
    """Extract text from an image using OCR"""
    img = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    text = pytesseract.image_to_string(gray)  # Perform OCR
    return text.lower()  # Convert the text to lowercase

def extract_text_from_pdf(pdf):
    """Extract text from a PDF file by converting pages to images"""
    # Save the uploaded PDF temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(pdf.read())
        temp_pdf_path = temp_pdf.name

    # Convert PDF to images using poppler
    pages = convert_from_path(temp_pdf_path, poppler_path=poppler_path)
    full_text = ""
    for page in pages:
        img = np.array(page)
        text = pytesseract.image_to_string(img)
        full_text += text + "\n"
    
    # Clean up the temporary file
    os.remove(temp_pdf_path)

    return full_text.lower()  # Convert the text to lowercase

def find_name_in_text(text, name):
    """Find the name in the extracted text and return its sequence & line"""
    lines = text.split("\n")  # Split text into lines
    words = text.split()  # Split text into words
    name_parts = name.lower().split()  # Convert the name to lowercase and split into individual words
    positions = []
    found_line = ""

    # Finding word sequence
    for i in range(len(words) - len(name_parts) + 1):
        if words[i:i + len(name_parts)] == name_parts:
            positions.append(i + 1)  # Convert to 1-based index

    # Finding the exact line where the name appears
    for line in lines:
        if name.lower() in line:  # Ensure both the text and name are in lowercase for comparison
            found_line = line.strip()
            break

    # Display results
    if positions:
        st.success(f"✅ Name '{name}' found in the document.")
        st.write(f"🔢 Word sequence position(s): {positions}")
        st.write(f"📌 Name appears in this line: \"{found_line}\"")
    else:
        st.error(f"❌ Name '{name}' not found in the document.")

def main():
    """Main function to process image or PDF and find the name sequence & line"""
    st.title("Text Extraction from Images and PDFs")
    
    # Upload file
    uploaded_file = st.file_uploader("Choose a PDF or Image file", type=["pdf", "png", "jpg", "jpeg"])
    
    # Name input
    name_to_find = st.text_input("Enter the name to search for", "ntombifuthi")

    if uploaded_file is not None:
        # Determine file type
        if uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
            # If it's an image, process it directly
            extracted_text = extract_text_from_image(uploaded_file)
        elif uploaded_file.type == "application/pdf":
            # If it's a PDF, convert it to images first, then process
            extracted_text = extract_text_from_pdf(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload an image or PDF.")
            return

        # Find name in the extracted text
        find_name_in_text(extracted_text, name_to_find)

if __name__ == "__main__":
    main()
