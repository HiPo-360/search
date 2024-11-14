# import fitz  # PyMuPDF
# import re

# def find_summary_paragraph(pdf_path, summary_keywords):
#     # Open the provided PDF file
#     pdf_document = fitz.open(pdf_path)
    
#     summary_paragraph = None
#     highest_score = 0  # To track the best matching paragraph
    
#     # Iterate through pages
#     for page_num in range(len(pdf_document)):
#         page = pdf_document.load_page(page_num)
#         text = page.get_text()

#         # Split text into paragraphs using common delimiters
#         paragraphs = re.split(r'\n{2,}|\r\n{2,}', text)

#         # Check each paragraph for summary keywords
#         for para in paragraphs:
#             lower_para = para.lower()
#             score = sum(1 for keyword in summary_keywords if keyword.lower() in lower_para)
            
#             # Update if a paragraph with more keyword matches is found
#             if score > highest_score:
#                 highest_score = score
#                 summary_paragraph = para

#         # If a perfect match is found, break early
#         if highest_score == len(summary_keywords):
#             break
    
#     # Close the PDF document
#     pdf_document.close()
    
#     return summary_paragraph

# if __name__ == "__main__":
#     # Path to the PDF file you want to process
#     pdf_path = '2.pdf'
    
#     # Keywords that indicate a summary
#     summary_keywords = ["summary", "conclusion", "abstract", "concluding remarks"]
    
#     # Find and display the summary paragraph
#     summary_paragraph = find_summary_paragraph(pdf_path, summary_keywords)
    
#     if summary_paragraph:
#         print("Summary Paragraph:")
#         print(summary_paragraph)
#     else:
#         print("No summary paragraph found.")

from gensim.summarization import summarize
import fitz  # PyMuPDF

def summarize_pdf(pdf_path):
    # Extract text from the PDF
    pdf_document = fitz.open(pdf_path)
    full_text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        full_text += page.get_text() + "\n"
    pdf_document.close()

    # Summarize using gensim
    summary = summarize(full_text, ratio=0.1)  # Adjust ratio for desired summary length
    return summary

if __name__ == "__main__":
    pdf_path = '5.pdf'
    summary_text = summarize_pdf(pdf_path)
    print("Summary:")
    print(summary_text)
