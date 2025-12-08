"""
Chat Interface Module
Handles the chat interface and user interactions
"""

import streamlit as st
from typing import List, Tuple
import os

class ChatInterface:
    """Manages the chat interface and user interactions"""
    
    def __init__(self, chatbot_service, multi_agent_system, resource_manager, chat_history_manager):
        """Initialize chat interface with required services"""
        self.chatbot_service = chatbot_service
        self.multi_agent_system = multi_agent_system
        self.resource_manager = resource_manager
        self.chat_history_manager = chat_history_manager
    
    def render_chat_interface(self):
        """Render the complete chat interface with professional dark theme"""
        
        # Load professional dark theme CSS
        self.load_professional_styles()
        
        # Professional Header
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem; padding: 2rem; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.3);">
            <h1 style="background: linear-gradient(45deg, #00d4ff, #0099cc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem;">
                🚀 Tech Mahindra AI Assistant
            </h1>
            <p style="color: #b8c5d6; font-size: 1.1rem; margin: 0; opacity: 0.9;">
                Enterprise-Grade Multi-Agent AI Platform
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Professional Layout with Columns
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # API Configuration Section
            self.render_api_config()
            
            # Document Access Indicator
            self.render_document_access()
        
        with col2:
            # User Access Board
            self.render_user_access_board()
        
        # Professional Chat Interface
        st.markdown("""
        <div style="margin: 2rem 0; padding: 1.5rem; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 15px; border: 1px solid #2a2a3e;">
            <h2 style="color: #00d4ff; margin-bottom: 1rem; font-weight: 600;">💬 AI Conversation</h2>
        </div>
        """, unsafe_allow_html=True)
        
        chat_container = st.container()
        with chat_container:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            
            # Professional Chat History Display
            if st.session_state.chat_history:
                st.markdown('<div style="margin-bottom: 1.5rem;"><h3 style="color: #b8c5d6; font-weight: 500;">📝 Conversation History</h3></div>', unsafe_allow_html=True)
                
                for i, (message, response) in enumerate(st.session_state.chat_history):
                    # User Message with Professional Styling
                    st.markdown(f'''
                    <div class="message user-message">
                        <div style="font-weight: 600; margin-bottom: 0.5rem; color: #ffffff;">👤 You</div>
                        <div style="color: #e8f4fd;">{message}</div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    # Bot Message with Professional Styling
                    st.markdown(f'''
                    <div class="message bot-message">
                        <div style="font-weight: 600; margin-bottom: 0.5rem; color: #00d4ff;">🤖 AI Assistant</div>
                        <div style="color: #d1d5db;">{response}</div>
                    </div>
                    ''', unsafe_allow_html=True)
            
            # Professional Chat Input Section
            st.markdown('<div style="margin-top: 2rem; padding-top: 1.5rem; border-top: 2px solid #2a2a3e;"><h3 style="color: #b8c5d6; font-weight: 500;">💭 Ask Your Question</h3></div>', unsafe_allow_html=True)
            
            # Enhanced Input with Placeholder
            user_message = st.text_input(
                "Enter your question here...",
                key="user_question",
                placeholder="Ask about the documents you have access to..."
            )
            
            # Professional Send Button
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🚀 Send Message", key="send_message", use_container_width=True):
                    if user_message:
                        with st.spinner("🤖 AI is processing your request..."):
                            response = self.get_chatbot_response(user_message, st.session_state.current_user[0])
                            st.session_state.chat_history.append((user_message, response))
                            st.rerun()
                    else:
                        st.warning("⚠️ Please enter a question before sending.")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def render_api_config(self):
        """Render API configuration section with professional styling"""
        with st.expander("🔧 API Configuration", expanded=False):
            st.markdown("""
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                        padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem; border: 1px solid #2a2a3e;">
                <h3 style="color: #00d4ff; margin: 0; font-weight: 600;">⚙️ AI Model Configuration</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Professional API Key Section
            st.markdown("### 🔑 API Authentication")
            default_api_key = os.getenv("GROQ_API_KEY", "")
            
            api_key = st.text_input(
                "Groq API Key:",
                value=st.session_state.get('groq_api_key', default_api_key),
                type="password",
                help="Enter your Groq API key. Get it from https://console.groq.com/",
                placeholder="sk_... (your API key here)"
            )
            
            if api_key:
                st.session_state.groq_api_key = api_key
                st.success("✅ API key configured successfully!")
            else:
                st.warning("⚠️ Please enter your Groq API key to use the chatbot.")
            
            # Professional Model Selection
            st.markdown("### 🤖 AI Model Selection")
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
                st.info(f"🤖 Active Model: {selected_model}")
            
            # Professional Temperature Setting
            st.markdown("### 🎛️ Response Settings")
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
        """Render document access information with professional styling"""
        if 'current_user' in st.session_state:
            user_id = st.session_state.current_user[0]
            user_resources = self.resource_manager.get_user_accessible_resources(user_id)
            
            if user_resources:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #1a4d2e 0%, #2d5a3d 100%); 
                            padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem; border: 1px solid #3a5a4a;">
                    <h3 style="color: #ffffff; margin: 0; font-weight: 600;">📚 Your Document Access</h3>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div style="background: #16213e; padding: 1rem; border-radius: 8px; border-left: 4px solid #00d4ff; margin-bottom: 1rem;">
                    <p style="color: #b8c5d6; margin: 0; font-size: 0.9rem;">
                        💡 <strong>AI Assistant Tip:</strong> I can only answer questions about the content of these documents. 
                        Ask me about specific information found in these files!
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Professional Document Cards
                for i, resource in enumerate(user_resources, 1):
                    if len(resource) >= 2:
                        doc_name = resource[1]  # name
                        doc_type = resource[4] if len(resource) > 4 else "Unknown"  # file_type
                        uploaded_by = resource[3] if len(resource) > 3 else "Unknown"  # uploaded_by
                        
                        # Professional document card
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #2a2a3e 0%, #3a3a4e 100%); 
                                    border: 1px solid #4a4a5e; border-radius: 12px; padding: 1.5rem; 
                                    margin: 0.5rem 0; transition: all 0.3s ease; box-shadow: 0 4px 16px rgba(0,0,0,0.2);">
                            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                                <span style="background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%); 
                                           color: white; padding: 0.3rem 0.8rem; border-radius: 6px; 
                                           font-size: 0.8rem; margin-right: 0.8rem; font-weight: 600;">
                                    {i}
                                </span>
                                <strong style="color: #ffffff; flex-grow: 1;">{doc_name}</strong>
                                <span style="background: #4a4a5e; color: #b8c5d6; padding: 0.3rem 0.8rem; 
                                           border-radius: 6px; font-size: 0.7rem; font-weight: 500;">
                                    {doc_type.upper()}
                                </span>
                            </div>
                            <div style="color: #b8c5d6; font-size: 0.9rem;">
                                📤 Uploaded by: <span style="color: #00d4ff; font-weight: 500;">{uploaded_by}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #4d3a1a 0%, #5d4a2a 100%); 
                            padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem; border: 1px solid #6d5a3a;">
                    <h3 style="color: #ffffff; margin: 0; font-weight: 600;">⚠️ No Document Access</h3>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div style="background: #16213e; padding: 1rem; border-radius: 8px; border-left: 4px solid #ffa500;">
                    <p style="color: #b8c5d6; margin: 0;">
                        You don't have access to any documents yet. Contact your administrator to upload relevant documents.
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: #16213e; padding: 1rem; border-radius: 8px; border-left: 4px solid #00d4ff;">
                <p style="color: #b8c5d6; margin: 0;">
                    ℹ️ Please log in to view your document access.
                </p>
            </div>
            """, unsafe_allow_html=True)
    
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
                                                uploaded_by = resource[4] if len(resource) > 4 else "Unknown"
                                                st.markdown(f"- {doc_name} ({doc_type}) - Uploaded by: {uploaded_by}")
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
            
            # Create context from user's documents
            if user_resources:
                context_parts = []
                for resource in user_resources:
                    # Handle the full resource tuple: (id, name, url, file_type, uploaded_by, uploaded_at, is_accessed, access_count, extracted_text, last_sync_time)
                    if len(resource) >= 9:  # Make sure we have enough columns
                        name = resource[1]  # name
                        extracted_text = resource[8] if len(resource) > 8 else None  # extracted_text
                        if extracted_text and len(extracted_text.strip()) > 0:
                            context_parts.append(f"Document: {name}\nContent: {extracted_text[:2000]}...")
                context = "\n\n".join(context_parts)
            else:
                context = "No documents available for reference."
            
            # Try to get relevant context from ChromaDB if available
            try:
                from services.ai.chroma_service import ChromaService
                chroma_service = ChromaService()
                chroma_context = chroma_service.get_relevant_context(message)
                if chroma_context and chroma_context != "No relevant documents found.":
                    # Combine database context with ChromaDB context
                    context = f"{context}\n\nRelevant Context from Vector Search:\n{chroma_context}"
            except Exception as chroma_error:
                # If ChromaDB fails, continue with database context only
                pass
            
            # Strict prompt engineering: refuse unrelated questions - EXACTLY as in original
            system_prompt = f"""You are a specialized AI assistant for Tech Mahindra that can ONLY answer questions based on the specific documents and data you have been provided access to.

CRITICAL RESTRICTIONS:
1. **STRICT DATA BOUNDARY**: You can ONLY answer questions that are directly related to the content of the documents provided to you.
2. **NO GENERAL KNOWLEDGE**: You must NOT answer general knowledge questions, current events, weather, cooking, math, or any topic outside your provided documents.
3. **NO CREATIVE RESPONSES**: You must NOT make up information, provide opinions, or generate creative content.
4. **NO EXTERNAL KNOWLEDGE**: You must NOT use any knowledge from your training data that is not present in the provided documents.
5. **ROLE-BASED ACCESS**: You have {user_role} access and can only discuss documents you have permission to view.

RESPONSE PROTOCOL:
- If a question is related to your documents: Answer based ONLY on the document content
- If a question is unrelated to your documents: Respond with: "I can only answer questions related to the documents I have access to. Please ask me about the content of the provided documents."
- If you're unsure: Respond with: "I can only answer questions related to the documents I have access to. Please ask me about the content of the provided documents."

DOCUMENT CONTEXT:
{context}

BEHAVIOR GUIDELINES:
- Be professional and helpful within your strict scope
- Always cite specific document content when answering
- If information is not in the documents, clearly state this
- Maintain Tech Mahindra's professional tone
- Keep responses concise and relevant
- Never provide information outside the scope of your documents

VALIDATION CHECK:
Before responding, ask yourself: "Is this question directly related to the content of my provided documents?"
- If YES: Answer based on document content
- If NO: Decline to answer and redirect to document-related questions

EXAMPLES OF REJECTED QUESTIONS:
- "What's the weather today?"
- "How do I cook pasta?"
- "What's 2+2?"
- "Tell me a joke"
- "What are the latest news?"
- "What's the capital of France?"
- "How do I solve a math problem?"

EXAMPLES OF ACCEPTED QUESTIONS:
- "What is ICDSA according to the documents?"
- "What are the key features mentioned in the telecom documents?"
- "Can you explain the process described in the uploaded files?"
- "What services does Tech Mahindra provide based on the documents?"

REMEMBER: You are a document-specific assistant. Your knowledge is limited to the provided documents only. You must NEVER answer questions outside your document scope, regardless of how simple or common the question might be."""
            
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
            
            response_content = response.choices[0].message.content
            
            # Save chat history
            self.chat_history_manager.save_chat_history(user_id, message, response_content)
            
            return response_content
            
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            # Save error to chat history
            self.chat_history_manager.save_chat_history(user_id, message, error_msg)
            return error_msg
    
    def clear_chat_history(self):
        """Clear the chat history"""
        if 'chat_history' in st.session_state:
            st.session_state.chat_history = []
        st.rerun()
    
    def export_chat_history(self) -> str:
        """Export chat history as text"""
        if not st.session_state.chat_history:
            return "No chat history to export."
        
        export_text = "Chat History Export\n"
        export_text += "=" * 50 + "\n\n"
        
        for i, (message, response) in enumerate(st.session_state.chat_history, 1):
            export_text += f"Exchange {i}:\n"
            export_text += f"User: {message}\n"
            export_text += f"AI: {response}\n"
            export_text += "-" * 30 + "\n\n"
        
        return export_text
    
    def get_chat_statistics(self) -> dict:
        """Get chat statistics"""
        if not st.session_state.chat_history:
            return {
                'total_exchanges': 0,
                'total_user_messages': 0,
                'total_ai_responses': 0,
                'average_response_length': 0
            }
        
        total_exchanges = len(st.session_state.chat_history)
        total_user_messages = sum(len(message) for message, _ in st.session_state.chat_history)
        total_ai_responses = sum(len(response) for _, response in st.session_state.chat_history)
        average_response_length = total_ai_responses / total_exchanges if total_exchanges > 0 else 0
        
        return {
            'total_exchanges': total_exchanges,
            'total_user_messages': total_user_messages,
            'total_ai_responses': total_ai_responses,
            'average_response_length': average_response_length
        }
    
    def render_chat_controls(self):
        """Render chat control buttons"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ Clear Chat"):
                self.clear_chat_history()
        
        with col2:
            if st.button("📊 Chat Statistics"):
                self.show_chat_statistics()
        
        with col3:
            if st.button("💾 Export Chat"):
                self.export_chat_to_file()
    
    def show_chat_statistics(self):
        """Display chat statistics"""
        stats = self.get_chat_statistics()
        
        st.markdown("### Chat Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Exchanges", stats['total_exchanges'])
        
        with col2:
            st.metric("User Messages", stats['total_user_messages'])
        
        with col3:
            st.metric("AI Responses", stats['total_ai_responses'])
        
        with col4:
            st.metric("Avg Response Length", f"{stats['average_response_length']:.1f}")
    
    def export_chat_to_file(self):
        """Export chat history to a downloadable file"""
        export_text = self.export_chat_history()
        
        st.download_button(
            label="📥 Download Chat History",
            data=export_text,
            file_name=f"chat_history_{st.session_state.current_user[1]}_{st.session_state.current_user[0]}.txt",
            mime="text/plain"
        )
    
    def render_quick_actions(self):
        """Render quick action buttons"""
        st.markdown("### Quick Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Refresh Chat"):
                st.rerun()
        
        with col2:
            if st.button("📋 View Resources"):
                st.info("Check the Resources tab to view your accessible documents.") 
    
    def load_professional_styles(self):
        """Load professional dark theme CSS with modern color combination"""
        professional_css = """
        <style>
        /* Professional Dark Theme CSS - Modern Color Palette */
        
        /* Color Variables */
        :root {
            --primary-bg: #0a0a0f;
            --secondary-bg: #1a1a2e;
            --tertiary-bg: #16213e;
            --accent-bg: #0f3460;
            --primary-text: #ffffff;
            --secondary-text: #b8c5d6;
            --muted-text: #8b9bb4;
            --accent-text: #00d4ff;
            --accent-secondary: #0099cc;
            --border-primary: #2a2a3e;
            --border-secondary: #3a3a4e;
            --success-bg: #1a4d2e;
            --warning-bg: #4d3a1a;
            --error-bg: #4d1a1a;
            --gradient-primary: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            --gradient-accent: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
            --gradient-secondary: linear-gradient(135deg, #2a2a3e 0%, #3a3a4e 100%);
            --shadow-light: rgba(0, 0, 0, 0.2);
            --shadow-medium: rgba(0, 0, 0, 0.4);
            --shadow-heavy: rgba(0, 0, 0, 0.6);
        }
        
        /* Global Styles */
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        body {
            background: var(--primary-bg);
            color: var(--primary-text);
        }
        
        /* Streamlit Overrides */
        .stApp {
            background: var(--primary-bg) !important;
        }
        
        .main .block-container {
            background: var(--primary-bg);
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 8px 32px var(--shadow-heavy);
        }
        
        /* Chat Container Styles */
        .chat-container {
            background: var(--gradient-primary);
            border-radius: 20px;
            padding: 2rem;
            margin: 1rem 0;
            border: 1px solid var(--border-primary);
            box-shadow: 0 8px 32px var(--shadow-medium);
            position: relative;
            overflow: hidden;
        }
        
        .chat-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--gradient-accent);
        }
        
        /* Message Styles */
        .message {
            margin: 1.5rem 0;
            padding: 1.5rem;
            border-radius: 15px;
            position: relative;
            animation: fadeInUp 0.4s ease-out;
            box-shadow: 0 4px 16px var(--shadow-light);
        }
        
        .user-message {
            background: var(--gradient-accent);
            color: white;
            margin-left: 3rem;
            border-bottom-right-radius: 8px;
            position: relative;
        }
        
        .user-message::before {
            content: '👤';
            position: absolute;
            left: -3rem;
            top: 1.5rem;
            font-size: 1.3rem;
        }
        
        .bot-message {
            background: var(--gradient-secondary);
            color: var(--primary-text);
            margin-right: 3rem;
            border-bottom-left-radius: 8px;
            border-left: 4px solid var(--accent-text);
            position: relative;
        }
        
        .bot-message::before {
            content: '🤖';
            position: absolute;
            right: -3rem;
            top: 1.5rem;
            font-size: 1.3rem;
        }
        
        /* Input Styles */
        .stTextInput > div > div > input {
            background: var(--tertiary-bg) !important;
            border: 2px solid var(--border-primary) !important;
            border-radius: 12px !important;
            color: var(--primary-text) !important;
            padding: 1rem 1.5rem !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: var(--accent-text) !important;
            box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1) !important;
            outline: none !important;
        }
        
        /* Button Styles */
        .stButton > button {
            background: var(--gradient-accent) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.75rem 2rem !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 16px var(--shadow-medium) !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 24px var(--shadow-heavy) !important;
        }
        
        /* Expander Styles */
        .streamlit-expanderHeader {
            background: var(--gradient-secondary) !important;
            color: var(--primary-text) !important;
            border: 1px solid var(--border-primary) !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            font-weight: 600 !important;
        }
        
        .streamlit-expanderContent {
            background: var(--tertiary-bg) !important;
            border: 1px solid var(--border-primary) !important;
            border-top: none !important;
            border-radius: 0 0 12px 12px !important;
            padding: 1.5rem !important;
        }
        
        /* Selectbox Styles */
        .stSelectbox > div > div > div {
            background: var(--tertiary-bg) !important;
            border: 2px solid var(--border-primary) !important;
            border-radius: 8px !important;
            color: var(--primary-text) !important;
        }
        
        /* Slider Styles */
        .stSlider > div > div > div > div {
            background: var(--accent-text) !important;
        }
        
        /* Success/Warning/Error Messages */
        .element-container .stAlert {
            border-radius: 12px !important;
            border: none !important;
            padding: 1rem 1.5rem !important;
            margin: 1rem 0 !important;
        }
        
        /* Animations */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes pulse {
            0%, 100% {
                opacity: 1;
            }
            50% {
                opacity: 0.8;
            }
        }
        
        /* Professional Typography */
        h1, h2, h3, h4, h5, h6 {
            font-weight: 600;
            color: var(--primary-text);
            margin-bottom: 1rem;
        }
        
        h1 {
            font-size: 2.5rem;
            background: var(--gradient-accent);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        h2 {
            font-size: 2rem;
            color: var(--accent-text);
        }
        
        h3 {
            font-size: 1.5rem;
            color: var(--secondary-text);
        }
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--secondary-bg);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--border-primary);
            border-radius: 5px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--border-secondary);
        }
        </style>
        """
        st.markdown(professional_css, unsafe_allow_html=True) 