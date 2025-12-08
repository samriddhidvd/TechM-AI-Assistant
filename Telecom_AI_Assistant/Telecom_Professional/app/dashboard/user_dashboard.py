"""
User Dashboard Module
Handles the user interface and dashboard functionality
"""

import streamlit as st
from typing import List, Tuple
import os

class UserDashboard:
    """Manages the user dashboard interface"""
    
    def __init__(self, chat_interface, resource_manager):
        """Initialize user dashboard with required services"""
        self.chat_interface = chat_interface
        self.resource_manager = resource_manager
    
    def render(self):
        """Render the user dashboard - EXACTLY as in original app.py"""
        st.title("🤖 AI Chatbot Assistant - Developed BY Samriddhi")
        
        # API Configuration Section
        self.render_api_config()
        
        # Document Access Indicator
        self.render_document_access()
        
        # User Access Board - NEW FEATURE
        self.render_user_access_board()
        
        # Chat interface - EXACTLY as in original app.py
        chat_container = st.container()
        with chat_container:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            
            # Display chat history - EXACTLY as in original app.py
            for message, response in st.session_state.chat_history:
                st.markdown(f'<div class="message user-message">{message}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="message bot-message">{response}</div>', unsafe_allow_html=True)
            
            # Chat input - EXACTLY as in original app.py
            user_message = st.text_input("Ask a question:", key="user_question")
            if st.button("Send", key="send_message"):
                if user_message:
                    with st.spinner("🤖 Multi-Agent AI is thinking..."):
                        response = self.get_chatbot_response(user_message, st.session_state.current_user[0])
                        st.session_state.chat_history.append((user_message, response))
                        st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def render_api_config(self):
        """Render API configuration section"""
        with st.expander("🔧 API Configuration", expanded=False):
            st.markdown("### Groq API Configuration")
            
            # Get default API key from environment variable
            default_api_key = os.getenv("GROQ_API_KEY", "")
            
            # API Key Input
            api_key = st.text_input(
                "Groq API Key:",
                value=st.session_state.get('groq_api_key', default_api_key),
                type="password",
                help="Enter your Groq API key. Get it from https://console.groq.com/"
            )
            
            if api_key:
                st.session_state.groq_api_key = api_key
                st.success("✅ API key saved!")
            else:
                st.warning("⚠️ Please enter your Groq API key to use the chatbot.")
            
            # Model Selection
            st.markdown("### Model Selection")
            available_models = [
                "llama3-8b-8192",
                "llama3-70b-8192", 
                "mixtral-8x7b-32768",
                "gemma2-9b-it",
                "llama2-70b-4096"
            ]
            
            selected_model = st.selectbox(
                "Choose AI Model:",
                available_models,
                index=0,
                help="Select the AI model to use for responses"
            )
            
            if selected_model:
                st.session_state.selected_model = selected_model
                st.info(f"🤖 Using model: {selected_model}")
            
            # Temperature Setting
            temperature = st.slider(
                "Response Creativity (Temperature):",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1,
                help="Lower values = more focused, Higher values = more creative"
            )
            
            if temperature != st.session_state.get('temperature', 0.7):
                st.session_state.temperature = temperature
                st.info(f"🎯 Temperature set to: {temperature}")
            
            # Max Tokens Setting
            max_tokens = st.slider(
                "Maximum Response Length:",
                min_value=100,
                max_value=2000,
                value=500,
                step=100,
                help="Maximum number of tokens in the response"
            )
            
            if max_tokens != st.session_state.get('max_tokens', 500):
                st.session_state.max_tokens = max_tokens
                st.info(f"📏 Max tokens set to: {max_tokens}")
    
    def render_document_access(self):
        """Render document access information"""
        if 'current_user' in st.session_state:
            user_id = st.session_state.current_user[0]
            user_resources = self.resource_manager.get_user_accessible_resources(user_id)
            
            if user_resources:
                with st.expander("📚 Your Accessible Documents", expanded=False):
                    st.markdown("### Documents You Can Ask About:")
                    
                    for i, resource in enumerate(user_resources, 1):
                        if len(resource) >= 2:
                            doc_name = resource[1]  # name
                            doc_type = resource[3] if len(resource) > 3 else "Unknown"  # file_type
                            extracted_text = resource[8] if len(resource) > 8 else None
                            text_length = len(extracted_text) if extracted_text and len(extracted_text.strip()) > 0 else 0
                            
                            col1, col2, col3 = st.columns([3, 1, 1])
                            with col1:
                                st.markdown(f"**{i}.** {doc_name}")
                            with col2:
                                st.markdown(f"*{doc_type}*")
                            with col3:
                                st.markdown(f"*{text_length} chars*")
                    
                    st.info("💡 **Tip**: I can only answer questions about the content of these documents. Ask me about specific information found in these files!")
            else:
                st.warning("⚠️ **No Documents Available**: You don't have access to any documents yet. Contact your administrator to upload relevant documents.")
        else:
            st.warning("⚠️ **Please Login**: You need to be logged in to access documents.")
    
    def render_user_access_board(self):
        """Render user access board showing which users have access to which data"""
        if 'current_user' in st.session_state and st.session_state.user_role == 'admin':
            with st.expander("👥 User Access Board", expanded=False):
                st.markdown("### User Data Access Matrix")
                
                try:
                    # Get all users and their access
                    with self.resource_manager.db_manager.get_connection() as conn:
                        cursor = conn.cursor()
                        
                        # Get all users
                        cursor.execute("SELECT id, username, role FROM users ORDER BY id")
                        users = cursor.fetchall()
                        
                        # Get all resources
                        cursor.execute("SELECT id, name, uploaded_by FROM resources ORDER BY id")
                        resources = cursor.fetchall()
                        
                        # Get permissions
                        cursor.execute("""
                            SELECT user_id, resource_id, can_access 
                            FROM permissions 
                            ORDER BY user_id, resource_id
                        """)
                        permissions = cursor.fetchall()
                        
                        # Create permission matrix
                        permission_matrix = {}
                        for user_id, resource_id, can_access in permissions:
                            if user_id not in permission_matrix:
                                permission_matrix[user_id] = {}
                            permission_matrix[user_id][resource_id] = can_access
                        
                        if users and resources:
                            # Create a table showing user access
                            st.markdown("#### User Access Matrix")
                            
                            # Header row
                            header_cols = st.columns([2] + [1] * len(resources))
                            with header_cols[0]:
                                st.markdown("**User**")
                            for i, resource in enumerate(resources):
                                with header_cols[i + 1]:
                                    st.markdown(f"**{resource[1][:15]}...**" if len(resource[1]) > 15 else f"**{resource[1]}**")
                            
                            # User rows
                            for user in users:
                                user_id, username, role = user
                                cols = st.columns([2] + [1] * len(resources))
                                
                                with cols[0]:
                                    st.markdown(f"**{username}** ({role})")
                                
                                for i, resource in enumerate(resources):
                                    resource_id = resource[0]
                                    with cols[i + 1]:
                                        # Check if user has access
                                        has_access = False
                                        
                                        # Check direct permissions
                                        if user_id in permission_matrix and resource_id in permission_matrix[user_id]:
                                            has_access = permission_matrix[user_id][resource_id]
                                        # Check if user uploaded the resource
                                        elif resource[2] == username:
                                            has_access = True
                                        # Admin has access to everything
                                        elif role == 'admin':
                                            has_access = True
                                        
                                        if has_access:
                                            st.markdown("✅")
                                        else:
                                            st.markdown("❌")
                            
                            # Summary statistics
                            st.markdown("---")
                            st.markdown("#### Access Summary")
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Total Users", len(users))
                            
                            with col2:
                                st.metric("Total Resources", len(resources))
                            
                            with col3:
                                total_access = sum(1 for user_id in permission_matrix.values() for access in user_id.values() if access)
                                st.metric("Total Permissions", total_access)
                            
                            # User-specific access details
                            st.markdown("#### User Access Details")
                            for user in users:
                                user_id, username, role = user
                                
                                # Get user's accessible resources
                                user_resources = self.resource_manager.get_user_accessible_resources(user_id)
                                
                                with st.expander(f"👤 {username} ({role})", expanded=False):
                                    if user_resources:
                                        st.markdown(f"**Access to {len(user_resources)} documents:**")
                                        for resource in user_resources:
                                            if len(resource) >= 2:
                                                doc_name = resource[1]
                                                doc_type = resource[3] if len(resource) > 3 else "Unknown"
                                                st.markdown(f"- {doc_name} ({doc_type})")
                                    else:
                                        st.markdown("❌ No documents accessible")
                                        
                        else:
                            st.warning("No users or resources found in database.")
                            
                except Exception as e:
                    st.error(f"Error loading user access board: {str(e)}")
        else:
            # For non-admin users, show their own access
            if 'current_user' in st.session_state:
                with st.expander("👤 Your Access Information", expanded=False):
                    st.markdown("### Your Document Access")
                    
                    user_id = st.session_state.current_user[0]
                    username = st.session_state.current_user[1]
                    role = st.session_state.user_role
                    
                    st.markdown(f"**User:** {username}")
                    st.markdown(f"**Role:** {role}")
                    st.markdown(f"**User ID:** {user_id}")
                    
                    # Get user's accessible resources
                    user_resources = self.resource_manager.get_user_accessible_resources(user_id)
                    
                    if user_resources:
                        st.markdown(f"**You have access to {len(user_resources)} documents:**")
                        for i, resource in enumerate(user_resources, 1):
                            if len(resource) >= 4:
                                doc_name = resource[1]
                                doc_type = resource[3]
                                uploaded_by = resource[4] if len(resource) > 4 else "Unknown"
                                st.markdown(f"{i}. **{doc_name}** ({doc_type}) - Uploaded by: {uploaded_by}")
                    else:
                        st.warning("You don't have access to any documents.")
            else:
                st.info("Please log in to view your access information.")
    
    def get_chatbot_response(self, message: str, user_id: int) -> str:
        """
        Get chatbot response for a given message and user - EXACTLY as in original app.py
        
        Args:
            message: User's message
            user_id: User's ID
            
        Returns:
            AI-generated response
        """
        try:
            # Check if API key is available
            api_key = st.session_state.get('groq_api_key', '')
            if not api_key:
                return "❌ Please configure your Groq API key in the API Configuration section above."
            
            # Get user role from session state or database
            user_role = st.session_state.user_role if st.session_state.user_role else "user"
            
            # Get user's accessible resources with extracted text
            user_resources = self.resource_manager.get_user_accessible_resources(user_id)
            
            # Get context from ChromaDB for better relevance
            try:
                from services.ai.chroma_service import ChromaService
                chroma_service = ChromaService()
                context = chroma_service.get_relevant_context(message, n_results=1)
                
                # If ChromaDB doesn't have relevant results, fall back to direct document access
                if context == "No relevant documents found." or context == "Error retrieving relevant context.":
                    if user_resources:
                        context_parts = []
                        for resource in user_resources:
                            # Handle the full resource tuple: (id, name, url, file_type, uploaded_by, uploaded_at, is_accessed, access_count, extracted_text, last_sync_time)
                            if len(resource) >= 9:  # Make sure we have enough columns
                                name = resource[1]  # name
                                extracted_text = resource[8] if len(resource) > 8 else None  # extracted_text
                                if extracted_text and len(extracted_text.strip()) > 0:
                                    context_parts.append(f"Document: {name}\nContent: {extracted_text[:500]}...")
                        context = "\n\n".join(context_parts)
                    else:
                        context = "No documents available for reference."
            except Exception as e:
                print(f"Error using ChromaDB: {e}")
                # Fallback to direct document access
                if user_resources:
                    context_parts = []
                    for resource in user_resources:
                        if len(resource) >= 9:
                            name = resource[1]
                            extracted_text = resource[8] if len(resource) > 8 else None
                            if extracted_text and len(extracted_text.strip()) > 0:
                                context_parts.append(f"Document: {name}\nContent: {extracted_text[:500]}...")
                    context = "\n\n".join(context_parts)
                else:
                    context = "No documents available for reference."
            
            # Optimized prompt for token limits
            system_prompt = f"""You are a Tech Mahindra AI assistant. Answer questions based on these documents:

{context}

Rules: Only answer questions about the documents above. If unrelated, say: 'I can only answer questions about the provided documents.' Be concise and professional.

User: {user_role.title()}"""
            
            # Generate response using Groq - EXACTLY as in original
            import groq
            from groq import Groq
            
            # Get configuration from session state
            selected_model = st.session_state.get('selected_model', 'llama3-8b-8192')
            temperature = st.session_state.get('temperature', 0.7)
            max_tokens = st.session_state.get('max_tokens', 500)
            
            groq_client = Groq(api_key=api_key)
            
            response = groq_client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            if "Invalid API Key" in str(e) or "401" in str(e):
                return "❌ Invalid API key. Please check your Groq API key in the configuration section."
            elif "rate limit" in str(e).lower():
                return "⚠️ Rate limit exceeded. Please try again in a moment."
            else:
                return f"Sorry, I encountered an error: {str(e)}" 