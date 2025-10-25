import time
import os
from PyPDF2 import PdfReader

class PDFProcessor:
    """
    Handles extraction, cleaning, and chunking of text from a single PDF file,
    optimized for dictionary-style content.
    """
    
    PDF_DIR = "pdf"
    
    # Define patterns for common headers/page numbers found in Arabic/Indonesian dictionary layout
    HEADER_PATTERNS = [
        'ا ب', 'آ ب', 'ب', 'ا ', 'ا د', 'آ د', # Arabic character range headers
        '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩', '٠', # Arabic numerals
    ]

    def __init__(self, pdf_file_name: str):
        self.pdf_file_name = pdf_file_name
        self.pdf_path = os.path.join(self.PDF_DIR, self.pdf_file_name)

    def extract_text_from_pdf(self) -> list[str]:
        """Extracts text page by page from the PDF file."""
        print(f"\n--- Starting Extraction for {self.pdf_file_name} ---")
        print("Reading the PDF...")
        
        start_time = time.time()
        
        try:
            if not os.path.exists(self.pdf_path):
                print(f"Error: PDF file not found at {self.pdf_path}")
                return []
                
            reader = PdfReader(self.pdf_path)
        except Exception as e:
            print(f"Error opening PDF: {e}")
            return []

        if reader.is_encrypted:
            print('PDF encrypted. Attempting to decrypt with empty password...')
            # Attempt to decrypt, assuming PyCryptodome is installed for AES
            try:
                 reader.decrypt("")
            except Exception as e:
                 print(f"Failed to decrypt PDF: {e}")
                 return []
            
        print(f'Encrypt status: {reader.is_encrypted}')
        pdf_text = [] 

        print(f"PDF total pages: {len(reader.pages)}")
        print("Extracting the PDF...")
        
        extraction_start_time = time.time()
        
        for i, page in enumerate(reader.pages):
            try:
                content = page.extract_text()
                if content:
                    pdf_text.append(content)
            except Exception as e:
                print(f"Warning: Could not extract text from page {i+1}. Error: {e}")
                
        extraction_end_time = time.time()
        
        print("PDF text extracted!")
        
        # Calculate and print the elapsed times
        extraction_time = extraction_end_time - extraction_start_time
        total_time = extraction_end_time - start_time
        
        print("-" * 30)
        print(f"Time to read PDF (open/parse): {extraction_start_time - start_time:.4f} seconds")
        print(f"Time to extract text from {len(pdf_text)} pages: {extraction_time:.4f} seconds")
        print(f"Total elapsed time: {total_time:.4f} seconds")
        print("-" * 30)

        return pdf_text

    def clean_dictionary_pages(self, extracted_pages: list[str]) -> str:
        """Cleans page headers and footers from the extracted dictionary content."""
        if not extracted_pages:
            return ""
            
        print("Cleaning extracted text...")
        cleaned_content = []
        
        for page_text in extracted_pages:
            lines = page_text.split('\n')
            
            # 1. Strip and remove truly empty lines
            lines = [line.strip() for line in lines if line.strip()]

            cleaned_lines = []
            i = 0
            while i < len(lines):
                line = lines[i]
                is_header = False
                
                # Check for patterns defined in the class
                for pattern in self.HEADER_PATTERNS:
                    if line.startswith(pattern) or line.endswith(pattern):
                        # Heuristic: Check if the line is short (likely header/page number)
                        if len(line.split()) < 3 and len(line) < 15: 
                            is_header = True
                            break
                
                if is_header:
                    i += 1
                else:
                    cleaned_lines.append(line)
                    i += 1
                    
            cleaned_content.append('\n'.join(cleaned_lines))

        # Join all pages back into one large string
        return '\n'.join(cleaned_content)

    def chunk_text_by_entry(self, cleaned_text: str) -> list[str]:
        """Splits the cleaned text into smaller chunks, trying to preserve dictionary entries."""
        if not cleaned_text:
            return []
            
        print("Chunking text into entries...")
        
        # Heuristic based on typical dictionary formatting: entries separated by multiple newlines
        chunks = cleaned_text.split('\n\n\n')
        
        # Filter out any very small or empty chunks that result from the split
        valid_chunks = [chunk.strip() for chunk in chunks if len(chunk.strip()) > 50]
        
        return valid_chunks

    def process_pdf_to_chunks(self) -> list[str]:
        """Orchestrates the entire process: extract -> clean -> chunk."""
        
        extracted_pages = self.extract_text_from_pdf()
        if not extracted_pages:
            return []
            
        cleaned_content = self.clean_dictionary_pages(extracted_pages)
        if not cleaned_content:
            return []
            
        dictionary_entries = self.chunk_text_by_entry(cleaned_content)
        
        print(f"Text successfully chunked into {len(dictionary_entries)} entries/chunks.")
        print("\n-------------- CLEANED & CHUNKED PREVIEW (First 1000 Chars) --------------")
        print(cleaned_content[:1000]) 
        print(f"\nTotal Cleaned Characters: {len(cleaned_content)}")
        
        return dictionary_entries
