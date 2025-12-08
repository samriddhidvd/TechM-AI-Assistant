"""
Authentication Module
Handles user login, registration, and session management
"""

import streamlit as st
from config.settings import Config

class LoginManager:
    """Manages user authentication and registration"""
    
    def __init__(self, user_manager):
        """Initialize login manager with user manager"""
        self.user_manager = user_manager
    
    def render_login_interface(self):
        """Render the login and registration interface"""
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            self.render_login_tab()
        
        with tab2:
            self.render_register_tab()
    
    def render_login_tab(self):
        """Render the login tab"""
        st.markdown("### Welcome Back")
        
        # Username input
        username = st.text_input(
            "👤 Username", 
            key="login_username", 
            placeholder="Enter your username"
        )
        
        # Password visibility toggle
        show_password = st.checkbox("👁️ Show Password", value=False, key="show_login_pw")
        
        # Password input
        password = st.text_input(
            "🔒 Password", 
            type="default" if show_password else "password", 
            key="login_password", 
            placeholder="Enter your password"
        )
        
        # Login buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Login as User", use_container_width=True):
                self.handle_login(username, password, "user")
        
        with col2:
            if st.button("👑 Login as Admin", use_container_width=True):
                self.handle_login(username, password, "admin")
    
    def render_register_tab(self):
        """Render the registration tab"""
        st.markdown("### Create New Account")
        
        # Registration form
        new_username = st.text_input(
            "👤 Username", 
            key="register_username", 
            placeholder="Choose a username"
        )
        
        # Password visibility toggle
        show_reg_pw = st.checkbox("👁️ Show Password", value=False, key="show_reg_pw")
        
        # Password inputs
        new_password = st.text_input(
            "🔒 Password", 
            type="default" if show_reg_pw else "password", 
            key="register_password", 
            placeholder="Create a strong password"
        )
        
        confirm_password = st.text_input(
            "🔐 Confirm Password", 
            type="default" if show_reg_pw else "password", 
            key="confirm_password", 
            placeholder="Confirm your password"
        )
        
        # Role selection
        role = st.selectbox("🎭 Role", ["user", "admin"], key="register_role")
        
        # Register button
        if st.button("📝 Register Account", use_container_width=True):
            self.handle_registration(new_username, new_password, confirm_password, role)
    
    def handle_login(self, username: str, password: str, expected_role: str):
        """Handle user login process"""
        if not username or not password:
            st.error("❌ Please enter both username and password")
            return
        
        with st.spinner("🔐 Authenticating..."):
            user = self.user_manager.verify_user(username, password)
            
            if user and user[3] == expected_role:
                # Login successful
                st.session_state.authenticated = True
                st.session_state.current_user = user
                st.session_state.user_role = expected_role
                st.success("✅ Login successful!")
                st.rerun()
            else:
                # Login failed
                st.error("❌ Invalid credentials or insufficient permissions")
    
    def handle_registration(self, username: str, password: str, confirm_password: str, role: str):
        """Handle user registration process"""
        # Validate inputs
        if not username or not password or not confirm_password:
            st.error("❌ Please fill in all fields")
            return
        
        if password != confirm_password:
            st.error("❌ Passwords do not match")
            return
        
        if len(password) < Config.PASSWORD_MIN_LENGTH:
            st.error(f"❌ Password must be at least {Config.PASSWORD_MIN_LENGTH} characters")
            return
        
        # Attempt to create user
        with st.spinner("📝 Creating account..."):
            if self.user_manager.create_user(username, password, role):
                st.success("✅ Account created successfully! Please login.")
            else:
                st.error("❌ Username already exists")
    
    def validate_password_strength(self, password: str) -> tuple[bool, str]:
        """
        Validate password strength
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < Config.PASSWORD_MIN_LENGTH:
            return False, f"Password must be at least {Config.PASSWORD_MIN_LENGTH} characters"
        
        # Check for common weak passwords
        weak_passwords = ["password", "123456", "admin", "user"]
        if password.lower() in weak_passwords:
            return False, "Password is too common. Please choose a stronger password."
        
        return True, ""
    
    def validate_username(self, username: str) -> tuple[bool, str]:
        """
        Validate username format
        
        Args:
            username: Username to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(username) > 20:
            return False, "Username must be less than 20 characters"
        
        # Check for valid characters
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Username can only contain letters, numbers, and underscores"
        
        return True, ""
    
    def get_user_info(self) -> dict:
        """Get current user information"""
        if not st.session_state.current_user:
            return {}
        
        user = st.session_state.current_user
        return {
            'id': user[0],
            'username': user[1],
            'role': user[3],
            'created_at': user[4] if len(user) > 4 else None
        }
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated"""
        return st.session_state.authenticated
    
    def get_user_role(self) -> str:
        """Get current user's role"""
        return st.session_state.user_role if st.session_state.user_role else "user"
    
    def logout(self):
        """Logout current user"""
        st.session_state.authenticated = False
        st.session_state.current_user = None
        st.session_state.user_role = None
        st.session_state.chat_history = []
        st.rerun() 