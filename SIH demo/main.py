from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for prototype; later restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load dataset
crops = pd.read_csv("crops.csv")

# Request model
class FarmerInput(BaseModel):
    soil_type: str
    rainfall: float
    ph: float
    season: str

@app.post("/recommend")
def recommend_crop(data: FarmerInput):
    # Filter crops based on conditions
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

# Optional root endpoint
@app.get("/")
def root():
    return {"message": "AI Crop Recommendation API is running"}
