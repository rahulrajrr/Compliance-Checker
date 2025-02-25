# Document Compliance Checker

## Overview
Document Compliance Checker is a robust Python-based application designed to analyze PDF and Word documents for English writing compliance using an AI-powered agent. The tool evaluates grammar, clarity, structure, and adherence to language standards, providing users with detailed compliance reports. Users can modify and download improved versions of their documents based on AI-driven suggestions.

## Features
✅ Upload and analyze PDF/Word documents for English language compliance  
✅ AI-powered grammar, structure, and readability analysis  
✅ Detailed compliance reports highlighting errors and improvement suggestions  
✅ Automated modifications to enhance document quality while preserving meaning  
✅ Download corrected documents in PDF/Word format  

## How It Works
1. **Upload a Document**  
   - Users upload a PDF or Word document via the Streamlit UI.

2. **AI Compliance Check**  
   - The AI agent evaluates the document for grammar, clarity, and structural compliance.  
   - A comprehensive compliance report is generated.

3. **Modify the Document**  
   - Users can request modifications based on the compliance report.  
   - The AI agent rewrites incorrect or unclear sections while maintaining the original intent.

4. **Download the Modified Document**  
   - Once modifications are completed, users can download the improved document in PDF or Word format.

## Technology Stack
- **Backend:** FastAPI  
- **Frontend:** Streamlit  
- **AI Processing:** Groq (LLM), Autogen (Agents)
- **Document Handling:** python-docx, pypdf  

## Installation & Setup
### Step 1: Create a Virtual Environment
python -m venv venv

### Step 2: Activate the Virtual Environment
venv\Scripts\activate


### Step 3: Install Dependencies
pip install -r requirements.txt

### Step 4: Run the FastAPI Server
python file_upload.py

### Step 5: Launch the UI
streamlit run streamlit_ui.py


## API Endpoints
| POST   | 127.0.0.1:8000/upload  | Uploads a document for analysis |

## Access this url to try the demo
https://aspireapp.streamlit.app/

![Screenshot 1](https://raw.githubusercontent.com/rahulrajrr/Compliance-Checker/main/images/file_upload.jpg)
![Screenshot 2](https://raw.githubusercontent.com/rahulrajrr/Compliance-Checker/main/images/UI.png)
