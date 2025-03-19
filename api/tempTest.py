from dotenv import load_dotenv
import datetime
import requests


load_dotenv()


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

week_number = 5

# Get previous two weeks (week_number - 2, week_number - 1)
previous_weeks = [
    f"week_{week_number - i}"
    for i in range(2, 0, -1)
    if f"week_{week_number - i}" in data
]

# Get current week and next week (week_number, week_number + 1)
next_weeks = [
    f"week_{week_number + i}" for i in range(0, 2) if f"week_{week_number + i}" in data
]


# Dynamic Inputs
crop = "wheat"
location = "Bahawalnagar"
start_date = datetime.date.today().strftime("%B %d")  # Today’s date
week_number = 8


# Generate previous and next weeks' data outside the f-string
previous_data = "\n".join([f"{week}: {data[week]}" for week in previous_weeks])
next_data = "\n".join([f"{week}: {data[week]}" for week in next_weeks])


# Placeholder for actual soil data (replace with real values)
soil_data = {
    "NPK": {"N": "{N}", "P": "{P}", "K": "{K}"},  # Replace dynamically
    "soil_temperature": "{temperature}°C",
    "soil_moisture": "{moisture}%",
    "conductivity": "{conductivity} dS/m",
    "pH": "{ph}",
}


# Fetch weather forecast for the next 2 weeks (Actual API Call)
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

            weekly_temps = [
                day["day"]["avgtemp_c"]
                for day in weather_data["forecast"]["forecastday"][i * 7 : (i + 1) * 7]
            ]
            avg_temp = sum(weekly_temps) / len(weekly_temps) if weekly_temps else "N/A"

            forecast[f"Week {i+1} ({week_start} - {week_end})"] = {
                "average_temperature": f"{avg_temp}°C",
                "precipitation": sum(
                    day["day"]["totalprecip_mm"]
                    for day in weather_data["forecast"]["forecastday"][
                        i * 7 : (i + 1) * 7
                    ]
                ),
                "wind_speed": max(
                    day["day"]["maxwind_kph"]
                    for day in weather_data["forecast"]["forecastday"][
                        i * 7 : (i + 1) * 7
                    ]
                ),
            }

        return forecast
    else:
        return {"error": "Could not fetch weather data"}


weather_forecast = get_weather_forecast(location)

# Generate Prompt
question = f"""
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

Return the response in **JSON format only not in string**.
"""


response = rag_chain.invoke(question)
print(f"Answer: {response}")
