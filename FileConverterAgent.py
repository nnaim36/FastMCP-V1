from fastmcp import FastMCP
import pdfkit
from dotenv import load_dotenv
from fastapi import FastAPI
import os

load_dotenv()

mcp = FastMCP(
    name="PDF-Generator",
    host="127.0.0.1",
    port=8007
)

WKHTMLTOPDF_PATH = os.getenv("WKHTMLTOPDF_PATH")
config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

@mcp.tool
def generate_pdf_from_html(html_code: str, output_filename: str) -> str:
    """
    Converts given HTML code to PDF and saves it locally.

    Args:
        html_code: The raw HTML string.
        output_filename: Desired name of the output PDF (e.g., 'menu.pdf').

    Returns:
        A message indicating success or failure.
    """
    try:
        pdfkit.from_string(html_code, output_filename, configuration=config)
        return f"PDF generated successfully: {output_filename}"
    except Exception as e:
        return f"Failed to generate PDF: {str(e)}"

if __name__ == "__main__":
    mcp.run()