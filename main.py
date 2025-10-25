import time
from PyPDF2 import PdfReader

pdf_files = [
    'sample1.pdf',
    'sample2.pdf',
    'arabic-dictionary.pdf'
]

def extract_text_from_pdf(pdf_file: str) -> [str]:
    print("Reading the PDF...")
    pdf = f"pdf/{pdf_file}"
    
    # 1. Start the timer before reading the file
    start_time = time.time()
    
    try:
        reader = PdfReader(pdf) # read pdf file
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return []

    if reader.is_encrypted:
        print('PDF encrypted')
        # Note: If the file is encrypted, you may need to call reader.decrypt('password') 
        # as discussed in the previous response, before accessing pages.
        
    print(f'Encrypt status: {reader.is_encrypted}')
    pdf_text = [] # list for pdf text we're going to extract

    print(f"PDF total pages: {len(reader.pages)}")
    print("Extracting the PDF...")
    
    # 2. Start a separate timer for just the extraction loop
    extraction_start_time = time.time()
    
    for page in reader.pages:
        content = page.extract_text()
        pdf_text.append(content)

    # 3. Stop the extraction timer
    extraction_end_time = time.time()
    
    print("PDF text extracted!")
    
    # 4. Calculate and print the elapsed times
    extraction_time = extraction_end_time - extraction_start_time
    total_time = extraction_end_time - start_time
    
    print("-" * 30)
    print(f"Time to read PDF (open/parse): {extraction_start_time - start_time:.4f} seconds")
    print(f"Time to extract text from {len(reader.pages)} pages: {extraction_time:.4f} seconds")
    print(f"Total elapsed time: {total_time:.4f} seconds")
    print("-" * 30)

    return pdf_text

def clean_dictionary_pages(extracted_pages: list[str]) -> str:
    cleaned_content = []
    
    # Define patterns you want to remove from the start of each page
    # This is based on the screenshot showing page headers like 'ا ب', 'ا', 'آب', 'آد', and page numbers ('١').
    # You'll need to expand this list after inspecting a few more pages.
    HEADER_PATTERNS = [
        'ا ب', 'آ ب', 'ب', 'ا ', 'ا د', 'آ د', # Common Arabic letters/headers
        '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩', '٠', # Page numbers (Arabic numerals)
    ]

    for page_text in extracted_pages:
        lines = page_text.split('\n')
        
        # 1. Strip and remove empty lines
        lines = [line.strip() for line in lines if line.strip()]

        # 2. Iterate and remove headers/footers (usually the first and last few lines)
        cleaned_lines = []
        
        # Simple removal of the first few lines that match a header pattern
        i = 0
        while i < len(lines):
            line = lines[i]
            is_header = False
            for pattern in HEADER_PATTERNS:
                if line.startswith(pattern):
                    # Check if the line is *only* the header pattern (e.g., 'ا ب')
                    if len(line.split()) < 3 and len(line) < 10:
                        is_header = True
                        break
            
            # If it's a short line that is likely a header or page number, skip it
            if is_header:
                i += 1
            else:
                cleaned_lines.append(line)
                i += 1
                
        # 3. Join the remaining lines and append to the result
        cleaned_content.append('\n'.join(cleaned_lines))

    # Join all pages back into one large string for the model
    return '\n'.join(cleaned_content)

def chunk_text_by_entry(cleaned_text: str) -> list[str]:
    # Placeholder: You'll need to find the specific pattern for a new entry.
    # For a dictionary, this might be a specific header, bullet point, or dash.
    
    # Simple example: Split by three newlines, assuming entries are separated by large gaps.
    # You might need a regex to look for a specific entry format, e.g., r'\n\n[A-Z]'
    
    chunks = cleaned_text.split('\n\n\n')
    
    # Filter out any very small or empty chunks that result from the split
    return [chunk.strip() for chunk in chunks if len(chunk.strip()) > 50]

if __name__ == '__main__':
    print('Choose the PDF will be extracted:')
    for i in range(len(pdf_files)):
        pdf = pdf_files[i]
        print(f'{i + 1}. {pdf}')
    print('Note: Type using the number (1, 2, etc)')
    number_input = int(input())
    if number_input > (len(pdf_files)) or number_input == 0:
        print("Option doesn't exists")
        exit()
    selected_pdf_file = pdf_files[number_input - 1]
    print(f"{selected_pdf_file} selected")
    extracted_text = extract_text_from_pdf(selected_pdf_file)
    
    # clean the text
    cleaned_dictionary_content = clean_dictionary_pages(extracted_text)

    print("\n--------------CLEANED RESULT (First 1000 Chars)--------------")
    print(cleaned_dictionary_content[:1000]) # Print only the first part to check the cleaning
    print(f"\nTotal Cleaned Characters: {len(cleaned_dictionary_content)}")