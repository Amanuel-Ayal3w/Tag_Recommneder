import asyncio
import logging
from typing import List, Tuple, Dict
from collections import Counter
import numpy as np

from models.tag_embeddings import TagEmbeddings
from models.bert_model import BERTTagRecommender
from models.clip_model import CLIPTagRecommender
from models.video_model import VideoTagRecommender
from services.fetch_content import ContentFetcher
from config import settings

logger = logging.getLogger(__name__)

class TagRecommender:
    """Main tag recommender service that combines BERT and CLIP recommendations."""
    
    def __init__(self):
        logger.info("Initializing TagRecommender...")
        
        # Initialize tag embeddings
        self.tag_embeddings = TagEmbeddings()
        
        # Initialize individual recommenders
        self.bert_recommender = BERTTagRecommender(self.tag_embeddings)
        self.clip_recommender = CLIPTagRecommender(self.tag_embeddings)
        self.video_recommender = VideoTagRecommender(self.tag_embeddings)
        
        # Initialize content fetcher
        self.content_fetcher = ContentFetcher()
        
        logger.info("TagRecommender initialized successfully")
    
    async def get_recommendations(
        self, 
        text: str = "", 
        images: List[str] = None, 
        videos: List[str] = None
    ) -> Tuple[List[str], List[float]]:
        """
        Get tag recommendations by combining BERT and CLIP models.
        
        Args:
            text: Blog post text content
            images: List of image URLs
            videos: List of video URLs (not currently used)
            
        Returns:
            Tuple of (recommended_tags, confidence_scores)
        """
        if images is None:
            images = []
        
        try:
            # Process text content
            processed_text = self._process_text(text)
            
            # Get BERT recommendations for text
            bert_tags, bert_scores = self.bert_recommender.get_recommendations(processed_text)
            
            # Get CLIP recommendations for images
            clip_tags, clip_scores = self.clip_recommender.get_recommendations(images)
            
            # Get video recommendations for videos
            video_tags, video_scores = self.video_recommender.get_recommendations(videos)
            
            # Combine recommendations
            final_tags, final_scores = self._combine_recommendations(
                bert_tags, bert_scores, clip_tags, clip_scores, video_tags, video_scores
            )
            
            logger.info(f"Generated {len(final_tags)} final recommendations")
            return final_tags, final_scores
            
        except Exception as e:
            logger.error(f"Error in tag recommendation: {e}")
            return [], []
    
    def _process_text(self, text: str) -> str:
        """Process and clean text content."""
        if not text:
            return ""
        
        # Extract content if it's WordPress/Gutenberg content
        if '<' in text and '>' in text:
            extracted = self.content_fetcher.extract_from_wordpress_content(text)
            text_parts = extracted['text']
            text = self.content_fetcher.combine_content(text_parts)
        
        # Truncate if too long
        if len(text) > settings.max_text_length:
            text = text[:settings.max_text_length] + "..."
        
        return text.strip()
    
    def _combine_recommendations(
        self, 
        bert_tags: List[str], 
        bert_scores: List[float],
        clip_tags: List[str], 
        clip_scores: List[float],
        video_tags: List[str] = None,
        video_scores: List[float] = None
    ) -> Tuple[List[str], List[float]]:
        """
        Combine BERT and CLIP recommendations using weighted fusion.
        
        Args:
            bert_tags: Tags recommended by BERT
            bert_scores: Confidence scores from BERT
            clip_tags: Tags recommended by CLIP
            clip_scores: Confidence scores from CLIP
            
        Returns:
            Tuple of (final_tags, final_scores)
        """
        # Create tag-score mappings
        bert_dict = dict(zip(bert_tags, bert_scores))
        clip_dict = dict(zip(clip_tags, clip_scores))
        video_dict = dict(zip(video_tags or [], video_scores or []))
        
        # Get all unique tags
        all_tags = set(bert_tags + clip_tags + (video_tags or []))
        
        # Calculate combined scores
        combined_scores = {}
        
        for tag in all_tags:
            bert_score = bert_dict.get(tag, 0.0)
            clip_score = clip_dict.get(tag, 0.0)
            video_score = video_dict.get(tag, 0.0)
            
            # Weighted combination (text: 50%, image: 30%, video: 20%)
            combined_score = (
                0.5 * bert_score + 
                0.3 * clip_score +
                0.2 * video_score
            )
            
            if combined_score >= settings.min_confidence:
                combined_scores[tag] = combined_score
        
        # Sort by score and get top tags
        sorted_tags = sorted(
            combined_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Limit to max_tags
        final_tags = [tag for tag, score in sorted_tags[:settings.max_tags]]
        final_scores = [score for tag, score in sorted_tags[:settings.max_tags]]
        
        return final_tags, final_scores
    
    def get_recommendations_sync(
        self, 
        text: str = "", 
        images: List[str] = None, 
        videos: List[str] = None
    ) -> Tuple[List[str], List[float]]:
        """
        Synchronous version of get_recommendations for non-async contexts.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.get_recommendations(text, images, videos)
            )
        finally:
            loop.close()
    
    def get_available_tags(self) -> List[str]:
        """Get list of all available tags."""
        return self.tag_embeddings.get_tags()
    
    def get_model_info(self) -> Dict:
        """Get information about the models being used."""
        return {
            "bert_model": settings.bert_model_name,
            "clip_model": settings.clip_model_name,
            "total_tags": len(self.get_available_tags()),
            "max_tags": settings.max_tags,
            "min_confidence": settings.min_confidence,
            "text_weight": settings.text_weight,
            "image_weight": settings.image_weight
        }
