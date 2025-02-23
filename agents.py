# importing required libraries
import os
import autogen
import docx
import easyocr
from pdf2image import convert_from_path
from pypdf import PdfReader
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Define Groq API key and base URL
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Autogen's LLM configuration for Groq
llm_config = {
    "model": "llama-3.3-70b-versatile",
    "api_key": GROQ_API_KEY,
    "base_url": "https://api.groq.com/openai/v1",
}


def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF, using EasyOCR for scanned pdf if necessary."""
    with open(pdf_path, "rb") as file:
        reader = PdfReader(file)
        text = "\n".join(
            [page.extract_text() for page in reader.pages if page.extract_text()]
        )

    if not text.strip():
        images = convert_from_path(pdf_path)
        reader = easyocr.Reader(["en"], gpu=False)
        text = "\n".join(["\n".join(reader.readtext(img, detail=0)) for img in images])

    return text


def extract_text_from_docx(docx_path):
    """Extracts text from a docx"""
    doc = docx.Document(docx_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text


def get_document_text(file_path):
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format")


def create_agents():
    """Creates Autogen agents using the Groq API via OpenAI-compatible settings."""
    parser_agent = autogen.AssistantAgent(
        name="DocumentParser",
        system_message="Extracts and preprocesses text from uploaded documents, ensuring readability and proper segmentation.",
        llm_config=llm_config,
    )

    compliance_agent = autogen.AssistantAgent(
        name="ComplianceChecker",
        system_message="Analyzes the document for compliance with grammatical, structural, and clarity guidelines. Checks adherence to professional and regulatory standards.",
        llm_config=llm_config,
    )

    report_agent = autogen.AssistantAgent(
        name="ReportGenerator",
        system_message="Creates an in-depth compliance report detailing strengths, weaknesses, and suggested improvements based on detected violations.",
        llm_config=llm_config,
    )

    rewrite_agent = autogen.AssistantAgent(
        name="RewriteAgent",
        system_message="When requested, rewrite the document to comply with all identified compliance issues while maintaining its original intent and meaning.",
        llm_config=llm_config,
    )

    return parser_agent, compliance_agent, report_agent, rewrite_agent


def process_document(file_path, modify=False):
    """Processes a document through Autogen agents using Groq."""
    _, compliance_agent, report_agent, rewrite_agent = create_agents()

    text = get_document_text(file_path)

    # Step 1: Compliance check
    compliance_prompt = f"""
    Perform a comprehensive compliance analysis of the following document. 
    Evaluate it based on the following criteria:
    
    1. **Grammar & Syntax**: Identify grammatical mistakes, awkward phrasing, or improper syntax.
    2. **Clarity & Readability**: Assess how easy it is to understand. Suggest improvements for better readability.
    3. **Logical Flow & Structure**: Check for coherence, proper organization, and logical progression of ideas.
    4. **Compliance with Professional Standards**: Ensure adherence to formal writing guidelines and industry best practices.
    5. **Potential Issues & Recommendations**: Highlight major concerns and provide detailed, actionable suggestions for improvement.
    
    Document:
    {text}
    """
    compliance_response = compliance_agent.generate_reply(
        messages=[{"role": "user", "content": compliance_prompt}]
    )

    # Step 2: Generate a compliance report
    report_prompt = f"""
    Based on the following compliance analysis, generate a structured, detailed compliance report. 
    Include:
    
    - **Summary of Key Findings**: Briefly summarize the main issues found.
    - **Detailed Analysis**: Break down compliance violations by category (grammar, structure, readability, etc.).
    - **Actionable Recommendations**: Provide clear, step-by-step suggestions for improvement.
    - **Final Compliance Score**: Rate the document's overall quality and adherence on a scale of 1-10.
    
    Compliance Analysis:
    {compliance_response}
    """
    report_response = report_agent.generate_reply(
        messages=[{"role": "user", "content": report_prompt}]
    )

    if modify:
        # Step 3: Rewrite the document if modification is requested
        rewrite_prompt = f"""
        Rewrite the following document to correct all compliance issues while maintaining its original intent and meaning. Provide only the rewritten text without additional explanations or notes.
       
        Original Document:
        {text}
        """
        rewritten_text = rewrite_agent.generate_reply(
            messages=[{"role": "user", "content": rewrite_prompt}]
        )
        return rewritten_text

    return report_response


def process_file(filename, upload_folder="uploads", modify=False):
    """Processes a single specified document."""
    file_path = os.path.join(upload_folder, filename)
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"File '{filename}' not found in '{upload_folder}' directory."
        )

    if filename.endswith(".pdf") or filename.endswith(".docx"):
        return {filename: process_document(file_path, modify)}
    else:
        raise ValueError("Unsupported file format")
