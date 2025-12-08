"""
Tech Mahindra AI Assistant - Main Application
Main entry point for the enterprise AI assistant platform
"""

import streamlit as st
import os
import sys
import base64
from datetime import datetime

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import configuration and services
from config.settings import Config
from database.models import DatabaseManager, UserManager, ResourceManager, PermissionManager, ChatHistoryManager
from services.ai.chatbot_service import ChatbotService, MultiAgentSystem

# Import UI components
from app.auth.login import LoginManager
from app.chat.chat_interface import ChatInterface
from app.dashboard.admin_dashboard import AdminDashboard
from app.dashboard.user_dashboard import UserDashboard

class TechMahindraAI:
    """Main application class that orchestrates all components"""
    
    def __init__(self):
        """Initialize the application with all required services"""
        self.setup_page_config()
        self.initialize_services()
        self.setup_session_state()
        self.load_custom_styles()
    
    def setup_page_config(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title=Config.APP_TITLE,
            page_icon=Config.APP_ICON,
            layout=Config.LAYOUT,
            initial_sidebar_state=Config.SIDEBAR_STATE
        )
    
    def initialize_services(self):
        """Initialize all application services"""
        # Initialize database managers
        self.db_manager = DatabaseManager(Config.DATABASE_PATH)
        self.user_manager = UserManager(self.db_manager)
        self.resource_manager = ResourceManager(self.db_manager)
        self.permission_manager = PermissionManager(self.db_manager)
        self.chat_history_manager = ChatHistoryManager(self.db_manager)
        
        # Initialize AI services
        self.chatbot_service = ChatbotService()
        self.multi_agent_system = MultiAgentSystem(self.chatbot_service)
        
        # Initialize UI managers
        self.login_manager = LoginManager(self.user_manager)
        self.chat_interface = ChatInterface(
            self.chatbot_service, 
            self.multi_agent_system,
            self.resource_manager,
            self.chat_history_manager
        )
        self.admin_dashboard = AdminDashboard(
            self.user_manager,
            self.resource_manager,
            self.permission_manager
        )
        self.user_dashboard = UserDashboard(
            self.chat_interface,
            self.resource_manager
        )
    
    def setup_session_state(self):
        """Initialize session state variables"""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'current_user' not in st.session_state:
            st.session_state.current_user = None
        if 'user_role' not in st.session_state:
            st.session_state.user_role = None
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'sync_in_progress' not in st.session_state:
            st.session_state.sync_in_progress = False
        if 'last_sync_folder' not in st.session_state:
            st.session_state.last_sync_folder = None
    
    def load_custom_styles(self):
        """Load custom CSS styles"""
        css_path = os.path.join(project_root, 'static', 'css', 'styles.css')
        try:
            with open(css_path, 'r') as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        except FileNotFoundError:
            st.error(f"CSS file not found at: {css_path}")
            # Fallback to embedded styles
            st.markdown("""
            <style>
            body, .stApp {
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 25%, #334155 50%, #475569 75%, #64748b 100%);
                background-attachment: fixed;
            }
            </style>
            """, unsafe_allow_html=True)
    
    def create_download_directory(self):
        """Ensure download directory exists"""
        os.makedirs(Config.DOWNLOAD_DIR, exist_ok=True)
    
    def load_company_logo(self):
        """Load and encode company logo"""
        try:
            logo_path = "static/images/tech_mahindra_logo.png"
            if os.path.exists(logo_path):
                with open(logo_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode()
                return encoded_string
            else:
                # Return empty string if logo not found
                return ""
        except Exception as e:
            print(f"Error loading logo: {e}")
            return ""
    
    def render_login_page(self):
        """Render the login/register page"""
        logo_encoded = self.load_company_logo()
        
        st.markdown(f'''
        <div class="login-container">
            <img src="data:image/png;base64,{logo_encoded}" alt="Tech Mahindra Logo" class="company-logo">
            <div class="login-title">Tech Mahindra AI</div>
            <div class="login-subtitle">Enterprise AI Assistant Platform</div>
            <div class="developer-credit">Developed BY Samriddhi</div>
        ''', unsafe_allow_html=True)
        
        # Render login interface
        self.login_manager.render_login_interface()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render the application sidebar"""
        with st.sidebar:
            if st.session_state.current_user:
                st.markdown(f"### Welcome, {st.session_state.current_user[1]}!")
                st.markdown(f"**Role:** {st.session_state.user_role.title()}")
                
                st.markdown("---")
                st.markdown("**Developed BY Samriddhi**")
                st.markdown("*Tech Mahindra AI Assistant*")
                
                # Add session clear button for debugging
                if st.button("🧹 Clear Chat Session"):
                    if 'chat_history' in st.session_state:
                        del st.session_state.chat_history
                    st.session_state.chat_history = []
                    st.success("Chat session cleared!")
                    st.rerun()
                
                if st.button("Logout"):
                    self.logout_user()
    
    def logout_user(self):
        """Handle user logout"""
        st.session_state.authenticated = False
        st.session_state.current_user = None
        st.session_state.user_role = None
        st.session_state.chat_history = []
        st.rerun()
    
    def render_main_application(self):
        """Render the main application after login"""
        self.render_sidebar()
        
        if st.session_state.user_role == "admin":
            self.admin_dashboard.render()
        else:
            self.user_dashboard.render()
    
    def render_footer(self):
        """Render the application footer"""
        st.markdown("""
        <div class="footer">
            <p><strong>Developed BY Samriddhi</strong></p>
            <p style="font-size: 0.9rem; margin-top: 0.5rem;">Tech Mahindra AI Assistant Platform</p>
            <p style="font-size: 0.8rem; margin-top: 1rem; opacity: 0.7;">Multi-Agent System with Advanced Document Management</p>
        </div>
        """, unsafe_allow_html=True)
    
    def run(self):
        """Main application run method"""
        try:
            # Create necessary directories
            self.create_download_directory()
            
            # Check if user is authenticated
            if not st.session_state.authenticated:
                self.render_login_page()
            else:
                self.render_main_application()
            
            # Render footer
            self.render_footer()
            
        except Exception as e:
            st.error(f"Application Error: {str(e)}")
            st.info("Please refresh the page or contact support if the issue persists.")

def main():
    """Main entry point for the application"""
    app = TechMahindraAI()
    app.run()

if __name__ == "__main__":
    main() 