
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
import uvicorn
import time
import os
from typing import Optional
from services.text_extraction import TextExtractionService
from services.pii_anonymization import PIIAnonymizationService

app = FastAPI(title="Document Processing API", version="1.0.0")

text_extractor = TextExtractionService()
pii_anonymizer = PIIAnonymizationService()

@app.post("/process-document")
async def process_document(
    file: UploadFile = File(...),
    strategy: Optional[str] = Form(default="unstructured")
):
    """
    Process document with text extraction and PII anonymization.
    
    Args:
        file: Uploaded file via multipart/form-data
        strategy: Processing strategy ('unstructured' or 'marker')
    
    Returns:
        JSONResponse with processed document data
    """
    start_time = time.time()
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Extract text based on strategy
        if strategy == "marker":
            extracted_text = await text_extractor.extract_with_marker(file_content, file.filename)
        else:
            extracted_text = await text_extractor.extract_with_unstructured(file_content, file.filename)
        
        # Anonymize PII
        anonymization_result = await pii_anonymizer.anonymize_text(extracted_text)
        
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)
        
        # Construct response
        response_data = {
            "metadata": {
                "filename": file.filename,
                "file_size_bytes": file_size,
                "extraction_engine": strategy,
                "processing_time_ms": processing_time
            },
            "content": {
                "layout_preserved_text": extracted_text,
                "anonymized_text": anonymization_result["anonymized_text"],
                "pii_analysis": {
                    "entities_found": anonymization_result["entities_found"],
                    "anonymization_count": len(anonymization_result["entities_found"])
                }
            }
        }
        
        return JSONResponse(content=response_data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Document Processing API is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
