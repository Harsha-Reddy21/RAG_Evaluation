import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from fastmcp import FastMCP
from config import Config

class MCPFilesystemManager:
    """Manages filesystem operations using FastMCP."""
    
    def __init__(self):
        """Initialize the MCP filesystem manager."""
        self.mcp = FastMCP()
        self.workspace_path = Config.MCP_FILESYSTEM_PATH
        
    def initialize_workspace(self):
        """Initialize the workspace directory structure."""
        directories = Config.create_workspace_directories()
        
        # Create template files if they don't exist
        self._create_default_templates()
        
        return directories
    
    def _create_default_templates(self):
        """Create default template files."""
        idea_template = """# Idea: {title}

## Metadata
- Created: {date}
- Status: Captured
- Tags: {tags}

## Description
{description}

## Key Points
- 

## Target Audience
- 

## Call to Action
- 

## Notes
{notes}
"""
        
        template_path = os.path.join(Config.TEMPLATES_DIR, 'idea_template.md')
        if not os.path.exists(template_path):
            self.write_file(template_path, idea_template)
    
    def list_directory(self, path: str) -> List[Dict]:
        """List contents of a directory."""
        try:
            full_path = os.path.join(self.workspace_path, path)
            if not os.path.exists(full_path):
                return []
            
            items = []
            for item in os.listdir(full_path):
                item_path = os.path.join(full_path, item)
                item_info = {
                    'name': item,
                    'path': os.path.join(path, item),
                    'type': 'directory' if os.path.isdir(item_path) else 'file',
                    'size': os.path.getsize(item_path) if os.path.isfile(item_path) else 0,
                    'modified': datetime.fromtimestamp(os.path.getmtime(item_path)).isoformat()
                }
                items.append(item_info)
            
            return sorted(items, key=lambda x: x['name'])
        except Exception as e:
            print(f"Error listing directory {path}: {e}")
            return []
    
    def read_file(self, path: str) -> Optional[str]:
        """Read content from a file."""
        try:
            full_path = os.path.join(self.workspace_path, path)
            if not os.path.exists(full_path):
                return None
            
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {path}: {e}")
            return None
    
    def write_file(self, path: str, content: str) -> bool:
        """Write content to a file."""
        try:
            full_path = os.path.join(self.workspace_path, path)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
        except Exception as e:
            print(f"Error writing file {path}: {e}")
            return False
    
    def move_file(self, source_path: str, destination_path: str) -> bool:
        """Move a file from source to destination."""
        try:
            source_full = os.path.join(self.workspace_path, source_path)
            dest_full = os.path.join(self.workspace_path, destination_path)
            
            if not os.path.exists(source_full):
                return False
            
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(dest_full), exist_ok=True)
            
            os.rename(source_full, dest_full)
            return True
        except Exception as e:
            print(f"Error moving file from {source_path} to {destination_path}: {e}")
            return False
    
    def delete_file(self, path: str) -> bool:
        """Delete a file."""
        try:
            full_path = os.path.join(self.workspace_path, path)
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {path}: {e}")
            return False
    
    def create_idea_file(self, title: str, description: str, tags: str = "") -> str:
        """Create a new idea file with proper naming and structure."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '-').lower()
        
        filename = f"{date_str}-{safe_title}.md"
        filepath = os.path.join('ideas', filename)
        
        # Read template
        template_path = os.path.join(Config.TEMPLATES_DIR, 'idea_template.md')
        template_content = self.read_file(template_path) or ""
        
        # Fill template
        content = template_content.format(
            title=title,
            date=date_str,
            tags=tags,
            description=description,
            notes=""
        )
        
        # Write file
        if self.write_file(filepath, content):
            return filepath
        else:
            raise Exception("Failed to create idea file")
    
    def get_file_status(self, path: str) -> Dict:
        """Get detailed status information for a file."""
        try:
            full_path = os.path.join(self.workspace_path, path)
            if not os.path.exists(full_path):
                return {'exists': False}
            
            stat = os.stat(full_path)
            return {
                'exists': True,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'type': 'directory' if os.path.isdir(full_path) else 'file'
            }
        except Exception as e:
            return {'exists': False, 'error': str(e)}
    
    def search_files(self, query: str, directory: str = "") -> List[Dict]:
        """Search for files containing the query."""
        results = []
        search_path = os.path.join(self.workspace_path, directory)
        
        if not os.path.exists(search_path):
            return results
        
        for root, dirs, files in os.walk(search_path):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if query.lower() in content.lower():
                                relative_path = os.path.relpath(file_path, self.workspace_path)
                                results.append({
                                    'path': relative_path,
                                    'name': file,
                                    'match_count': content.lower().count(query.lower())
                                })
                    except Exception:
                        continue
        
        return sorted(results, key=lambda x: x['match_count'], reverse=True) 