import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from mcp_filesystem import MCPFilesystemManager
from openai_service import OpenAIService
from medium_service import MediumService
from config import Config

class ContentManager:
    """Main content management orchestrator."""
    
    def __init__(self):
        """Initialize the content manager with all services."""
        self.filesystem = MCPFilesystemManager()
        self.openai = OpenAIService()
        self.medium = MediumService()
        
        # Initialize workspace
        self.filesystem.initialize_workspace()
    
    def capture_idea(self, user_input: str) -> Dict:
        """Capture and structure a content idea from user input."""
        try:
            # Use OpenAI to structure the idea
            idea_summary = self.openai.generate_idea_summary(user_input)
            
            # Create idea file
            filepath = self.filesystem.create_idea_file(
                title=idea_summary.get('title', 'Untitled Idea'),
                description=user_input,
                tags=', '.join(idea_summary.get('seo_keywords', []))
            )
            
            # Update the idea file with structured data
            idea_content = self.filesystem.read_file(filepath)
            if idea_content:
                # Add structured metadata
                enhanced_content = f"""# Idea: {idea_summary.get('title', 'Untitled Idea')}

## Metadata
- Created: {datetime.now().strftime('%Y-%m-%d')}
- Status: Captured
- Tags: {', '.join(idea_summary.get('seo_keywords', []))}
- Target Audience: {idea_summary.get('target_audience', '')}
- Estimated Word Count: {idea_summary.get('estimated_word_count', 1500)}
- Content Type: {idea_summary.get('content_type', 'blog')}
- Difficulty Level: {idea_summary.get('difficulty_level', 'intermediate')}

## Description
{user_input}

## Key Points
{chr(10).join([f'- {point}' for point in idea_summary.get('key_points', [])])}

## Target Audience
{idea_summary.get('target_audience', '')}

## Call to Action
- 

## Notes
- Content Type: {idea_summary.get('content_type', 'blog')}
- Difficulty: {idea_summary.get('difficulty_level', 'intermediate')}
- SEO Keywords: {', '.join(idea_summary.get('seo_keywords', []))}
"""
                self.filesystem.write_file(filepath, enhanced_content)
            
            return {
                'success': True,
                'filepath': filepath,
                'title': idea_summary.get('title', 'Untitled Idea'),
                'summary': idea_summary,
                'message': f"Idea captured successfully! File: {filepath}"
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to capture idea: {str(e)}"
            }
    
    def generate_content_from_idea(self, idea_filepath: str) -> Dict:
        """Generate content from an existing idea."""
        try:
            # Read idea content
            idea_content = self.filesystem.read_file(idea_filepath)
            if not idea_content:
                raise Exception(f"Idea file not found: {idea_filepath}")
            
            # Generate content using OpenAI
            generated_content = self.openai.generate_content_from_idea(idea_content)
            
            # Create generated file
            filename = os.path.basename(idea_filepath).replace('.md', '-draft.md')
            generated_filepath = os.path.join('generated', filename)
            
            # Add metadata to generated content
            enhanced_content = f"""# Generated Content

## Source Idea
{idea_filepath}

## Generated On
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Status
Draft - Ready for Review

---

{generated_content}

---

## Publication Metadata
- Medium URL: 
- Published Date: 
- Status: Draft
"""
            
            success = self.filesystem.write_file(generated_filepath, enhanced_content)
            
            if success:
                return {
                    'success': True,
                    'filepath': generated_filepath,
                    'content': generated_content,
                    'message': f"Content generated successfully! File: {generated_filepath}"
                }
            else:
                raise Exception("Failed to save generated content")
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to generate content: {str(e)}"
            }
    
    def approve_content(self, generated_filepath: str) -> Dict:
        """Move content from generated to published folder."""
        try:
            # Create published filepath
            filename = os.path.basename(generated_filepath).replace('-draft.md', '-published.md')
            published_filepath = os.path.join('published', filename)
            
            # Move file
            success = self.filesystem.move_file(generated_filepath, published_filepath)
            
            if success:
                # Update status in file
                content = self.filesystem.read_file(published_filepath)
                if content:
                    content = content.replace('Status: Draft - Ready for Review', 'Status: Approved - Ready for Publishing')
                    self.filesystem.write_file(published_filepath, content)
                
                return {
                    'success': True,
                    'filepath': published_filepath,
                    'message': f"Content approved and moved to published folder: {published_filepath}"
                }
            else:
                raise Exception("Failed to move file")
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to approve content: {str(e)}"
            }
    
    def publish_to_medium(self, published_filepath: str) -> Dict:
        """Publish content to Medium."""
        try:
            # Read published content
            content = self.filesystem.read_file(published_filepath)
            if not content:
                raise Exception(f"Published file not found: {published_filepath}")
            
            # Extract title and tags
            title = self.medium.extract_title_from_content(content)
            tags = self.medium.extract_tags_from_content(content)
            
            # Clean content for Medium (remove metadata)
            clean_content = self._extract_clean_content(content)
            
            # Publish to Medium
            medium_response = self.medium.publish_post(
                title=title,
                content=clean_content,
                tags=tags
            )
            
            # Update file with Medium metadata
            medium_url = medium_response.get('data', {}).get('url', '')
            updated_content = content.replace(
                'Medium URL: ',
                f'Medium URL: {medium_url}'
            ).replace(
                'Published Date: ',
                f'Published Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            ).replace(
                'Status: Approved - Ready for Publishing',
                'Status: Published on Medium'
            )
            
            self.filesystem.write_file(published_filepath, updated_content)
            
            return {
                'success': True,
                'medium_url': medium_url,
                'title': title,
                'message': f"Successfully published to Medium! URL: {medium_url}"
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to publish to Medium: {str(e)}"
            }
    
    def _extract_clean_content(self, content: str) -> str:
        """Extract clean content without metadata for Medium publishing."""
        lines = content.split('\n')
        clean_lines = []
        in_content = False
        
        for line in lines:
            if line.startswith('---'):
                in_content = not in_content
                continue
            
            if in_content and not line.startswith('## Publication Metadata'):
                clean_lines.append(line)
        
        return '\n'.join(clean_lines).strip()
    
    def get_workspace_status(self) -> Dict:
        """Get current status of the workspace."""
        try:
            ideas = self.filesystem.list_directory('ideas')
            generated = self.filesystem.list_directory('generated')
            published = self.filesystem.list_directory('published')
            
            return {
                'ideas_count': len(ideas),
                'generated_count': len(generated),
                'published_count': len(published),
                'ideas': ideas,
                'generated': generated,
                'published': published
            }
        except Exception as e:
            return {
                'error': str(e),
                'ideas_count': 0,
                'generated_count': 0,
                'published_count': 0
            }
    
    def enhance_content(self, filepath: str, enhancement_type: str) -> Dict:
        """Enhance existing content."""
        try:
            content = self.filesystem.read_file(filepath)
            if not content:
                raise Exception(f"File not found: {filepath}")
            
            # Extract clean content for enhancement
            clean_content = self._extract_clean_content(content)
            
            # Enhance content
            enhanced_content = self.openai.enhance_content(clean_content, enhancement_type)
            
            # Update file with enhanced content
            updated_content = content.replace(
                clean_content,
                enhanced_content
            )
            
            success = self.filesystem.write_file(filepath, updated_content)
            
            if success:
                return {
                    'success': True,
                    'filepath': filepath,
                    'message': f"Content enhanced for {enhancement_type}"
                }
            else:
                raise Exception("Failed to save enhanced content")
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to enhance content: {str(e)}"
            }
    
    def search_content(self, query: str) -> List[Dict]:
        """Search for content across the workspace."""
        try:
            results = []
            
            # Search in ideas
            idea_results = self.filesystem.search_files(query, 'ideas')
            results.extend([{'type': 'idea', **result} for result in idea_results])
            
            # Search in generated
            generated_results = self.filesystem.search_files(query, 'generated')
            results.extend([{'type': 'generated', **result} for result in generated_results])
            
            # Search in published
            published_results = self.filesystem.search_files(query, 'published')
            results.extend([{'type': 'published', **result} for result in published_results])
            
            return sorted(results, key=lambda x: x['match_count'], reverse=True)
        
        except Exception as e:
            return [{'error': str(e)}] 