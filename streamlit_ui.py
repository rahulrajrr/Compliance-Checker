# importing required libraries
import streamlit as st
import requests
import os
import json
import time
from docx import Document
from agents import process_file
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph

FASTAPI_URL = "http://127.0.0.1:8000/upload"
UPLOAD_FOLDER = "uploads"
MODIFIED_FOLDER = "modified_documents"
os.makedirs(MODIFIED_FOLDER, exist_ok=True)

st.set_page_config(
    page_title="Compliance Checker", layout="wide", initial_sidebar_state="expanded"
)

# Sidebar UI
with st.sidebar:
    st.markdown(
        """
        <style>
            .sidebar-title {
                font-size: 22px;
                font-weight: bold;
                color: #FF7700;
            }
            .sidebar-text {
                font-size: 16px;
                color: #555;
            }
        </style>
        <p class='sidebar-title'>⚡ Compliance Checker</p>
        <p class='sidebar-text'>🚀 Upload a <b>PDF</b> or <b>Word</b> file to check compliance.</p>
        <p class='sidebar-text'>📝 Modify the document if needed & download it.</p>
        <hr style='border:1px solid #ddd;' />
    """,
        unsafe_allow_html=True,
    )

# Fix Button UI
st.markdown(
    """
    <style>
        div.stButton > button {
            width: 100%;
            border-radius: 8px;
            font-size: 16px;
            padding: 10px;
            background-color: #4CAF50;
            color: white;
        }
        .css-18e3th9 {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
        }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    "<h1 style='text-align: center;'>Compliance Checker</h1>", unsafe_allow_html=True
)

if "modify_clicked" not in st.session_state:
    st.session_state.modify_clicked = False


st.markdown(
    """
    <style>
    /* Hide the file uploader's size limit text */
    div.stFileUploader small {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader("Upload a PDF or Word document", type=["pdf", "docx"])

if uploaded_file:
    # Reset modify button state for a new file
    st.session_state.modify_clicked = False
    st.session_state["uploaded_filename"] = uploaded_file.name
    st.session_state["uploaded_file"] = uploaded_file

    col1, col2 = st.columns([1, 2])

    with col1:
        st.info(f"**Uploaded File:** {uploaded_file.name}")

    # Improved Loading State Handling
    st.markdown("🔄 **Processing file...** Please wait.", unsafe_allow_html=True)

    # Uploading the file
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    response = requests.post(FASTAPI_URL, files=files)

    if response.status_code == 200:
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")

        with st.spinner("🔍 **Analyzing document...**"):
            try:
                time.sleep(3)
                report = process_file(uploaded_file.name, UPLOAD_FOLDER)

                if isinstance(report, dict):
                    compliance_text = next(iter(report.values()))
                elif isinstance(report, str):
                    report_dict = json.loads(report.replace("'", '"'))
                    compliance_text = next(iter(report_dict.values()))
                else:
                    raise ValueError("Invalid report format")

                # Display Compliance Report
                st.subheader("Compliance Report")
                st.markdown(
                    f"<div class='css-18e3th9'>{compliance_text}</div>",
                    unsafe_allow_html=True,
                )

                # Modify Button
                st.subheader(
                    "Do you want to modify the document to comply with guidelines?"
                )
                # Custom CSS to make the button normal-sized
                st.markdown(
                    """
                    <style>
                    div.stButton > button {
                        width: auto;
                        padding: 8px 16px;
                        font-size: 16px;
                        background-color: #4CAF50; /* Green */
                        color: white;
                        border-radius: 5px;
                        border: none;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )

                # Regular Streamlit button
                if st.button("Modify Document", key="modify_btn"):
                    st.session_state.modify_clicked = True

                if st.session_state.modify_clicked:
                    with st.spinner("🔧 **Modifying document...**"):
                        uploaded_file = st.session_state.uploaded_file
                        modification_result = process_file(
                            uploaded_file.name, UPLOAD_FOLDER, modify=True
                        )

                        modified_doc = None
                        if isinstance(modification_result, dict):
                            modified_doc = modification_result.get(
                                uploaded_file.name, None
                            )
                        elif isinstance(modification_result, str):
                            try:
                                modified_dict = json.loads(
                                    modification_result.replace("'", '"')
                                )
                                modified_doc = modified_dict.get(
                                    uploaded_file.name, None
                                )
                            except json.JSONDecodeError:
                                st.error(
                                    "Error: Invalid JSON format in modification result."
                                )
                        else:
                            st.error("Error: Unexpected modification result format.")

                        if modified_doc:
                            st.subheader("Modified Document")

                            file_extension = os.path.splitext(uploaded_file.name)[-1]
                            modified_filename = f"modified_{uploaded_file.name}"
                            modified_path = os.path.join(
                                MODIFIED_FOLDER, modified_filename
                            )

                            if file_extension.lower() == ".pdf":
                                doc = SimpleDocTemplate(modified_path, pagesize=letter)
                                styles = getSampleStyleSheet()
                                paragraph = Paragraph(
                                    modified_doc.replace("\n", "<br/>"),
                                    styles["Normal"],
                                )
                                doc.build([paragraph])
                                mime_type = "application/pdf"
                            elif file_extension.lower() == ".docx":
                                doc = Document()
                                for line in modified_doc.split("\n"):
                                    doc.add_paragraph(line)
                                doc.save(modified_path)
                                mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            else:
                                st.error("Unsupported file format.")
                                st.stop()

                            if os.path.exists(modified_path):
                                st.success("Modified document saved!")

                            with open(modified_path, "rb") as f:
                                st.download_button(
                                    label="Download Modified Document",
                                    data=f,
                                    file_name=modified_filename,
                                    mime=mime_type,
                                    key="download_btn",
                                )

            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    else:
        st.error(f"Upload failed: {response.json().get('detail', 'Unknown error')}")
