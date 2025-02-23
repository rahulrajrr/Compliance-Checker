import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Add the root directory of the project to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from file_upload import app
from agents import process_file, process_document

# Create a test client for FastAPI
client = TestClient(app)

UPLOAD_DIR = "tests"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def test_upload_valid_file():
    """Test uploading a valid file"""
    file_path = "tests/sample.docx"
    with open(file_path, "rb") as file:
        response = client.post(
            "/upload",
            files={
                "file": (
                    "sample.docx",
                    file,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

    assert response.status_code == 200
    assert "File uploaded successfully" in response.json()["message"]


def test_upload_invalid_file():
    """Test uploading an invalid file type"""
    file_path = "tests/sample.txt"
    with open(file_path, "rb") as file:
        response = client.post(
            "/upload", files={"file": ("sample.txt", file, "text/plain")}
        )

    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]


@patch("agents.get_document_text", return_value="Sample extracted text")
def test_process_document(mock_text_extraction):
    """Test processing a document for compliance checking"""
    mock_agent = MagicMock()
    mock_agent.generate_reply.return_value = "Compliance Report"
    with patch(
        "agents.create_agents", return_value=(None, mock_agent, mock_agent, mock_agent)
    ):
        result = process_document("test/sample.docx")
    assert "Compliance Report" in result


def test_process_file_not_found():
    """Test processing a non-existent file"""
    with pytest.raises(FileNotFoundError):
        process_file("sample1.docx", UPLOAD_DIR)


@patch("agents.process_document", return_value="Compliance Report")
def test_process_file(mock_process_document):
    """Test processing a valid file"""
    result = process_file("sample.docx", UPLOAD_DIR)
    assert "sample.docx" in result
    assert result["sample.docx"] == "Compliance Report"


@pytest.mark.performance
def test_large_file_upload():
    """Test uploading a large file for performance validation"""
    file_path = "tests/large_sample.pdf"
    with open(file_path, "rb") as file:
        response = client.post(
            "/upload", files={"file": ("large_sample.pdf", file, "application/pdf")}
        )

    assert response.status_code == 200
    assert "File uploaded successfully" in response.json()["message"]
