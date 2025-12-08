"""
AI Chatbot Service
Handles AI interactions and response generation using Groq API
"""

import os
import groq
from typing import Optional, List, Tuple
from config.settings import Config

class ChatbotService:
    """Manages AI chatbot interactions and response generation"""
    
    def __init__(self):
        """Initialize the chatbot service with Groq client and ChromaDB"""
        self.groq_client = groq.Groq(api_key=Config.GROQ_API_KEY)
        self.model = Config.GROQ_MODEL
        self.max_tokens = Config.GROQ_MAX_TOKENS
        self.temperature = Config.GROQ_TEMPERATURE
        
        # Initialize ChromaDB service for document search
        from services.ai.chroma_service import ChromaService
        self.chroma_service = ChromaService()
    
    def generate_response(self, message: str, context: str, user_role: str = "user") -> str:
        """
        Generate AI response based on user message and document context
        
        Args:
            message: User's question or message
            context: Document context for the AI to reference
            user_role: User's role (admin/user) for personalized responses
            
        Returns:
            AI-generated response string
        """
        try:
            # Create system prompt with context and restrictions
            system_prompt = self._create_system_prompt(context, user_role)
            
            # Generate response using Groq API
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            error_msg = str(e)
            if "rate_limit_exceeded" in error_msg or "Request too large" in error_msg:
                return "The request was too large. Please try asking a more specific question about a single document, or contact your administrator to optimize the document processing."
            else:
                return f"Sorry, I encountered an error while processing your request: {error_msg}"
    
    def _create_system_prompt(self, context: str, user_role: str) -> str:
        """
        Create a system prompt with context and role-based instructions
        
        Args:
            context: Document context for AI reference
            user_role: User's role for personalized responses
            
        Returns:
            Formatted system prompt string
        """
        base_prompt = f"""You are a Tech Mahindra AI assistant. Answer questions based on these documents:

{context}

Rules: Only answer questions about the documents above. If unrelated, say: 'I can only answer questions about the provided documents.' Be concise and professional.

User: {user_role.title()}"""

        return base_prompt
    
    def is_document_related_question(self, message: str, context: str) -> bool:
        """
        Check if a question is related to the available documents
        
        Args:
            message: User's question
            context: Available document context
            
        Returns:
            True if question is document-related, False otherwise
        """
        # Simple heuristic: if context is empty or error, question is not document-related
        if not context or context.strip() == "No documents available for reference.":
            return False
        
        # Check for common non-document questions
        non_document_keywords = [
            "weather", "cook", "recipe", "movie", "music", "sports",
            "general knowledge", "trivia", "personal", "private"
        ]
        
        message_lower = message.lower()
        for keyword in non_document_keywords:
            if keyword in message_lower:
                return False
        
        return True
    
    def create_context_from_resources(self, resources: List[Tuple]) -> str:
        """
        Create context string from user's accessible resources
        
        Args:
            resources: List of (name, extracted_text) tuples
            
        Returns:
            Formatted context string
        """
        if not resources:
            return "No documents available for reference."
        
        context_parts = []
        total_length = 0
        max_total_length = Config.MAX_CONTEXT_LENGTH
        
        # Limit to only the first 2 documents to prevent token overflow
        limited_resources = resources[:2]
        
        for name, text in limited_resources:
            if text and len(text.strip()) > 0:
                # Calculate available space for this document
                remaining_length = max_total_length - total_length
                if remaining_length <= 0:
                    break
                
                # Limit text length to prevent token overflow
                limited_text = text[:min(Config.TEXT_EXTRACTION_LIMIT, remaining_length - 100)]  # Reserve 100 chars for formatting
                context_parts.append(f"Document: {name}\nContent: {limited_text}...")
                total_length += len(limited_text) + len(name) + 50  # Approximate formatting overhead
        
        return "\n\n".join(context_parts)
    
    def get_context_from_chroma(self, question: str, n_results: int = 5) -> str:
        """
        Get relevant context from ChromaDB based on user question
        
        Args:
            question: User's question
            n_results: Number of relevant documents to retrieve
            
        Returns:
            Relevant context from ChromaDB
        """
        try:
            return self.chroma_service.get_relevant_context(question, n_results)
        except Exception as e:
            print(f"Error getting context from ChromaDB: {e}")
            return "Error retrieving relevant context from documents."
    
    def validate_response(self, response: str) -> bool:
        """
        Validate if AI response is appropriate and helpful
        
        Args:
            response: AI-generated response
            
        Returns:
            True if response is valid, False otherwise
        """
        # Check for error indicators
        error_indicators = [
            "I cannot", "I don't have", "I'm unable", "I don't know",
            "I'm not sure", "I cannot provide", "I don't have access"
        ]
        
        response_lower = response.lower()
        for indicator in error_indicators:
            if indicator in response_lower:
                return False
        
        # Check for appropriate length
        if len(response.strip()) < 10:
            return False
        
        return True
    
    def get_response_with_fallback(self, message: str, context: str, user_role: str) -> str:
        """
        Get AI response with fallback handling
        
        Args:
            message: User's question
            context: Document context
            user_role: User's role
            
        Returns:
            AI response or fallback message
        """
        # Check if question is document-related
        if not self.is_document_related_question(message, context):
            return "I can only answer questions related to the documents I have access to. Please ask me about the content of the provided documents."
        
        # Generate AI response
        response = self.generate_response(message, context, user_role)
        
        # Validate response
        if not self.validate_response(response):
            return "I'm having trouble processing your question. Please try rephrasing or ask about the documents I have access to."
        
        return response

class MultiAgentSystem:
    """Simplified multi-agent system for specialized responses"""
    
    def __init__(self, chatbot_service: ChatbotService):
        self.chatbot_service = chatbot_service
    
    def route_message(self, message: str) -> str:
        """
        Route message to appropriate specialized agent
        
        Args:
            message: User's message
            
        Returns:
            Agent type string
        """
        message_lower = message.lower()
        
        # Technical support keywords
        technical_keywords = [
            "network", "connection", "internet", "wifi", "router", "modem",
            "speed", "slow", "down", "error", "troubleshoot", "technical",
            "device", "configuration", "settings", "password", "reset"
        ]
        
        # Sales keywords
        sales_keywords = [
            "plan", "package", "price", "cost", "upgrade", "new service",
            "product", "offer", "deal", "promotion", "compare", "recommend",
            "features", "benefits", "contract", "installation"
        ]
        
        # Billing keywords
        billing_keywords = [
            "bill", "payment", "invoice", "charge", "fee", "cost",
            "billing", "account", "statement", "due", "overdue"
        ]
        
        # Check for specialized keywords
        for keyword in technical_keywords:
            if keyword in message_lower:
                return "technical_support"
        
        for keyword in sales_keywords:
            if keyword in message_lower:
                return "sales"
        
        for keyword in billing_keywords:
            if keyword in message_lower:
                return "billing"
        
        # Default to customer service
        return "customer_service"
    
    def get_specialized_response(self, message: str, context: str, user_role: str) -> str:
        """
        Get response from specialized agent based on message content
        
        Args:
            message: User's message
            context: Document context
            user_role: User's role
            
        Returns:
            Specialized AI response
        """
        agent_type = self.route_message(message)
        
        # Add agent-specific context to system prompt
        agent_context = f"Agent Type: {agent_type.replace('_', ' ').title()}\n"
        enhanced_context = agent_context + context
        
        return self.chatbot_service.get_response_with_fallback(message, enhanced_context, user_role) 