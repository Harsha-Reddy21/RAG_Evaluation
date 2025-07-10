import streamlit as st
import json
import os
from datetime import datetime
from typing import Dict, List
import traceback

# Import our modules
from config import Config
from content_manager import ContentManager
from mcp_filesystem import MCPFilesystemManager

# Page configuration
st.set_page_config(
    page_title="Content Creation Tool",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern, clean CSS for improved UI
st.markdown("""
<style>
body {
    background: #f6f8fa;
    font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
}
.main-header {
    font-size: 2.7rem;
    font-weight: 800;
    color: #2563eb;
    text-align: center;
    margin-bottom: 2rem;
    letter-spacing: -1px;
}
.chat-container {
    background: #f6f8fa;
    padding: 1.5rem 0;
    border-radius: 1rem;
    min-height: 400px;
}
.chat-bubble {
    display: flex;
    align-items: flex-end;
    margin-bottom: 1.2rem;
}
.bubble-user {
    background: #2563eb;
    color: #fff;
    border-radius: 1.2rem 1.2rem 0.2rem 1.2rem;
    margin-left: auto;
    box-shadow: 0 2px 8px rgba(37,99,235,0.08);
}
.bubble-assistant {
    background: #fff;
    color: #222;
    border-radius: 1.2rem 1.2rem 1.2rem 0.2rem;
    margin-right: auto;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    border: 1px solid #e5e7eb;
}
.bubble-content {
    padding: 1.1rem 1.4rem;
    font-size: 1.08rem;
    line-height: 1.7;
    max-width: 600px;
    word-break: break-word;
}
.bubble-meta {
    font-size: 0.85rem;
    color: #888;
    margin-top: 0.2rem;
    text-align: right;
}
.avatar {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    margin: 0 0.7rem;
    background: #e0e7ff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    font-weight: bold;
}
.avatar-user {
    background: #2563eb;
    color: #fff;
}
.avatar-assistant {
    background: #fbbf24;
    color: #fff;
}
.success-message {
    background: #e8f5e9;
    border-left: 4px solid #43a047;
    color: #256029;
    border-radius: 0.7rem;
    padding: 1rem 1.2rem;
    margin: 1rem 0;
    font-size: 1.08rem;
}
.error-message {
    background: #ffebee;
    border-left: 4px solid #e53935;
    color: #b71c1c;
    border-radius: 0.7rem;
    padding: 1rem 1.2rem;
    margin: 1rem 0;
    font-size: 1.08rem;
}
.file-browser {
    background: #fff;
    padding: 1.2rem 1.5rem;
    border-radius: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    margin: 1rem 0;
}
.status-card {
    background: #f1f5f9;
    padding: 1.1rem 1.3rem;
    border-radius: 0.8rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.03);
    margin: 0.5rem 0;
    font-size: 1.08rem;
}
.stTabs [data-baseweb="tab-list"] {
    background: #f1f5f9;
    border-radius: 0.7rem 0.7rem 0 0;
    padding: 0.3rem 0.5rem;
}
.stTabs [data-baseweb="tab"] {
    font-size: 1.1rem;
    font-weight: 600;
    color: #2563eb;
    padding: 0.7rem 1.2rem;
}
.stTabs [aria-selected="true"] {
    background: #fff;
    border-bottom: 2px solid #2563eb;
}
.stButton>button {
    background: #2563eb;
    color: #fff;
    border-radius: 0.6rem;
    font-size: 1.08rem;
    font-weight: 600;
    padding: 0.6rem 1.3rem;
    margin: 0.2rem 0.5rem 0.2rem 0;
    border: none;
    box-shadow: 0 1px 4px rgba(37,99,235,0.08);
    transition: background 0.2s;
}
.stButton>button:hover {
    background: #1d4ed8;
}
.stTextInput>div>input {
    font-size: 1.1rem;
    padding: 0.7rem 1.1rem;
    border-radius: 0.6rem;
    border: 1px solid #cbd5e1;
    background: #fff;
}
.stTextArea>div>textarea {
    font-size: 1.08rem;
    padding: 0.8rem 1.1rem;
    border-radius: 0.6rem;
    border: 1px solid #cbd5e1;
    background: #fff;
}
.stExpanderHeader {
    font-size: 1.08rem;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'content_manager' not in st.session_state:
    st.session_state.content_manager = None
if 'current_file' not in st.session_state:
    st.session_state.current_file = None
if 'file_content' not in st.session_state:
    st.session_state.file_content = ""
if 'last_input' not in st.session_state:
    st.session_state.last_input = ""

def initialize_app():
    """Initialize the application and services."""
    try:
        Config.validate_config()
        if st.session_state.content_manager is None:
            st.session_state.content_manager = ContentManager()
        return True
    except Exception as e:
        st.error(f"Initialization error: {str(e)}")
        st.info("Please check your .env file and ensure all API keys are configured.")
        return False

def add_chat_message(role: str, content: str, message_type: str = "normal"):
    st.session_state.chat_history.append({
        'role': role,
        'content': content,
        'type': message_type,
        'timestamp': datetime.now().strftime("%H:%M:%S")
    })

def display_chat_history():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for message in st.session_state.chat_history:
        if message['role'] == "User":
            avatar = '<div class="avatar avatar-user">🧑</div>'
            bubble_class = "bubble-user"
        else:
            avatar = '<div class="avatar avatar-assistant">🤖</div>'
            bubble_class = "bubble-assistant"
        meta = f'<div class="bubble-meta">{message["role"]} <span style="font-size:0.8em;">({message["timestamp"]})</span></div>'
        bubble = f'''<div class="chat-bubble {bubble_class}">{avatar}<div><div class="bubble-content">{message["content"]}</div>{meta}</div></div>'''
        st.markdown(bubble, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def process_chat_command(user_input: str):
    try:
        cm = st.session_state.content_manager
        if any(phrase in user_input.lower() for phrase in ["i want to write about", "create idea", "new idea"]):
            add_chat_message("User", user_input)
            with st.spinner("Capturing your idea..."):
                result = cm.capture_idea(user_input)
            if result['success']:
                add_chat_message("Assistant", result['message'], "success")
                st.success(f"✅ {result['message']}")
            else:
                add_chat_message("Assistant", result['message'], "error")
                st.error(f"❌ {result['message']}")
        elif any(phrase in user_input.lower() for phrase in ["generate article", "generate content", "create article"]):
            add_chat_message("User", user_input)
            ideas = cm.filesystem.list_directory('ideas')
            if not ideas:
                add_chat_message("Assistant", "No ideas found. Please create an idea first.", "error")
                st.error("❌ No ideas found. Please create an idea first.")
                return
            latest_idea = ideas[-1]['path']
            with st.spinner("Generating content..."):
                result = cm.generate_content_from_idea(latest_idea)
            if result['success']:
                add_chat_message("Assistant", result['message'], "success")
                st.success(f"✅ {result['message']}")
                with st.expander("📄 Content Preview"):
                    st.markdown(result['content'][:500] + "...")
            else:
                add_chat_message("Assistant", result['message'], "error")
                st.error(f"❌ {result['message']}")
        elif any(phrase in user_input.lower() for phrase in ["approve", "approve content", "ready to publish"]):
            add_chat_message("User", user_input)
            generated = cm.filesystem.list_directory('generated')
            if not generated:
                add_chat_message("Assistant", "No generated content found to approve.", "error")
                st.error("❌ No generated content found to approve.")
                return
            latest_generated = generated[-1]['path']
            with st.spinner("Approving content..."):
                result = cm.approve_content(latest_generated)
            if result['success']:
                add_chat_message("Assistant", result['message'], "success")
                st.success(f"✅ {result['message']}")
            else:
                add_chat_message("Assistant", result['message'], "error")
                st.error(f"❌ {result['message']}")
        elif any(phrase in user_input.lower() for phrase in ["publish to medium", "publish", "post to medium"]):
            add_chat_message("User", user_input)
            published = cm.filesystem.list_directory('published')
            if not published:
                add_chat_message("Assistant", "No approved content found to publish.", "error")
                st.error("❌ No approved content found to publish.")
                return
            latest_published = published[-1]['path']
            with st.spinner("Publishing to Medium..."):
                result = cm.publish_to_medium(latest_published)
            if result['success']:
                add_chat_message("Assistant", result['message'], "success")
                st.success(f"✅ {result['message']}")
                if 'medium_url' in result:
                    st.info(f"🌐 View your post: {result['medium_url']}")
            else:
                add_chat_message("Assistant", result['message'], "error")
                st.error(f"❌ {result['message']}")
        elif any(phrase in user_input.lower() for phrase in ["status", "show status", "workspace status"]):
            add_chat_message("User", user_input)
            status = cm.get_workspace_status()
            status_message = f"""
            📊 Workspace Status:
            • Ideas: {status['ideas_count']}
            • Generated: {status['generated_count']}
            • Published: {status['published_count']}
            """
            add_chat_message("Assistant", status_message)
            st.info(status_message)
        elif any(phrase in user_input.lower() for phrase in ["help", "commands", "what can you do"]):
            add_chat_message("User", user_input)
            help_message = """
            🤖 <b>Available Commands:</b><br><br>
            📝 <b>Idea Capture:</b> "I want to write about [topic]" • "Create idea about [topic]"<br>
            ✍️ <b>Content Generation:</b> "Generate article from my idea" • "Generate content"<br>
            ✅ <b>Content Approval:</b> "Approve content" • "Ready to publish"<br>
            🌐 <b>Publishing:</b> "Publish to Medium" • "Post to Medium"<br>
            📊 <b>Status:</b> "Show status" • "Workspace status"<br>
            🔍 <b>Search:</b> "Search for [query]"<br>
            """
            add_chat_message("Assistant", help_message)
            st.info("Available commands are shown above.")
        elif user_input.lower().startswith("search for "):
            query = user_input[11:]
            add_chat_message("User", user_input)
            with st.spinner("Searching..."):
                results = cm.search_content(query)
            if results and not results[0].get('error'):
                search_message = f"🔍 Found {len(results)} results for '{query}':\n"
                for result in results[:5]:
                    search_message += f"• {result['type'].title()}: {result['name']}\n"
                add_chat_message("Assistant", search_message)
                st.info(search_message)
            else:
                add_chat_message("Assistant", f"No results found for '{query}'", "error")
                st.warning(f"🔍 No results found for '{query}'")
        else:
            add_chat_message("User", user_input)
            response = "I understand you said: " + user_input + "\n\nTry saying 'help' to see available commands."
            add_chat_message("Assistant", response)
            st.info(response)
    except Exception as e:
        error_message = f"Error processing command: {str(e)}"
        add_chat_message("Assistant", error_message, "error")
        st.error(f"❌ {error_message}")

def display_file_browser():
    """Display the file browser interface."""
    st.subheader("📁 File Browser")
    
    try:
        cm = st.session_state.content_manager
        status = cm.get_workspace_status()
        
        # Create tabs for different directories
        tab1, tab2, tab3, tab4 = st.tabs(["💡 Ideas", "✍️ Generated", "✅ Published", "📋 Templates"])
        
        with tab1:
            st.write(f"**Ideas ({status['ideas_count']})**")
            for idea in status['ideas']:
                with st.expander(f"📄 {idea['name']}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Modified:** {idea['modified']}")
                        st.write(f"**Size:** {idea['size']} bytes")
                    with col2:
                        if st.button("📖 Read", key=f"read_idea_{idea['name']}"):
                            content = cm.filesystem.read_file(idea['path'])
                            st.session_state.current_file = idea['path']
                            st.session_state.file_content = content
                        if st.button("✏️ Edit", key=f"edit_idea_{idea['name']}"):
                            st.session_state.current_file = idea['path']
                            st.session_state.file_content = cm.filesystem.read_file(idea['path'])
        
        with tab2:
            st.write(f"**Generated ({status['generated_count']})**")
            for generated in status['generated']:
                with st.expander(f"📄 {generated['name']}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Modified:** {generated['modified']}")
                        st.write(f"**Size:** {generated['size']} bytes")
                    with col2:
                        if st.button("📖 Read", key=f"read_gen_{generated['name']}"):
                            content = cm.filesystem.read_file(generated['path'])
                            st.session_state.current_file = generated['path']
                            st.session_state.file_content = content
                        if st.button("✏️ Edit", key=f"edit_gen_{generated['name']}"):
                            st.session_state.current_file = generated['path']
                            st.session_state.file_content = cm.filesystem.read_file(generated['path'])
                        if st.button("✅ Approve", key=f"approve_{generated['name']}"):
                            result = cm.approve_content(generated['path'])
                            if result['success']:
                                st.success(result['message'])
                                st.rerun()
                            else:
                                st.error(result['message'])
        
        with tab3:
            st.write(f"**Published ({status['published_count']})**")
            for published in status['published']:
                with st.expander(f"📄 {published['name']}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Modified:** {published['modified']}")
                        st.write(f"**Size:** {published['size']} bytes")
                    with col2:
                        if st.button("📖 Read", key=f"read_pub_{published['name']}"):
                            content = cm.filesystem.read_file(published['path'])
                            st.session_state.current_file = published['path']
                            st.session_state.file_content = content
                        if st.button("🌐 Publish", key=f"publish_{published['name']}"):
                            result = cm.publish_to_medium(published['path'])
                            if result['success']:
                                st.success(result['message'])
                                if 'medium_url' in result:
                                    st.info(f"🌐 {result['medium_url']}")
                                st.rerun()
                            else:
                                st.error(result['message'])
        
        with tab4:
            templates = cm.filesystem.list_directory('templates')
            st.write(f"**Templates ({len(templates)})**")
            for template in templates:
                with st.expander(f"📋 {template['name']}"):
                    st.write(f"**Modified:** {template['modified']}")
                    if st.button("📖 View", key=f"view_template_{template['name']}"):
                        content = cm.filesystem.read_file(template['path'])
                        st.code(content, language='markdown')
    
    except Exception as e:
        st.error(f"Error displaying file browser: {str(e)}")

def display_content_editor():
    """Display the content editor interface."""
    st.subheader("✏️ Content Editor")
    
    if st.session_state.current_file:
        st.write(f"**Editing:** {st.session_state.current_file}")
        
        # Content editor
        edited_content = st.text_area(
            "Content",
            value=st.session_state.file_content,
            height=400,
            key="content_editor"
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Save"):
                try:
                    cm = st.session_state.content_manager
                    success = cm.filesystem.write_file(st.session_state.current_file, edited_content)
                    if success:
                        st.success("✅ Content saved successfully!")
                        st.session_state.file_content = edited_content
                    else:
                        st.error("❌ Failed to save content")
                except Exception as e:
                    st.error(f"❌ Error saving: {str(e)}")
        
        with col2:
            if st.button("🔄 Refresh"):
                try:
                    cm = st.session_state.content_manager
                    content = cm.filesystem.read_file(st.session_state.current_file)
                    st.session_state.file_content = content
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error refreshing: {str(e)}")
        
        with col3:
            if st.button("❌ Close"):
                st.session_state.current_file = None
                st.session_state.file_content = ""
                st.rerun()
        
        # Enhancement options
        st.write("**Enhancement Options:**")
        enhancement_type = st.selectbox(
            "Select enhancement type:",
            ["seo", "readability", "engagement", "professional"],
            key="enhancement_type"
        )
        
        if st.button("✨ Enhance Content"):
            try:
                cm = st.session_state.content_manager
                with st.spinner("Enhancing content..."):
                    result = cm.enhance_content(st.session_state.current_file, enhancement_type)
                
                if result['success']:
                    st.success(f"✅ {result['message']}")
                    # Refresh content
                    content = cm.filesystem.read_file(st.session_state.current_file)
                    st.session_state.file_content = content
                    st.rerun()
                else:
                    st.error(f"❌ {result['message']}")
            except Exception as e:
                st.error(f"❌ Error enhancing content: {str(e)}")
    
    else:
        st.info("Select a file from the File Browser to edit its content.")

def main():
    """Main application function."""
    st.markdown('<h1 class="main-header">📝 Content Creation Tool</h1>', unsafe_allow_html=True)
    
    # Initialize app
    if not initialize_app():
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Controls")
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        
        if st.button("📊 Show Status"):
            cm = st.session_state.content_manager
            status = cm.get_workspace_status()
            st.info(f"""
            📊 Workspace Status:
            • Ideas: {status['ideas_count']}
            • Generated: {status['generated_count']}
            • Published: {status['published_count']}
            """)
        
        if st.button("🔄 Refresh All"):
            st.rerun()
        
        # Configuration info
        st.subheader("⚙️ Configuration")
        st.write(f"**Workspace:** {Config.MCP_FILESYSTEM_PATH}")
        st.write(f"**OpenAI:** {'✅ Configured' if Config.OPENAI_API_KEY else '❌ Missing'}")
        st.write(f"**Medium:** {'✅ Configured' if Config.MEDIUM_ACCESS_TOKEN else '❌ Missing'}")
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["💬 Chat Interface", "📁 File Browser", "✏️ Content Editor"])
    
    with tab1:
        st.subheader("💬 Chat Interface")
        st.write("Use natural language to interact with the content creation tool.")
        
        # Chat input
        user_input = st.text_input(
            "Type your message:",
            placeholder="Try: 'I want to write about MCP for developers' or 'help' for commands",
            key="chat_input"
        )
        
        # Handle chat input submission
        if st.button("Send", key="send_button"):
            if user_input:
                process_chat_command(user_input)
                st.rerun()
        
        # Handle Enter key submission
        if user_input and user_input != st.session_state.get('last_input', ''):
            process_chat_command(user_input)
            st.session_state.last_input = user_input
            st.rerun()
        
        # Chat history
        st.subheader("💭 Chat History")
        display_chat_history()
    
    with tab2:
        display_file_browser()
    
    with tab3:
        display_content_editor()

if __name__ == "__main__":
    main() 