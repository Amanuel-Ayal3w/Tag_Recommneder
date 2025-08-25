# iCog Tag Recommender

An AI-powered tag recommendation system that combines BERT (text) and CLIP (image) models to suggest relevant tags for blog posts.

## Features

- **BERT-based text analysis**: Analyzes blog content to suggest relevant tags
- **CLIP-based image analysis**: Analyzes images in blog posts for visual tag suggestions
- **Video thumbnail analysis**: Extracts thumbnails from videos and analyzes them for tag suggestions
- **FastAPI backend**: RESTful API with automatic documentation
- **WordPress integration**: Ready-to-use WordPress plugin
- **Docker support**: Easy deployment with Docker Compose

## Architecture

```
tag_recommender/
├── backend/                 # FastAPI backend
│   ├── main.py             # FastAPI app entrypoint
│   ├── models/             # AI models
│   │   ├── bert_model.py   # BERT text embedding + recommendation
│   │   ├── clip_model.py   # CLIP image embedding + recommendation
│   │   └── tag_embeddings.py # Load tags + precompute embeddings
│   ├── services/           # Business logic
│   │   ├── fetch_content.py # Content extraction
│   │   └── tag_recommender.py # Main recommendation logic
│   ├── static/             # Web UI
│   │   └── index.html      # Simple testing interface
│   ├── data/               # Data files
│   │   └── tags.txt        # Tag list (one per line)
│   ├── requirements.txt    # Python dependencies
│   ├── config.py           # Configuration
│   └── Dockerfile          # Docker configuration
└── README.md              # This file
```

## Quick Start

### 1. Setup with Docker Compose

The FastAPI service is already integrated into your existing `docker-compose.yml`. To start:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f tag-recommender
```

### 2. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Web UI**: http://localhost:8000/static/index.html

### 3. WordPress Integration

The WordPress plugin is already configured to call the FastAPI backend at `http://host.docker.internal:8000/recommend/json`.

## API Endpoints

### POST /recommend/json

Main endpoint for tag recommendations.

**Request Body:**
```json
{
  "text": "Your blog post content here...",
  "images": ["https://example.com/image1.jpg", "https://example.com/image2.jpg"],
  "videos": ["https://example.com/video1.mp4", "https://example.com/video2.mp4"]
}
```

**Response:**
```json
{
  "tags": ["machine learning", "artificial intelligence", "data science"],
  "confidence_scores": [0.95, 0.87, 0.76],
  "message": "Tags recommended successfully"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "tag_recommender"
}
```

## Configuration

Edit `backend/config.py` to customize:

- **Model settings**: BERT and CLIP model names
- **Tag limits**: Maximum number of tags to return
- **Confidence thresholds**: Minimum confidence for tag inclusion
- **Weights**: Text vs image vs video importance (default: 50% text, 30% image, 20% video)

## Adding Custom Tags

1. Edit `backend/data/tags.txt`
2. Add one tag per line
3. Restart the service: `docker-compose restart tag-recommender`

Example `tags.txt`:
```
machine learning
artificial intelligence
data science
web development
photography
travel
fitness
health
finance
cooking
education
```

## Development

### Local Development

```bash
cd tag_recommender/backend

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Testing

```bash
# Run tests
pytest tests/

# Test API endpoint
curl -X POST "http://localhost:8000/recommend/json" \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a blog post about machine learning", "images": []}'
```

## Model Information

- **BERT Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **CLIP Model**: `openai/clip-vit-base-patch32`
- **Video Processing**: OpenCV for thumbnail extraction
- **Embedding Dimension**: 384 (BERT), 512 (CLIP)

## Troubleshooting

### Common Issues

1. **Models not loading**: Check internet connection for model downloads
2. **Memory issues**: Reduce `max_images` in config.py
3. **Slow responses**: First request may be slow due to model loading

### Logs

```bash
# View FastAPI logs
docker-compose logs tag-recommender

# View all logs
docker-compose logs
```

## Performance

- **First request**: ~10-15 seconds (model loading)
- **Subsequent requests**: ~1-3 seconds
- **Memory usage**: ~2-3GB RAM
- **CPU**: Multi-threaded processing

## License

This project is part of the iCog Tag Recommender system.
