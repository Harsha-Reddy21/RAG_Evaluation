import openai
from typing import Dict, List, Optional
from config import Config

class OpenAIService:
    """Service for OpenAI API interactions."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        if not Config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
        
        openai.api_key = Config.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def generate_content_from_idea(self, idea_content: str, content_type: str = "blog") -> str:
        """Generate content from an idea using OpenAI."""
        
        system_prompt = f"""You are an expert content creator specializing in {content_type} writing. 
        Your task is to transform a content idea into a well-structured, engaging piece of content.
        
        Guidelines:
        - Write in a clear, professional tone
        - Include engaging headlines and subheadings
        - Use bullet points and numbered lists where appropriate
        - Include practical examples and actionable insights
        - Optimize for readability and SEO
        - Include a compelling introduction and conclusion
        - Target length: 1500-2000 words for blog posts
        
        Format the output as clean markdown with proper structure."""
        
        user_prompt = f"""Based on the following content idea, generate a complete {content_type}:

{idea_content}

Please create a comprehensive, well-structured piece that expands on this idea with:
1. An engaging headline
2. A compelling introduction
3. Well-organized sections with subheadings
4. Practical insights and examples
5. A strong conclusion with call-to-action
6. Proper markdown formatting

Make it ready for publication on Medium."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=3000,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def enhance_content(self, content: str, enhancement_type: str) -> str:
        """Enhance existing content based on type."""
        
        enhancement_prompts = {
            "seo": "Optimize this content for SEO by improving headlines, adding relevant keywords, and enhancing meta descriptions.",
            "readability": "Improve the readability of this content by simplifying complex sentences, adding transitions, and improving flow.",
            "engagement": "Make this content more engaging by adding storytelling elements, questions, and interactive elements.",
            "professional": "Make this content more professional by improving tone, adding citations, and enhancing credibility."
        }
        
        system_prompt = """You are an expert content editor. Your task is to enhance the provided content based on the specified improvement type."""
        
        user_prompt = f"""Please enhance the following content for {enhancement_type}:

{content}

Enhancement focus: {enhancement_prompts.get(enhancement_type, "General improvement")}

Return the enhanced content in the same markdown format."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=3000,
                temperature=0.5
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def generate_idea_summary(self, idea_content: str) -> Dict:
        """Generate a structured summary of an idea."""
        
        system_prompt = """You are an expert content strategist. Analyze the provided content idea and extract key information in a structured format."""
        
        user_prompt = f"""Analyze this content idea and provide a structured summary:

{idea_content}

Please provide a JSON response with the following structure:
{{
    "title": "Suggested title",
    "key_points": ["point1", "point2", "point3"],
    "target_audience": "description",
    "estimated_word_count": number,
    "content_type": "blog/article/guide",
    "difficulty_level": "beginner/intermediate/advanced",
    "seo_keywords": ["keyword1", "keyword2", "keyword3"]
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            import json
            return json.loads(response.choices[0].message.content.strip())
        
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def suggest_improvements(self, content: str) -> List[str]:
        """Suggest improvements for content."""
        
        system_prompt = """You are an expert content editor. Analyze the provided content and suggest specific improvements."""
        
        user_prompt = f"""Analyze this content and suggest 3-5 specific improvements:

{content}

Provide suggestions in a clear, actionable format."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.5
            )
            
            suggestions = response.choices[0].message.content.strip().split('\n')
            return [s.strip() for s in suggestions if s.strip()]
        
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}") 