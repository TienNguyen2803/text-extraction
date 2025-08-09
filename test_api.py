
import requests
import os

def test_health_check():
    """Test health check endpoint"""
    response = requests.get("http://0.0.0.0:5000/")
    print("Health check:", response.json())

def test_document_processing():
    """Test document processing endpoint"""
    # Tạo file test đơn giản
    test_content = "This is a test document with PII: John Doe, email: john@example.com, phone: 555-123-4567"
    
    with open("test.txt", "w") as f:
        f.write(test_content)
    
    # Upload file
    with open("test.txt", "rb") as f:
        files = {"file": ("test.txt", f, "text/plain")}
        data = {"strategy": "unstructured"}
        response = requests.post("http://0.0.0.0:5000/process-document", files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print("Document processing successful:")
        print(f"Original text: {result['content']['layout_preserved_text']}")
        print(f"Anonymized text: {result['content']['anonymized_text']}")
        print(f"PII found: {result['content']['pii_analysis']['entities_found']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
    
    # Clean up
    os.remove("test.txt")

if __name__ == "__main__":
    test_health_check()
    test_document_processing()
