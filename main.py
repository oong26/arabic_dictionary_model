from classes.pdf_processor import PDFProcessor
from classes.model_builder import ModelBuilder

pdf_files = [
    'sample1.pdf',
    'sample2.pdf',
    'arabic-dictionary.pdf'
]

if __name__ == '__main__':
    print('Choose the PDF will be extracted:')
    for i in range(len(pdf_files)):
        pdf = pdf_files[i]
        print(f'{i + 1}. {pdf}')
    print('Note: Type using the number (1, 2, 3)')
    number_input = int(input())
    if number_input > (len(pdf_files)) or number_input == 0:
        print("Option doesn't exists")
        exit()
    selected_pdf_file = pdf_files[number_input - 1]
    print(f"{selected_pdf_file} selected")

    processor = PDFProcessor(selected_pdf_file)
    extracted_text = processor.extract_text_from_pdf()
    
    # clean the text
    cleaned_dictionary_content = processor.clean_dictionary_pages(extracted_text)
    
    # chunk text
    dictionary_entries = processor.chunk_text_by_entry(cleaned_dictionary_content)

    # Confirmation to save into model or no
    print("Are you want to save that extracted text into model? (Y/N)")
    answer = input().lower()
    if answer == 'y':
        model_name = selected_pdf_file.replace('.pdf', '')
        ModelBuilder.create_and_save_embeddings(chunks=dictionary_entries, model_filename=model_name)
    print("Finish")
    exit()