from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic_models import QueryInput, QueryResponse, DocumentInfo, DeleteFileRequest
from langchain_utils import (get_rag_chain, get_rag_llm)
from db_utils import (
    insert_application_logs,
    get_chat_history,
    get_all_documents,
    insert_document_record,
    delete_document_record,
)
from chroma_utils import index_document_to_chroma, delete_doc_from_chroma
import os
import uuid
import logging
import shutil
from typing import (List,Dict, Any)
from pydantic import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser
import asyncio
import json
from langchain_core.output_parsers import StrOutputParser
from langchain.schema import AIMessage


# Set up logging
logging.basicConfig(filename="app.log", level=logging.INFO)

# Initialize FastAPI app
app = FastAPI()


class GrowthPhase(BaseModel):
    phase_name: str = Field(description="Name of the growth phase")
    duration_weeks: int = Field(
        description="Approximate duration of this phase in weeks"
    )
    key_activities: List[str] = Field(description="Main tasks during this phase")


class CropTimeline(BaseModel):
    crop: str = Field(description="Crop name")
    location: str = Field(description="Geographical location")
    estimated_start_date: str = Field(description="Approximate planting start date")
    estimated_end_date: str = Field(description="Approximate harvesting end date")
    total_duration_weeks: int = Field(
        description="Total duration of the crop cycle in weeks"
    )
    growth_phases: List[GrowthPhase] = Field(
        description="List of growth phases with durations and tasks"
    )


def FetchApprox():
    queryForApproxTimeline = """
    You are an AI agricultural assistant. Your task is to provide a structured timeline for growing wheat in Bahawalnagar, Punjab, Pakistan.

    ### **Provide the following details in JSON format**:
    - `"crop"`: Name of the crop
    - `"location"`: Location of farming
    - `"estimated_start_date"`: Approximate planting start date
    - `"estimated_end_date"`: Approximate harvesting end date
    - `"total_duration_weeks"`: Total duration in weeks
    - `"growth_phases"`: List of growth phases with:
      - `"phase_name"`: Growth phase name
      - `"duration_weeks"`: Phase duration in weeks
      - `"key_activities"`: Main activities during this phase

    Ensure the response is structured as per the format.
    """

    print("Fetch Approx Running")
    rag_chain = get_rag_llm("llama-3.3-70b-versatile")
    structured_llm = rag_chain.with_structured_output(CropTimeline)
    ansForApproxTimeline = structured_llm.invoke(queryForApproxTimeline)
    print(ansForApproxTimeline)
    return ansForApproxTimeline


def FetchEntire():
    queryForEntire = """Role & Context:
    You are an agriculture expert. Your task is to generate a high-level, week-wise farming plan for a given crop, location, and starting date. The plan should outline the expected growth stages and key activities for each week without daily breakdowns or detailed instructions.

    Instructions:
    - Dynamically determine the starting date, location, and crop based on the input.
    - Only provide an overview of tasks for each week.
    - Consider real-time factors such as temperature ({temperature}°C), NPK levels (N: {N}, P: {P}, K: {K}), and soil conditions.

    Response Format:
    The response should be in JSON format with the following structure:
    {{
    "week_1": {{
        "growth_stage": "Germination & Early Growth",
        "key_activities": "This week, you will focus on sowing seeds and ensuring proper initial irrigation. Keep an eye on soil moisture and maintain an optimal temperature of around {temperature}°C to support germination."
    }},
    "week_2": {{
        "growth_stage": "Root Establishment",
        "key_activities": "The seedlings will start developing stronger roots. Apply early-stage fertilizers based on NPK levels (N: {N}, P: {P}, K: {K}) to promote healthy growth. Weed control is also essential at this stage to prevent competition for nutrients."
    }},
    "...": "...",
    "week_n": {{
        "growth_stage": "Harvest & Post-Harvest Management",
        "key_activities": "Your crop is now ready for harvest. Ensure you pick the crop at optimal maturity for the best yield. After harvesting, focus on proper storage and residue management to maintain quality."
    }}
    }}

    Additional Guidelines:
    - Growth stage – The general phase of crop development.
    - Key activities – A short summary of the most important actions.

    This should be a broad timeline for the entire farming cycle. After this, we will regenerate detailed tasks for the current and next week based on real-time data.

    Here is some real-time context about how the crop timeline really looks like:
    {output}

    Now, generate the full week-wise farming plan for the given input. Return answer in pure JSON, not as a string!
    """

    # Example dynamic values
    temperature = 25  # Fetch from weather API
    N, P, K = 40, 30, 20  # Example soil NPK values

    # Get approximate timeline
    approx_timeline = FetchApprox()
    # approx_timeline = crop=""" 'Wheat' location='Bahawalnagar, Punjab, Pakistan' estimated_start_date='November 1' estimated_end_date='December 31' total_duration_weeks=8 growth_phases=[GrowthPhase(phase_name='Germination', duration_weeks=1, key_activities=['Sowing', 'Irrigation']), GrowthPhase(phase_name='Seedling', duration_weeks=2, key_activities=['Fertilization', 'Pest control']), GrowthPhase(phase_name='Tillering', duration_weeks=2, key_activities=['Irrigation', 'Weeding']), GrowthPhase(phase_name='Heading', duration_weeks=1, key_activities=['Pest control', 'Fungicide application']), GrowthPhase(phase_name='Maturation', duration_weeks=1, key_activities=['Irrigation', 'Harvest preparation']), GrowthPhase(phase_name='Harvesting', duration_weeks=1, key_activities=['Cutting', 'Threshing'])]"""

    # Format the query
    formatted_ques = queryForEntire.format(
        temperature=temperature, N=N, P=P, K=K, output=approx_timeline
    )
    print("FetchEntire Running")

    # Send to LLM
    rag_chain = get_rag_llm("llama-3.3-70b-versatile") | StrOutputParser()
    response = rag_chain.invoke(formatted_ques)
    # Ensure the response is parsed properly
    try:
        if isinstance(response, AIMessage):
            json_string = response.content
        else:
            json_string = response  # Assuming response is already a JSON string

        data = json.loads(json_string)  # Convert to dictionary
        print(json.dumps(data, indent=4))  # Pretty print
        return data  # Return as dict

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return {"error": "Invalid JSON response", "raw_response": response}

    return response


@app.post("/fetch-entire")
def fetchEntire():
    return FetchEntire()


@app.post("/chat", response_model=QueryResponse)
def chat(query_input: QueryInput):
    session_id = query_input.session_id or str(uuid.uuid4())
    logging.info(
        f"Session ID: {session_id}, User Query: {query_input.question}, Model: {query_input.model.value}"
    )

    chat_history = get_chat_history(session_id)
    rag_chain = get_rag_chain(query_input.model.value)
    answer = rag_chain.invoke(
        {"input": query_input.question, "chat_history": chat_history}
    )["answer"]

    insert_application_logs(
        session_id, query_input.question, answer, query_input.model.value
    )
    logging.info(f"Session ID: {session_id}, AI Response: {answer}")
    return QueryResponse(answer=answer, session_id=session_id, model=query_input.model)


@app.post("/upload-doc")
def upload_and_index_document(file: UploadFile = File(...)):
    allowed_extensions = [".pdf", ".docx", ".html"]
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed types are: {', '.join(allowed_extensions)}",
        )

    temp_file_path = f"temp_{file.filename}"

    try:
        # Save the uploaded file to a temporary file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_id = insert_document_record(file.filename)
        success = index_document_to_chroma(temp_file_path, file_id)

        if success:
            return {
                "message": f"File {file.filename} has been successfully uploaded and indexed.",
                "file_id": file_id,
            }
        else:
            delete_document_record(file_id)
            raise HTTPException(
                status_code=500, detail=f"Failed to index {file.filename}."
            )
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@app.get("/list-docs", response_model=list[DocumentInfo])
def list_documents():
    return get_all_documents()


@app.post("/delete-doc")
def delete_document(request: DeleteFileRequest):
    chroma_delete_success = delete_doc_from_chroma(request.file_id)

    if chroma_delete_success:
        db_delete_success = delete_document_record(request.file_id)
        if db_delete_success:
            return {
                "message": f"Successfully deleted document with file_id {request.file_id} from the system."
            }
        else:
            return {
                "error": f"Deleted from Chroma but failed to delete document with file_id {request.file_id} from the database."
            }
    else:
        return {
            "error": f"Failed to delete document with file_id {request.file_id} from Chroma."
        }
