from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from services.tag_recommender import TagRecommender
from config import settings

app = FastAPI(title="iCog Tag Recommender API", version="1.0.0")

# Configure CORS for WordPress integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your WordPress domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for the simple UI
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize tag recommender
tag_recommender = TagRecommender()

class RecommendationRequest(BaseModel):
    text: str
    images: List[str] = []
    videos: List[str] = []

class RecommendationResponse(BaseModel):
    tags: List[str]
    confidence_scores: Optional[List[float]] = None
    message: Optional[str] = None

@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return {
        "message": "iCog Tag Recommender API",
        "version": "1.0.0",
        "endpoints": {
            "recommend": "/recommend/json",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "tag_recommender"}

@app.post("/recommend/json", response_model=RecommendationResponse)
async def recommend_tags(request: RecommendationRequest):
    """
    Main endpoint for tag recommendation.
    Accepts blog content (text, images, videos) and returns recommended tags.
    """
    try:
        # Get recommendations from the tag recommender service
        recommended_tags, confidence_scores = await tag_recommender.get_recommendations(
            text=request.text,
            images=request.images,
            videos=request.videos
        )
        
        return RecommendationResponse(
            tags=recommended_tags,
            confidence_scores=confidence_scores,
            message="Tags recommended successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.post("/recommend")
async def recommend_tags_legacy(request: RecommendationRequest):
    """
    Legacy endpoint for backward compatibility
    """
    return await recommend_tags(request)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
