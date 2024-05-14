import streamlit as st
import pydicom
from PIL import Image
import easyocr
import numpy as np
import json

def load_dicom(file):
    ds = pydicom.dcmread(file)
    img_array = ds.pixel_array
    img_array = (np.maximum(img_array, 0) / img_array.max()) * 255.0
    img = Image.fromarray(np.uint8(img_array)).convert('RGB')
    
    img_cropped = img.crop((1050, 700, 1500, 950))
    return img_cropped

reader = easyocr.Reader(['en'], gpu=False )

def perform_ocr(img):
    img = np.array(img)
    result = reader.readtext(img)
    text = "\n".join([line[1] for line in result])
    return text

def parse_ocr_output(input_string):
    parts = input_string.split('\n')
    parts = parts[3:]  # Assuming you need to remove initial three labels
    results = {}
    for i in range(0, len(parts), 4):
        prefix = parts[i]
        results[f"{prefix}_EF"] = parts[i + 1]
        results[f"{prefix}_UR"] = parts[i + 2]
        results[f"{prefix}_Frame"] = parts[i + 3]
    return results

# Streamlit interface
st.title('DICOM OCR Extractor')
uploaded_file = st.file_uploader("Choose a DICOM file", type=["dcm"])

if uploaded_file is not None:
    img = load_dicom(uploaded_file)
    st.image(img, caption='Loaded DICOM image', use_column_width=True)
    ocr_text = perform_ocr(img)
    st.write("OCR Text:")
    st.text_area("Extracted Text", ocr_text, height=150)

    # Parse OCR text to JSON
    if ocr_text.strip():  # Check if the OCR text is not just empty or whitespace
        results_json = parse_ocr_output(ocr_text)
        st.write("Extracted JSON:")
        st.json(results_json)
        
        # Convert JSON to string
        json_str = json.dumps(results_json, indent=4)
        # Create a download button for the JSON data
        st.download_button(
            label="Download JSON",
            data=json_str,
            file_name="ocr_results.json",
            mime="application/json"
        )
