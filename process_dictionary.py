
import pdfplumber
import json
from tqdm import tqdm
import re
import collections

def is_arabic(text):
    """Checks if a string contains Arabic characters."""
    return bool(re.search(r'[\u0600-\u06FF]', text))

def clean_text(text, is_arabic_text=False):
    """Removes common noise, extraneous characters, and ensures consistent spacing."""
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r'^[^\w\s]+|[^\w\s]+$', '', text)
    text = re.sub(r'[\*■\d]', '', text).strip()
    if is_arabic_text:
        text = text.replace(':', '')
    return text.strip()

def process_page_to_json(page):
    """
    Processes a single page of the dictionary PDF, extracting and cleaning words to structure them into JSON.
    This version uses indentation-based logic to handle multi-line entries.
    """
    words = page.extract_words(x_tolerance=1, y_tolerance=1, keep_blank_chars=False)

    page_midpoint = page.width / 2
    entries = []

    left_column_words = sorted([w for w in words if w['x0'] < page_midpoint], key=lambda w: (w['top'], w['x0']))
    right_column_words = sorted([w for w in words if w['x0'] >= page_midpoint], key=lambda w: (w['top'], w['x0']))

    def create_entries_from_column(column_words):
        """Processes a list of words from a single column to create dictionary entries using indentation logic."""
        if not column_words:
            return []

        # Determine the left margin of the column for indentation detection
        left_margin = min(w['x0'] for w in column_words)
        indentation_tolerance = 5  # How much space counts as an indent vs. a new entry

        # Group words into lines with a vertical tolerance
        lines = []
        if column_words:
            current_line_words = [column_words[0]]
            for word in column_words[1:]:
                if abs(word['top'] - current_line_words[-1]['top']) < 5:
                    current_line_words.append(word)
                else:
                    lines.append(sorted(current_line_words, key=lambda w: w['x0']))
                    current_line_words = [word]
            lines.append(sorted(current_line_words, key=lambda w: w['x0']))

        column_entries = []
        current_entry = None

        for line_words in lines:
            # Check if the line starts near the left margin (new entry) or is indented (continuation)
            is_new_entry_start = line_words[0]['x0'] < left_margin + indentation_tolerance

            indonesian_words, arabic_words = [], []
            found_arabic = False
            for word in line_words:
                if not found_arabic and is_arabic(word['text']):
                    found_arabic = True
                (arabic_words if found_arabic else indonesian_words).append(word['text'])

            indonesian_part = clean_text(" ".join(indonesian_words))
            arabic_part = clean_text(" ".join(arabic_words), is_arabic_text=True)

            if is_new_entry_start:
                if current_entry and current_entry.get('indonesian') and current_entry.get('arabic'):
                    column_entries.append(current_entry)
                current_entry = {"indonesian": indonesian_part, "arabic": arabic_part}
            else:  # Continuation line
                if current_entry:
                    current_entry["indonesian"] = (current_entry.get("indonesian", "") + " " + indonesian_part).strip()
                    current_entry["arabic"] = (current_entry.get("arabic", "") + " " + arabic_part).strip()

        if current_entry and current_entry.get('indonesian') and current_entry.get('arabic'):
            column_entries.append(current_entry)

        return column_entries

    entries.extend(create_entries_from_column(left_column_words))
    entries.extend(create_entries_from_column(right_column_words))

    return entries

def main():
    """
    Main function to process the Arabic-Indonesian dictionary PDF and save it as a clean JSON file.
    """
    pdf_path = "pdf/arabic-dictionary.pdf"
    all_entries = []
    num_pages_to_process = 20

    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = min(num_pages_to_process, len(pdf.pages))

            for i in tqdm(range(total_pages), desc="Processing pages"):
                page = pdf.pages[i]
                page_entries = process_page_to_json(page)
                all_entries.extend(page_entries)

        unique_entries = [dict(t) for t in {tuple(d.items()) for d in all_entries if d.get("indonesian") and d.get("arabic")}]

        output_path = "dictionary_data_clean.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(unique_entries, f, ensure_ascii=False, indent=2)

        print(f"Clean, structured data extraction complete. Output saved to {output_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
