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
def html_code_to_pdf(html_code: str, output_filename: str = "menu.pdf") -> str:
    """
    Converts raw HTML code to a PDF and returns the full file path.
    """
    try:

        # Generate PDF
        pdfkit.from_string(html_code, output_filename, configuration=config)

        # Get full absolute path
        full_path = os.path.abspath(output_filename)

        return full_path
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()