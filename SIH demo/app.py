from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

# Initialize app
app = FastAPI(
    title="AI-Based Crop Recommendation",
    description="Prototype API for recommending crops to farmers",
    version="1.0.0"
)

# Enable CORS (for frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for prototype; later restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load dataset
try:
    crops = pd.read_csv("crops.csv")
except FileNotFoundError:
    crops = pd.DataFrame(columns=[
        "soil_type", "min_rainfall", "max_rainfall",
        "min_ph", "max_ph", "season", "crop"
    ])
    print("⚠️ Warning: crops.csv not found. API will return no matches.")

# Input model
class FarmerInput(BaseModel):
    soil_type: str
    rainfall: float
    ph: float
    season: str

# Recommendation endpoint
@app.post("/recommend")
def recommend_crop(data: FarmerInput):
    if crops.empty:
        return {"error": "Dataset not loaded. Please add crops.csv"}

    # Filter based on given conditions
    filtered = crops[
        (crops['soil_type'].str.lower() == data.soil_type.lower()) &
        (crops['min_rainfall'] <= data.rainfall) &
        (crops['max_rainfall'] >= data.rainfall) &
        (crops['min_ph'] <= data.ph) &
        (crops['max_ph'] >= data.ph) &
        (crops['season'].str.lower() == data.season.lower())
    ]

    if filtered.empty:
        return {"message": "No exact match found. Try adjusting inputs."}

    recommendations = filtered['crop'].tolist()
    return {
        "recommended_crops": recommendations,
        "reason": f"Based on {data.soil_type} soil, {data.rainfall}mm rainfall, pH {data.ph}, season {data.season}"
    }

# Root endpoint (health check)
@app.get("/")
def root():
    return {"message": "🌱 AI Crop Recommendation API is running!"}
