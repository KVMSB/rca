import base64
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import FileResponse, StreamingResponse
from app.prompts.prompt import NON_COMPLIANCE_WORDS, TRAINING_MATERIAL_PROMPT
from app.services.doc_gen import doc_gen
 
# Initialize the router
router = APIRouter()
 
 
# Define the route
@router.post("/training_material_gen")
async def training_material_gen(request: Request):
    """
    Generate training material based on the incident and final root cause and return as a Word document.
    """
 
    llm = request.app.state.llm
 
    try:
        data = await request.json()
        if "incident" not in data or "final_root_cause" not in data:
            raise HTTPException(
                status_code=400,
                detail="Bad Request: Required keys 'incident' or 'final_root_cause' are missing.",
            )
        incident = str(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
 
    # Generate the query for the LLM
    query = TRAINING_MATERIAL_PROMPT.format(incident=incident) + NON_COMPLIANCE_WORDS
 
    # Get the response from the LLM
    response = await llm.acomplete(query)
 
    # Generate the Word document
    doc = doc_gen(str(response))
 
    # Convert the BytesIO to Base64
    base64_encoded = base64.b64encode(doc.read()).decode("utf-8")
 
    # Return Base64 string
    return {"filename": "training-material.docx", "file": base64_encoded}