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
import json
from langchain_core.output_parsers import StrOutputParser
from langchain.schema import AIMessage
import datetime
import requests
import json

# Set up logging
logging.basicConfig(filename="app.log", level=logging.INFO)

# Initialize FastAPI app
app = FastAPI()


data = {
    "week_1": {
        "growth_stage": "Germination",
        "key_activities": "This week, you will focus on sowing wheat seeds in Bahawalnagar, Punjab, Pakistan, and ensuring proper initial irrigation. Keep an eye on soil moisture and maintain an optimal temperature of around 25°C to support germination.",
    },
    "week_2": {
        "growth_stage": "Germination",
        "key_activities": "Continue to monitor soil moisture and temperature. Ensure the soil has adequate NPK levels (N: 40, P: 30, K: 20) to support the germination process.",
    },
    "week_3": {
        "growth_stage": "Seedling",
        "key_activities": "The seedlings will start to emerge. Apply early-stage fertilizers based on NPK levels to promote healthy growth. Begin pest control measures to prevent damage to the young seedlings.",
    },
    "week_4": {
        "growth_stage": "Seedling",
        "key_activities": "Continue to provide adequate irrigation and fertilization. Monitor the crop for any signs of pests or diseases and take corrective action as needed.",
    },
    "week_5": {
        "growth_stage": "Seedling",
        "key_activities": "The seedlings will continue to grow and develop. Maintain optimal soil conditions and continue with pest control measures.",
    },
    "week_6": {
        "growth_stage": "Seedling",
        "key_activities": "The seedlings are now established. Ensure they receive sufficient water and nutrients to support further growth.",
    },
    "week_7": {
        "growth_stage": "Tillering",
        "key_activities": "The wheat crop will start to produce tillers. Increase irrigation frequency to support this growth phase. Begin weeding to prevent competition for nutrients.",
    },
    "week_8": {
        "growth_stage": "Tillering",
        "key_activities": "Continue to provide adequate irrigation and fertilization. Monitor the crop for any signs of pests or diseases and take corrective action as needed.",
    },
    "week_9": {
        "growth_stage": "Tillering",
        "key_activities": "The crop will continue to produce tillers. Maintain optimal soil conditions and continue with weeding and pest control measures.",
    },
    "week_10": {
        "growth_stage": "Tillering",
        "key_activities": "The tillering phase is progressing. Ensure the crop receives sufficient water and nutrients to support further growth.",
    },
    "week_11": {
        "growth_stage": "Tillering",
        "key_activities": "The crop is now well-established. Continue to provide adequate irrigation and fertilization, and monitor for any signs of stress or disease.",
    },
    "week_12": {
        "growth_stage": "Tillering",
        "key_activities": "The tillering phase is nearing completion. Prepare for the heading phase by ensuring the crop has adequate nutrients and water.",
    },
    "week_13": {
        "growth_stage": "Heading",
        "key_activities": "The wheat crop will start to produce heads. Increase fertilization to support this growth phase. Begin pest control measures to prevent damage to the heads.",
    },
    "week_14": {
        "growth_stage": "Heading",
        "key_activities": "Continue to provide adequate irrigation and fertilization. Monitor the crop for any signs of pests or diseases and take corrective action as needed.",
    },
    "week_15": {
        "growth_stage": "Heading",
        "key_activities": "The crop will continue to produce heads. Maintain optimal soil conditions and continue with pest control measures.",
    },
    "week_16": {
        "growth_stage": "Heading",
        "key_activities": "The heading phase is nearing completion. Ensure the crop receives sufficient water and nutrients to support further growth.",
    },
    "week_17": {
        "growth_stage": "Maturation",
        "key_activities": "The wheat crop will start to mature. Reduce irrigation frequency to support this growth phase. Begin harvest preparation by checking the crop's moisture levels.",
    },
    "week_18": {
        "growth_stage": "Maturation",
        "key_activities": "Continue to monitor the crop's moisture levels and reduce irrigation frequency as needed. Prepare for harvest by checking equipment and planning logistics.",
    },
    "week_19": {
        "growth_stage": "Maturation",
        "key_activities": "The crop will continue to mature. Maintain optimal soil conditions and continue with harvest preparation.",
    },
    "week_20": {
        "growth_stage": "Maturation",
        "key_activities": "The crop is nearing maturity. Ensure it receives sufficient water and nutrients to support final growth.",
    },
    "week_21": {
        "growth_stage": "Maturation",
        "key_activities": "The crop is now mature. Prepare for harvest by finalizing equipment and logistics.",
    },
    "week_22": {
        "growth_stage": "Maturation",
        "key_activities": "The crop is ready for harvest. Begin harvesting the wheat crop, ensuring optimal moisture levels for storage.",
    },
    "week_23": {
        "growth_stage": "Maturation",
        "key_activities": "Continue harvesting the wheat crop. Ensure proper storage and handling to maintain quality.",
    },
    "week_24": {
        "growth_stage": "Maturation",
        "key_activities": "The harvest is nearing completion. Ensure all crop residue is properly managed to maintain soil health.",
    },
    "week_25": {
        "growth_stage": "Harvest & Post-Harvest Management",
        "key_activities": "The harvest is complete. Focus on proper storage and residue management to maintain quality and prepare the soil for future crops.",
    },
    "week_26": {
        "growth_stage": "Harvest & Post-Harvest Management",
        "key_activities": "Finalize post-harvest management activities, including soil preparation and equipment maintenance, to conclude the wheat farming cycle.",
    },
}

seconddata = {
    "week_8": {
        "dates": "March 19 - March 26",
        "tasks": {
            "Monday": {
                "task": "Irrigation",
                "details": "Water the field with 25 mm of water to support tillering stage",
                "tools_needed": ["Irrigation pipes", "Water pump"],
                "watering": {
                    "amount": "25 mm",
                    "time": "Early morning",
                    "method": "Flood irrigation",
                },
                "reason": "Adequate moisture is essential for tiller production and growth",
            },
            "Tuesday": {
                "task": "Fertilization",
                "details": "Apply 30 kg per acre of diammonium phosphate (DAP) fertilizer to promote tiller growth",
                "tools_needed": ["Fertilizer spreader", "Tractor"],
                "fertilizer_application": {
                    "type": "DAP",
                    "amount": "30 kg per acre",
                    "method": "Broadcast evenly",
                    "reason": "Provides phosphorus for root development and tiller production",
                },
            },
            "Wednesday": {
                "task": "Weeding",
                "details": "Remove weeds manually or with a weeder to prevent competition for nutrients",
                "tools_needed": ["Weeder", "Gloves"],
                "reason": "Weeds can compete with wheat plants for water, nutrients, and light, reducing crop yield",
            },
            "Thursday": {
                "task": "Pest monitoring",
                "details": "Inspect the crop for signs of pests such as aphids, armyworms, and rodents",
                "tools_needed": ["Magnifying glass", "Pest identification guide"],
                "pest_control": {
                    "pests_to_look_for": ["Aphids", "Armyworms", "Rodents"],
                    "treatment": "Neem oil spray or Imidacloprid 0.3 ml/L for aphids, Bt spray or Lambda-cyhalothrin 0.05 ml/L for armyworms, and rodenticides for rodents",
                },
            },
            "Friday": {
                "task": "Soil monitoring",
                "details": "Check soil moisture and temperature to determine if irrigation is needed",
                "tools_needed": ["Soil probe", "Thermometer"],
                "reason": "Optimal soil conditions are essential for wheat growth and development",
            },
            "Saturday": {
                "task": "Crop monitoring",
                "details": "Inspect the crop for signs of disease such as yellowing leaves or powdery mildew",
                "tools_needed": ["Magnifying glass", "Disease identification guide"],
                "reason": "Early detection of disease is crucial for effective management",
            },
            "Sunday": {
                "task": "Record keeping",
                "details": "Record irrigation, fertilization, and pest control activities for future reference",
                "tools_needed": ["Notebook", "Pen"],
                "reason": "Accurate record keeping is essential for tracking crop progress and making informed decisions",
            },
        },
        "summary": "At the end of Week 8, the crop should be in the tillering stage, and adequate irrigation, fertilization, and pest control measures should be in place",
    },
    "week_9": {
        "dates": "March 26 - April 02",
        "tasks": {
            "Monday": {
                "task": "Irrigation",
                "details": "Water the field with 25 mm of water to support continued tiller production",
                "tools_needed": ["Irrigation pipes", "Water pump"],
                "watering": {
                    "amount": "25 mm",
                    "time": "Early morning",
                    "method": "Flood irrigation",
                },
                "reason": "Adequate moisture is essential for continued tiller production and growth",
            },
            "Tuesday": {
                "task": "Fertilization",
                "details": "Apply 20 kg per acre of urea fertilizer to promote plant growth and development",
                "tools_needed": ["Fertilizer spreader", "Tractor"],
                "fertilizer_application": {
                    "type": "Urea",
                    "amount": "20 kg per acre",
                    "method": "Broadcast evenly",
                    "reason": "Provides nitrogen for plant growth and development",
                },
            },
            "Wednesday": {
                "task": "Weeding",
                "details": "Remove weeds manually or with a weeder to prevent competition for nutrients",
                "tools_needed": ["Weeder", "Gloves"],
                "reason": "Weeds can compete with wheat plants for water, nutrients, and light, reducing crop yield",
            },
            "Thursday": {
                "task": "Pest monitoring",
                "details": "Inspect the crop for signs of pests such as aphids, armyworms, and rodents",
                "tools_needed": ["Magnifying glass", "Pest identification guide"],
                "pest_control": {
                    "pests_to_look_for": ["Aphids", "Armyworms", "Rodents"],
                    "treatment": "Neem oil spray or Imidacloprid 0.3 ml/L for aphids, Bt spray or Lambda-cyhalothrin 0.05 ml/L for armyworms, and rodenticides for rodents",
                },
            },
            "Friday": {
                "task": "Soil monitoring",
                "details": "Check soil moisture and temperature to determine if irrigation is needed",
                "tools_needed": ["Soil probe", "Thermometer"],
                "reason": "Optimal soil conditions are essential for wheat growth and development",
            },
            "Saturday": {
                "task": "Crop monitoring",
                "details": "Inspect the crop for signs of disease such as yellowing leaves or powdery mildew",
                "tools_needed": ["Magnifying glass", "Disease identification guide"],
                "reason": "Early detection of disease is crucial for effective management",
            },
            "Sunday": {
                "task": "Record keeping",
                "details": "Record irrigation, fertilization, and pest control activities for future reference",
                "tools_needed": ["Notebook", "Pen"],
                "reason": "Accurate record keeping is essential for tracking crop progress and making informed decisions",
            },
        },
        "summary": "At the end of Week 9, the crop should be in the late tillering stage, and adequate irrigation, fertilization, and pest control measures should be in place to support continued growth and development",
    },
}

soil_data = {
    "NPK": {"N": "{N}", "P": "{P}", "K": "{K}"},  # Replace dynamically
    "soil_temperature": "{temperature}°C",
    "soil_moisture": "{moisture}%",
    "conductivity": "{conductivity} dS/m",
    "pH": "{ph}",
}

def get_weather_forecast(location):
    api_key = os.getenv("WEATHER_API_KEY")
    url = f"https://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&days=14"
    response = requests.get(url)

    if response.status_code == 200:
        weather_data = response.json()
        forecast = {}

        for i in range(2):  # Next 2 weeks
            week_start = (
                datetime.date.today() + datetime.timedelta(days=i * 7)
            ).strftime("%B %d")
            week_end = (
                datetime.date.today() + datetime.timedelta(days=(i + 1) * 7)
            ).strftime("%B %d")

            week_data = weather_data.get("forecast", {}).get("forecastday", [])[
                i * 7 : (i + 1) * 7
            ]

            if not week_data:  # Ensure week_data is not empty
                forecast[f"Week {i+1} ({week_start} - {week_end})"] = (
                    "No data available"
                )
                continue

            weekly_temps = [
                day["day"]["avgtemp_c"] for day in week_data if "day" in day
            ]
            avg_temp = sum(weekly_temps) / len(weekly_temps) if weekly_temps else "N/A"

            precipitation = sum(
                day["day"]["totalprecip_mm"] for day in week_data if "day" in day
            )

            wind_speeds = [
                day["day"]["maxwind_kph"] for day in week_data if "day" in day
            ]
            max_wind_speed = max(wind_speeds) if wind_speeds else "N/A"

            forecast[f"Week {i+1} ({week_start} - {week_end})"] = {
                "average_temperature": f"{avg_temp}°C",
                "precipitation": precipitation,
                "wind_speed": max_wind_speed,
            }

        return forecast

    return {"error": "Could not fetch weather data"}


@app.get("/currentTask")
def current_task():
    global data
    global soil_data
    week_number = 8  
    crop = "wheat"
    location = "Bahawalnagar"
    start_date = datetime.date.today().strftime("%B %d")

    previous_weeks = [
        f"week_{week_number - i}"
        for i in range(2, 0, -1)
        if f"week_{week_number - i}" in data
    ]
    next_weeks = [
        f"week_{week_number + i}"
        for i in range(0, 2)
        if f"week_{week_number + i}" in data
    ]

    previous_data = {week: data[week] for week in previous_weeks}
    next_data = {week: data[week] for week in next_weeks}
    weather_forecast = get_weather_forecast(location)

    queryFor2Week = f"""
    You are an agricultural expert with deep knowledge of {crop} farming in {location}.
    Your task is to generate an extremely detailed, 2-week {crop} farming guide starting from {start_date} to two weeks from this data(basically 2 upcoming weeks in total).

    This is not a simple summary. Write as if you are explaining to a farmer who will follow every word of your guide.
    The response should be like a full textbook or an agricultural manual, covering everything in-depth.

    ### Current Soil Conditions:
    - **NPK Levels:** N: {soil_data["NPK"]["N"]}, P: {soil_data["NPK"]["P"]}, K: {soil_data["NPK"]["K"]}
    - **Soil Temperature:** {soil_data["soil_temperature"]}
    - **Soil Moisture:** {soil_data["soil_moisture"]}
    - **Conductivity:** {soil_data["conductivity"]}
    - **pH Level:** {soil_data["pH"]}

    ### Weather Forecast for the Next 2 Weeks:
    {weather_forecast}

    The farming plan should be structured as:
    1. Week Number & Dates (e.g., Week 1: March 1st - March 7th)
    2. Daily Plan for Each Week (Monday-Sunday)
    3. Comprehensive Tasks for Each Day (Not just one-liners. Explain every detail.)
    4. Why Each Task is Important (Scientific reason + real-world examples)
    5. How to Do Each Task Properly (Step-by-step guidance)

    At the end of each week, reflect on the progress and adjustments needed for the next week.

    Now, think carefully.

    For each week, go through the following steps before answering:

    1. Break the week into daily tasks and think: "What does the farmer need to do on each day?"
    2. For each task, ask yourself:
    - What are the exact steps?
    - What tools or materials are needed?
    - What could go wrong, and how to fix it?
    - What is the scientific reason behind this task?
    - How will this task affect the next steps?

    3. Expand and Explain Every Detail
    - If the farmer is watering, specify how much water (in mm) and best time to water (morning/evening).
    - If applying fertilizer, mention which type (organic or synthetic), exact dosage, and method (broadcast, foliar spray, etc.).
    - If checking for pests, list which pests are common this week, how to identify them, and treatment methods (organic & chemical).

    The response should be in **JSON format**, structured like this:

    {{
    "week_1": {{
        "dates": "{start_date} ",
        "tasks": {{
        "Monday": {{
            "task": "Soil Preparation",
            "details": "Plow the field to a depth of 6 inches, remove weeds...",
            "tools_needed": ["Plow", "Tractor"],
            "fertilizer_application": {{
            "type": "Urea",
            "amount": "50 kg per acre",
            "method": "Broadcast evenly",
            "reason": "Provides nitrogen for early growth"
            }},
            "watering": {{
            "amount": "20 mm",
            "time": "Early morning",
            "method": "Flood irrigation"
            }},
            "pest_control": {{
            "pests_to_look_for": ["Aphids"],
            "treatment": "Neem oil spray or Imidacloprid 0.3 ml/L"
            }}
        }},
        "Tuesday": {{ ... }},
        "Wednesday": {{ ... }}
        }},
        "summary": "At the end of Week 1, soil should be fully prepared, seeds sown, and initial irrigation completed."
    }},
    "week_2": {{ ... }}
    }}

    The properly drafted plan was actually this, so please look into it while writing your answer. Our current week is {week_number}.


    Below is what happened in the last two weeks:
    {previous_data}

    The current week is Week {week_number}. The data below is what is supposed to happen in the upcoming two weeks:
    {next_data}
    Give results for all upcoming **2 weeks**.

    Return the response **only as a JSON format**. Do not include any explanations, headers, or additional text. Just return a valid JSON response. Please donot add strings or escape charcters.


  
    """

    rag_chain = get_rag_llm("llama-3.3-70b-versatile") | StrOutputParser()
    response = rag_chain.invoke(queryFor2Week)


    # Removing the triple backticks and "json\n" from the beginning
    response = response.strip().strip("```json").strip("```")

    # Convert to a proper JSON object
    try:
        json_response = json.loads(response)
        return json_response
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format", "raw_response": response}


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
