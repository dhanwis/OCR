import pytesseract
import cv2
import os
from dotenv import load_dotenv
import re
import spacy
import pdfplumber       

load_dotenv()

tesseract_path = os.getenv(r'MY_PATH')
pytesseract.pytesseract.tesseract_cmd = tesseract_path

def text_from_image(path) :

    file_extension = os.path.splitext(path)[1].lower()

    if file_extension in ['.jpg', '.jpeg', '.png', '.webp']:
        # Extract text using pytesseract for images
        img = cv2.imread(path)
        if img is None:
            raise ValueError(f"Unable to read the image file: {path}")
        extracted_text = pytesseract.image_to_string(img)

    elif file_extension == '.pdf':
        # Extract text using pdfplumber for PDFs
        extracted_text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text
    else:
        raise ValueError("Unsupported file type. Provide an image or PDF.")

    # extracting mobile no
    pattern=r'\b\d{10}\b'
    mobile_nos = re.findall(pattern, extracted_text)


    #extracting email
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(pattern, extracted_text)

    pattern = r'\b(?:(0[1-9]|[12][0-9]|3[01])[-/.](0[1-9]|1[0-2])[-/.](\d{4})|' \
              r'(0[1-9]|1[0-2])[-/.](0[1-9]|[12][0-9]|3[01])[-/.](\d{4})|' \
              r'(\d{4})[-/.](0[1-9]|1[0-2])[-/.](0[1-9]|[12][0-9]|3[01]))\b'

    matches = re.findall(pattern, extracted_text)

    #extracting dates
    dates = []
    
    for match in matches:
        if match[0]:  # DD/MM/YYYY or DD-MM-YYYY or DD.MM.YYYY
            dates.append(f"{match[0]}/{match[1]}/{match[2]}")
        elif match[3]:  # MM/DD/YYYY or MM-DD-YYYY or MM.DD.YYYY
            dates.append(f"{match[3]}/{match[4]}/{match[5]}")
        elif match[6]:  # YYYY-MM-DD or YYYY.MM.DD
            dates.append(f"{match[6]}-{match[7]}-{match[8]}")

    # extracting person's names, organization names
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(extracted_text)
    person_names = [(ent.text, ent.label_) for ent in doc.ents if ent.label_ == "PERSON"]

    # extracting invoice numbers
    patterns = [
        r'\b(?:INV|Invoice|Bill)[-:\s]?\d{1,5}\b',  # Example: INV123, Invoice 2214, Bill-98765
        r'\bINV-\d{4}-\d{1,5}\b'                    # Example: INV-2023-456
    ]

    # Search for all patterns in the text
    invoice_numbers = []
    for pattern in patterns:
        matches = re.findall(pattern, extracted_text, re.IGNORECASE)
        invoice_numbers.extend(matches)

    # pattern = r'\b(?:USD|INR|EUR|₹|\$|€)\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b'
    pattern = r'(?:(?:USD|INR|EUR|₹|\$|€)\s?)?\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b'
    
    # Search for all matches in the text
    potential_prices = re.findall(pattern, extracted_text)
    
    # Filtering to ensure only prices with currency symbols are included
    filtered_prices = [
        price for price in potential_prices 
        if re.match(r'^(?:USD|INR|EUR|₹|\$|€)\s*\d', price)  # Check if it starts with a currency symbol followed by a number
    ]

    return mobile_nos, emails, dates, person_names, invoice_numbers, filtered_prices

mobile_nos, emails, dates, names, invoice, prices = text_from_image(r"document path")
print("mobile_no - ", mobile_nos)
print("Emails - ", emails)
print("Dates - ", dates)
print("Names - ", names)   
print("Invoice - ", invoice)
print("Prices - ", prices)