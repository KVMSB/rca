from docx import Document
from io import BytesIO


def doc_gen(content: str):
    # Create an in-memory .docx file
    doc = Document()
    doc.add_paragraph(content)

    # Save to a BytesIO object
    doc_io = BytesIO()
    doc.save(doc_io)
    doc_io.seek(0)  # Move the pointer to the beginning of the file

    # Return the file as a response with appropriate headers
    return doc_io
