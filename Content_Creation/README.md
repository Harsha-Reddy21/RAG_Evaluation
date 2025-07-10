# 📝 Content Creation Tool

A GUI-based content creation tool with chat interface that helps content teams automate blog writing from idea capture to Medium publishing using local filesystem operations.

## 🚀 Features

### Core Features
- **💬 Chat-Based Idea Capture**: Natural language interface for capturing content ideas
- **🤖 AI Content Generation**: Automated content creation using OpenAI GPT-4
- **📁 Content Review Dashboard**: Visual file browser with approval workflow
- **🌐 One-Click Medium Publishing**: Direct publishing to Medium with proper formatting
- **🔍 Content Search**: Search across all content in the workspace
- **✏️ In-App Content Editor**: Rich text editing with enhancement options

### Technical Features
- **MCP Filesystem Integration**: Local file operations using FastMCP
- **OpenAI API Integration**: Advanced content generation and enhancement
- **Medium API Integration**: Direct publishing to Medium platform
- **Streamlit GUI**: Modern, responsive web interface
- **Local Workspace Management**: Organized file structure for content pipeline

## 📋 Requirements

- Python 3.8+
- OpenAI API key
- Medium API access token and user ID
- Internet connection for API calls

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Content_Creation
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your API keys:
   ```env
   # OpenAI API Configuration
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Medium API Configuration
   MEDIUM_ACCESS_TOKEN=your_medium_access_token_here
   MEDIUM_USER_ID=your_medium_user_id_here
   
   # MCP Filesystem Configuration
   MCP_FILESYSTEM_PATH=./content-workspace
   ```

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## 🔧 Setup Instructions

### OpenAI API Setup
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account and get your API key
3. Add the API key to your `.env` file

### Medium API Setup
1. Go to [Medium Developer Portal](https://medium.com/developers)
2. Create a new integration
3. Get your access token and user ID
4. Add them to your `.env` file

## 📖 Usage Guide

### 1. Idea Capture
```
Chat: "I want to write about MCP for developers"
```
- AI captures and structures your idea
- Saves to `ideas/` folder with metadata
- File naming: `YYYY-MM-DD-idea-title.md`

### 2. Content Generation
```
Chat: "Generate article from my MCP idea"
```
- Loads idea from local filesystem
- Calls OpenAI API for content generation
- Saves draft to `generated/` folder
- Shows content preview in chat

### 3. Content Review
- Use File Browser to view generated content
- Edit content in the in-app editor
- Approve content to move to `published/` folder

### 4. Medium Publishing
```
Chat: "Publish to Medium"
```
- Loads approved content
- Posts to Medium API
- Updates local file with Medium URL
- Shows success notification

## 🗂️ Workspace Structure

```
content-workspace/
├── ideas/          # Captured content ideas
├── generated/      # AI-generated drafts
├── published/      # Approved content ready for publishing
└── templates/      # Content templates
```

## 💬 Chat Commands

### Idea Management
- `"I want to write about [topic]"`
- `"Create idea about [topic]"`

### Content Generation
- `"Generate article from my idea"`
- `"Generate content"`

### Content Approval
- `"Approve content"`
- `"Ready to publish"`

### Publishing
- `"Publish to Medium"`
- `"Post to Medium"`

### Status & Search
- `"Show status"`
- `"Search for [query]"`

### Help
- `"help"`
- `"commands"`

## 🔄 Content Pipeline

```
1. Idea Capture → ideas/ folder
2. AI Generation → generated/ folder  
3. Human Review → Edit & Approve
4. Move to Published → published/ folder
5. Medium Publishing → Update with URL
```

## 🎛️ GUI Interface

### Chat Interface
- Natural language interaction
- Real-time responses
- Command history
- Success/error notifications

### File Browser
- Visual directory structure
- File metadata display
- Quick actions (Read, Edit, Approve, Publish)
- Tabbed organization (Ideas, Generated, Published, Templates)

### Content Editor
- Rich text editing
- Save/Refresh/Close options
- Content enhancement tools
- Real-time preview

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `MEDIUM_ACCESS_TOKEN`: Your Medium access token
- `MEDIUM_USER_ID`: Your Medium user ID
- `MCP_FILESYSTEM_PATH`: Local workspace path

### Customization
- Modify templates in `templates/` folder
- Adjust OpenAI prompts in `openai_service.py`
- Customize Medium formatting in `medium_service.py`

## 🚨 Troubleshooting

### Common Issues

1. **API Key Errors**
   - Verify API keys in `.env` file
   - Check API key permissions
   - Ensure internet connection

2. **File Permission Errors**
   - Check workspace directory permissions
   - Ensure write access to `content-workspace/`

3. **Medium Publishing Errors**
   - Verify Medium API credentials
   - Check content formatting
   - Ensure Medium account is active

4. **OpenAI Rate Limits**
   - Wait between requests
   - Check OpenAI account status
   - Verify API quota

### Debug Mode
Enable debug logging by setting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [FastMCP](https://github.com/jlowin/fastmcp) for filesystem operations
- [Streamlit](https://streamlit.io/) for the web interface
- [OpenAI](https://openai.com/) for content generation
- [Medium API](https://medium.com/developers) for publishing

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the chat commands with `"help"`

---

**Happy Content Creating! 🎉** 