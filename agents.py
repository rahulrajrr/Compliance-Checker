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
    Perform a **sentence-by-sentence** compliance analysis of the following document. 

    For each sentence:
    1. Identify **grammar, syntax, clarity, and structure** issues.
    2. Explain what is incorrect.
    3. Don't give the correct version of answers. 

    ### **Format the response as follows:**
    **Sentence:** "<exact sentence from the document>"
    - **Issue:** <Describe the problem>
    ---
    (Ensure to separate each sentence and its issues with a "---" for readability.)

    Do NOT give a generic summary. Only return sentence-by-sentence analysis.

    Document:
    {text}
    """

    compliance_response = compliance_agent.generate_reply(
        messages=[{"role": "user", "content": compliance_prompt}]
    )

    # Step 2: Generate a detailed compliance report
    report_prompt = f"""
    Generate a **comprehensive compliance report** based on the following **sentence-by-sentence** compliance analysis.

    ### **Report Structure:**
    1. **Summary of Key Findings**  
    - Provide a **brief overview** of the main issues found in the document.

    2. **Line-by-Line Detailed Analysis**  
    - For each problematic sentence, include:
        - **Original Sentence:** "<exact sentence from the document>"
        - **Issue:** <Explain what is wrong>

    3. **Actionable Recommendations**  
    - Suggest **general best practices** based on the errors identified.

    4. **Final Compliance Score**  
    - Rate the document's quality and adherence on a **scale of 1-10** (considering grammar, readability, and professional compliance).

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
