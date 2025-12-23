# Tech Mahindra AI Assistant

A comprehensive enterprise AI assistant platform that combines document management, intelligent text extraction, and context-aware AI responses.

## Features

- **Multi-Agent AI System**: Specialized agents for technical support, sales, and customer service
- **Document Management**: Automated processing of PDF, DOCX, and TXT files
- **Google Drive Integration**: Seamless cloud document synchronization
- **Role-Based Access Control**: Secure user authentication and permissions
- **Real-Time Chat Interface**: AI-powered conversations with document context
- **Professional UI**: Modern, responsive web interface

## Tech Stack

- **Backend**: Python, Streamlit
- **AI/ML**: Groq API (Llama 3), ChromaDB
- **Database**: SQLite
- **Cloud**: Google Drive API
- **Authentication**: Custom user management system

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Telecom_Professional
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Run the application:
```bash
streamlit run app/main.py
```

## Project Structure

```
Telecom_Professional/
├── app/                    # Main application modules
│   ├── auth/              # Authentication system
│   ├── chat/              # Chat interface
│   ├── dashboard/         # Admin dashboard
│   └── file_management/   # File processing
├── config/                # Configuration files
├── database/              # Database models and operations
├── services/              # External service integrations
│   ├── ai/               # AI/ML services
│   ├── google_drive/     # Google Drive integration
│   └── file_processing/  # File processing services
├── utils/                 # Utility functions
├── static/                # Static assets
└── tests/                 # Test files
```

## Usage

1. **Login**: Use default admin credentials (admin/admin123) or create new account
2. **Upload Documents**: Add PDF, DOCX, or TXT files via URL or Google Drive
3. **Chat with AI**: Ask questions about your uploaded documents
4. **Admin Features**: Manage users, permissions, and system settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is developed for Tech Mahindra as an internal tool.

## Developer

Developed by Samriddhi 
