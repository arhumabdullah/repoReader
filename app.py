import streamlit as st
from PIL import Image
from ocr_utils import preprocess_image, extract_text_from_image, parse_test_data
from ai_utils import analyze_value, get_explanation
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# Function to generate the PDF
def generate_pdf_report(tests, file_name="medical_report.pdf"):
    """
    Generates a PDF report with extracted test data and explanations.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Add title to PDF
    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, height - 40, "Medical Report Summary")

    # Add a line break
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 60, "-------------------------------------------")

    y_position = height - 80  # Start from the top of the page

    # Iterate over the tests and add them to the PDF
    for test in tests:
        if y_position < 100:
            c.showPage()  # Create a new page if the current page is full
            y_position = height - 40  # Reset y-position for new page

        # Write test name
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, y_position, f"Test: {test['test']}")

        y_position -= 20
        # Write value, range, and unit
        c.setFont("Helvetica", 12)
        c.drawString(100, y_position, f"Value: {test['value']} {test['unit']} (Range: {test['range']})")

        y_position -= 20
        # Write explanation
        explanation = get_explanation(test['test'], test['value'], test['range'], test['unit'])
        c.drawString(100, y_position, f"Explanation: {explanation}")
        
        y_position -= 20
        # Write advice
        status, advice = analyze_value(test['value'], test['range'])
        c.drawString(100, y_position, f"Advice: {advice}")
        
        y_position -= 40  # Space for the next test

    # Save the PDF to the buffer
    c.save()

    # Move the buffer position to the beginning of the stream
    buffer.seek(0)
    return buffer

# Streamlit UI setup
st.title("🩺 AI Medical Report Helper")

uploaded_file = st.file_uploader("Upload your medical report (image or PDF)", type=["jpg", "png", "pdf"])

if uploaded_file:
    # Load the image or PDF
    if uploaded_file.type in ["image/jpeg", "image/png"]:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        # Process image for OCR
        processed_image = preprocess_image(image)
        extracted_text = extract_text_from_image(processed_image)

        # Display the OCR result
        st.text_area("📝 Extracted Text", extracted_text, height=200)

        # Parse structured test data
        tests = parse_test_data(extracted_text)
        if not tests:
            st.write("No recognizable test data found.")
        else:
            # Display structured test data with explanations
            for test in tests:
                st.subheader(f"{test['test']}")
                status, advice = analyze_value(test['value'], test['range'])
                st.write(f"- Value: {test['value']} {test['unit']} ({status})")
                explanation = get_explanation(test['test'], test['value'], test['range'], test['unit'])
                st.write(f"- Explanation: {explanation}")
                st.write(f"- Advice: {advice}")

            # Generate PDF report for download
            pdf_buffer = generate_pdf_report(tests)
            st.download_button(
                label="Download PDF Report",
                data=pdf_buffer,
                file_name="medical_report.pdf",
                mime="application/pdf"
            )

    elif uploaded_file.type == "application/pdf":
        st.write("PDF upload feature is under development.")
    
    # Option to download a PDF summary (feature to be developed later)
    st.download_button("Download PDF Summary", "summary_placeholder.pdf")
