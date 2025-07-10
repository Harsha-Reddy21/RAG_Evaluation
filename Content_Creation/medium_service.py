import requests
import json
from typing import Dict, Optional
from config import Config

class MediumService:
    """Service for Medium API interactions."""
    
    def __init__(self):
        """Initialize Medium service."""
        if not Config.MEDIUM_ACCESS_TOKEN:
            raise ValueError("Medium access token not configured")
        if not Config.MEDIUM_USER_ID:
            raise ValueError("Medium user ID not configured")
        
        self.access_token = Config.MEDIUM_ACCESS_TOKEN
        self.user_id = Config.MEDIUM_USER_ID
        self.base_url = "https://api.medium.com/v1"
    
    def get_user_info(self) -> Dict:
        """Get current user information."""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(f"{self.base_url}/me", headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get user info: {str(e)}")
    
    def publish_post(self, title: str, content: str, tags: list = None, 
                    canonical_url: str = None, publish_status: str = "public") -> Dict:
        """Publish a post to Medium."""
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        # Convert markdown content to HTML for Medium
        html_content = self._markdown_to_html(content)
        
        post_data = {
            'title': title,
            'contentFormat': 'html',
            'content': html_content,
            'publishStatus': publish_status
        }
        
        if tags:
            post_data['tags'] = tags
        
        if canonical_url:
            post_data['canonicalUrl'] = canonical_url
        
        try:
            response = requests.post(
                f"{self.base_url}/users/{self.user_id}/posts",
                headers=headers,
                json=post_data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to publish post: {str(e)}")
    
    def _markdown_to_html(self, markdown_content: str) -> str:
        """Convert markdown content to HTML for Medium."""
        import markdown
        
        # Basic markdown to HTML conversion
        html = markdown.markdown(
            markdown_content,
            extensions=['extra', 'codehilite', 'tables']
        )
        
        # Medium-specific formatting adjustments
        html = html.replace('<h1>', '<h1><strong>')
        html = html.replace('</h1>', '</strong></h1>')
        
        html = html.replace('<h2>', '<h2><strong>')
        html = html.replace('</h2>', '</strong></h2>')
        
        html = html.replace('<h3>', '<h3><strong>')
        html = html.replace('</h3>', '</strong></h3>')
        
        # Add Medium-specific styling
        html = f'<p>{html}</p>'
        
        return html
    
    def extract_title_from_content(self, content: str) -> str:
        """Extract title from markdown content."""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
            elif line.startswith('## ') and not any(line.startswith(f'## {prefix}') for prefix in ['Key Points', 'Target Audience', 'Call to Action', 'Notes']):
                return line[3:].strip()
        
        # Fallback: use first non-empty line
        for line in lines:
            if line.strip() and not line.strip().startswith('#'):
                return line.strip()[:100]  # Limit to 100 characters
        
        return "Untitled Post"
    
    def extract_tags_from_content(self, content: str) -> list:
        """Extract tags from content metadata or content itself."""
        tags = []
        
        # Look for tags in metadata section
        if 'Tags:' in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'Tags:' in line:
                    tag_line = line.split('Tags:')[1].strip()
                    if tag_line:
                        tags.extend([tag.strip() for tag in tag_line.split(',')])
                    break
        
        # If no tags found, extract from content
        if not tags:
            # Simple keyword extraction (this could be enhanced with NLP)
            common_tags = ['technology', 'programming', 'ai', 'machine-learning', 
                          'web-development', 'python', 'javascript', 'data-science',
                          'productivity', 'tools', 'tutorial', 'guide']
            
            content_lower = content.lower()
            for tag in common_tags:
                if tag in content_lower:
                    tags.append(tag)
        
        return tags[:5]  # Limit to 5 tags
    
    def update_post_metadata(self, post_id: str, updates: Dict) -> Dict:
        """Update post metadata."""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.put(
                f"{self.base_url}/posts/{post_id}",
                headers=headers,
                json=updates
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to update post: {str(e)}")
    
    def get_publication_posts(self, publication_id: str) -> list:
        """Get posts from a publication."""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/publications/{publication_id}/posts",
                headers=headers
            )
            response.raise_for_status()
            return response.json().get('data', [])
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get publication posts: {str(e)}")
    
    def publish_to_publication(self, publication_id: str, title: str, content: str, 
                              tags: list = None, canonical_url: str = None) -> Dict:
        """Publish a post to a specific publication."""
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        html_content = self._markdown_to_html(content)
        
        post_data = {
            'title': title,
            'contentFormat': 'html',
            'content': html_content,
            'publishStatus': 'public'
        }
        
        if tags:
            post_data['tags'] = tags
        
        if canonical_url:
            post_data['canonicalUrl'] = canonical_url
        
        try:
            response = requests.post(
                f"{self.base_url}/publications/{publication_id}/posts",
                headers=headers,
                json=post_data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to publish to publication: {str(e)}") 