from fpdf import FPDF
from datetime import datetime

def generate_user_pdf(user_data, output_path="user_data.pdf"):
    """
    Generate a PDF containing user data.

    user_data: dict containing user info, e.g.
        {
            "name": "John Doe",
            "email": "john@example.com",
            "joined_at": "2025-01-01",
            "scans_done": 25,
            "cracks_detected": 7,
            "last_scan": "2025-12-07",
        }
    output_path: Path to save the PDF
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 10, "User Data Report", ln=True, align='C')
    pdf.ln(10)
    
    # User info
    pdf.set_font("Arial", '', 12)
    for key, value in user_data.items():
        # Capitalize key and replace underscores with spaces
        display_key = key.replace("_", " ").title()
        pdf.cell(0, 8, f"{display_key}: {value}", ln=True)
    
    # Footer
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 8, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='R')
    
    # Save PDF
    pdf.output(output_path)

