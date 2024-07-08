import fitz  # PyMuPDF

def find_summary_paragraph(pdf_path, summary_keywords):
    # Open the provided PDF file
    pdf_document = fitz.open(pdf_path)
    
    summary_paragraph = None
    
    # Iterate through pages
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text = page.get_text()
        
        # Split text into paragraphs
        paragraphs = text.split('\n\n')
        
        # Check each paragraph for summary keywords
        for para in paragraphs:
            if any(keyword in para.lower() for keyword in summary_keywords):
                summary_paragraph = para
                break
        if summary_paragraph:
            break
    
    # Close the PDF document
    pdf_document.close()
    
    return summary_paragraph

if __name__ == "__main__":
    # Path to the PDF file you want to process
    pdf_path = '1.pdf'
    
    # Keywords that indicate a summary
    summary_keywords = ["summary", "conclusion", "abstract", "concluding remarks"]
    
    # Find and display the summary paragraph
    summary_paragraph = find_summary_paragraph(pdf_path, summary_keywords)
    
    if summary_paragraph:
        print("Summary Paragraph:")
        print(summary_paragraph)
    else:
        print("No summary paragraph found.")
