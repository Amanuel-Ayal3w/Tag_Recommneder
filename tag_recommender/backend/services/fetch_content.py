import re
import logging
from typing import List, Dict, Tuple
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import html

logger = logging.getLogger(__name__)

class ContentFetcher:
    """Service for fetching and extracting content from blog posts and URLs."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def extract_from_html(self, html_content: str) -> Dict[str, List[str]]:
        """
        Extract text and images from HTML content.
        
        Args:
            html_content: HTML string
            
        Returns:
            Dictionary with 'text' and 'images' lists
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract text content
            text_content = self._extract_text(soup)
            
            # Extract images
            images = self._extract_images(soup)
            
            return {
                'text': text_content,
                'images': images
            }
            
        except Exception as e:
            logger.error(f"Error extracting content from HTML: {e}")
            return {'text': [], 'images': []}
    
    def fetch_from_url(self, url: str) -> Dict[str, List[str]]:
        """
        Fetch content from a URL.
        
        Args:
            url: URL to fetch content from
            
        Returns:
            Dictionary with 'text' and 'images' lists
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            return self.extract_from_html(response.text)
            
        except Exception as e:
            logger.error(f"Error fetching content from URL {url}: {e}")
            return {'text': [], 'images': []}
    
    def _extract_text(self, soup: BeautifulSoup) -> List[str]:
        """Extract text content from BeautifulSoup object."""
        text_content = []
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract text from various content areas
        content_selectors = [
            'article',
            '.post-content',
            '.entry-content',
            '.content',
            'main',
            'body'
        ]
        
        for selector in content_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(separator=' ', strip=True)
                if text and len(text) > 50:  # Only include substantial text
                    text_content.append(text)
        
        # If no content found, get all text
        if not text_content:
            text = soup.get_text(separator=' ', strip=True)
            if text:
                text_content.append(text)
        
        return text_content
    
    def _extract_images(self, soup: BeautifulSoup) -> List[str]:
        """Extract image URLs from BeautifulSoup object."""
        images = []
        
        # Find all img tags
        img_tags = soup.find_all('img')
        
        for img in img_tags:
            src = img.get('src')
            if src:
                # Clean and normalize URL
                src = src.strip()
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    # This would need base URL to be complete
                    pass
                
                if src and self._is_valid_image_url(src):
                    images.append(src)
        
        return images
    
    def _is_valid_image_url(self, url: str) -> bool:
        """Check if URL is a valid image URL."""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
        parsed = urlparse(url)
        
        # Check file extension
        path = parsed.path.lower()
        if any(path.endswith(ext) for ext in image_extensions):
            return True
        
        # Check if it's a data URL
        if url.startswith('data:image/'):
            return True
        
        return False
    
    def extract_from_wordpress_content(self, content: str) -> Dict[str, List[str]]:
        """
        Extract content from WordPress post content (Gutenberg blocks).
        
        Args:
            content: WordPress post content with Gutenberg blocks
            
        Returns:
            Dictionary with 'text' and 'images' lists
        """
        try:
            # Extract text content
            text_content = self._extract_text_from_blocks(content)
            
            # Extract images from content
            images = self._extract_images_from_content(content)
            
            return {
                'text': text_content,
                'images': images
            }
            
        except Exception as e:
            logger.error(f"Error extracting from WordPress content: {e}")
            return {'text': [], 'images': []}
    
    def _extract_text_from_blocks(self, content: str) -> List[str]:
        """Extract text from Gutenberg blocks."""
        text_content = []
        
        # Remove HTML tags but keep text
        clean_text = re.sub(r'<[^>]+>', ' ', content)
        clean_text = html.unescape(clean_text)
        
        # Split into paragraphs and clean
        paragraphs = [p.strip() for p in clean_text.split('\n') if p.strip()]
        
        for paragraph in paragraphs:
            if len(paragraph) > 20:  # Only include substantial paragraphs
                text_content.append(paragraph)
        
        return text_content
    
    def _extract_images_from_content(self, content: str) -> List[str]:
        """Extract image URLs from content."""
        images = []
        
        # Find img tags
        img_pattern = r'<img[^>]+src="([^">]+)"'
        matches = re.findall(img_pattern, content)
        
        for match in matches:
            if self._is_valid_image_url(match):
                images.append(match)
        
        return images
    
    def combine_content(self, text_list: List[str]) -> str:
        """
        Combine multiple text pieces into a single string.
        
        Args:
            text_list: List of text strings
            
        Returns:
            Combined text string
        """
        if not text_list:
            return ""
        
        # Join with spaces and clean up
        combined = " ".join(text_list)
        
        # Remove extra whitespace
        combined = re.sub(r'\s+', ' ', combined).strip()
        
        return combined
