from django.shortcuts import render
from django.http import HttpResponse
from .forms import uploadPDFForm
import pdfplumber
from docx import Document
import os
import tempfile
import uuid

def convert_pdf_to_word(request):
    if request.method == "POST":
        form = uploadPDFForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = request.FILES['pdf_file']

            # Temporary file paths
            temp_pdf_path = os.path.join(tempfile.gettempdir(), f"temp_{uuid.uuid4().hex}.pdf")
            output_word_path = os.path.join(tempfile.gettempdir(), f"converted_{uuid.uuid4().hex}.docx")
            
            try:
                # Save the uploaded PDF file to a temporary file
                with open(temp_pdf_path, 'wb') as temp_file:
                    for chunk in pdf_file.chunks():
                        temp_file.write(chunk)

                # Extract text from the PDF and create a Word document
                full_text = ""
                with pdfplumber.open(temp_pdf_path) as pdf:
                    for page in pdf.pages:
                        full_text += page.extract_text() + "\n"

                # Create a Word document from the extracted text
                document = Document()
                for line in full_text.split("\n"):       
                    document.add_paragraph(line.strip())
                document.save(output_word_path)

                # Send the Word document as an HTTP response
                with open(output_word_path, "rb") as docx_file:
                    response = HttpResponse(docx_file.read(), content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")    
                    response['Content-Disposition'] = f'attachment; filename={os.path.basename(output_word_path)}'

                # Clean up temporary files after sending the response
                os.remove(temp_pdf_path)
                os.remove(output_word_path)
                return response

            except Exception as e:
                # Handle errors
                return HttpResponse(f"An error occurred: {str(e)}", status=500)

    else:
        form = uploadPDFForm()

    return render(request, "upload.html", {"form": form})
