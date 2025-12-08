# Tech Mahindra AI Assistant - Setup Guide

## Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (optional, for version control)

### 2. Installation

1. **Clone or download the project:**
   ```bash
   # If using git
   git clone <repository-url>
   cd Telecom_Professional
   
   # Or simply navigate to the project directory
   cd Telecom_Professional
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   # Copy the example environment file
   cp env_example.txt .env
   
   # Edit the .env file with your API keys
   nano .env  # or use your preferred text editor
   ```

4. **Configure your API keys:**
   ```bash
   # Edit .env file and add your Groq API key
   GROQ_API_KEY=your_actual_groq_api_key_here
   ```

### 3. Running the Application

**Option 1: Using the run script**
```bash
python run.py
```

**Option 2: Using Streamlit directly**
```bash
streamlit run app/main.py
```

**Option 3: Using Python module**
```bash
python -m streamlit run app/main.py
```

### 4. Access the Application

Open your web browser and navigate to:
```
http://localhost:8501
```

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Required: Groq API Key
GROQ_API_KEY=your_groq_api_key_here

# Optional: Google Drive API (for cloud document sync)
GOOGLE_CREDENTIALS_FILE=client_secret_671068610606-0dtubpgrm8d76kmfh19lcsueuruc3bpe.apps.googleusercontent.com.json

# Database settings
DATABASE_PATH=telecom.db

# Application settings
LOG_LEVEL=INFO
DOWNLOAD_DIR=downloads
```

### Getting API Keys

#### Groq API Key
1. Visit [Groq Console](https://console.groq.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key to your `.env` file

#### Google Drive API (Optional)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Drive API
4. Create credentials (OAuth 2.0 Client ID)
5. Download the credentials JSON file
6. Place it in the project root and update `.env`

## Project Structure

```
Telecom_Professional/
├── app/                    # Main application modules
│   ├── auth/              # Authentication system
│   │   └── login.py       # Login/registration logic
│   ├── chat/              # Chat interface
│   │   └── chat_interface.py
│   ├── dashboard/         # Dashboard components
│   │   ├── admin_dashboard.py
│   │   └── user_dashboard.py
│   └── main.py            # Main application entry point
├── config/                # Configuration files
│   └── settings.py        # Application settings
├── database/              # Database models
│   └── models.py          # Database operations
├── services/              # External services
│   └── ai/               # AI services
│       └── chatbot_service.py
├── static/                # Static assets
│   └── css/              # Stylesheets
│       └── styles.css
├── utils/                 # Utility functions
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── SETUP.md              # This setup guide
├── run.py                # Run script
└── .env                  # Environment variables (create this)
```

## Features

### For Users
- **AI Chat Interface**: Ask questions about your documents
- **Document Management**: View accessible documents
- **Chat History**: Export and manage conversation history
- **Quick Actions**: Common queries with one click

### For Administrators
- **User Management**: Create, edit, and delete users
- **Resource Management**: Add and manage documents
- **Permission Management**: Control access to resources
- **System Monitoring**: View system statistics and health

## Troubleshooting

### Common Issues

1. **"Module not found" errors:**
   ```bash
   pip install -r requirements.txt
   ```

2. **"GROQ_API_KEY not found" error:**
   - Make sure you have created a `.env` file
   - Verify your API key is correct
   - Check that the key is properly formatted

3. **Database errors:**
   - The application will create the database automatically
   - Check file permissions in the project directory

4. **Port already in use:**
   ```bash
   # Use a different port
   streamlit run app/main.py --server.port 8502
   ```

### Logs and Debugging

- Check the terminal output for error messages
- Streamlit logs are displayed in the terminal
- Database logs are minimal but errors will be shown

## Development

### Adding New Features

1. **Create new modules** in the appropriate directory
2. **Update imports** in `app/main.py`
3. **Add configuration** in `config/settings.py` if needed
4. **Update requirements.txt** for new dependencies

### Code Style

- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions small and focused

### Testing

```bash
# Run basic tests (if implemented)
python -m pytest tests/

# Manual testing
streamlit run app/main.py
```

## Deployment

### Local Development
```bash
streamlit run app/main.py
```

### Production Deployment
```bash
# Using Streamlit Cloud
streamlit deploy app/main.py

# Using Docker (if Dockerfile is provided)
docker build -t telecom-ai .
docker run -p 8501:8501 telecom-ai
```

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the logs for error messages
3. Ensure all dependencies are installed
4. Verify API keys are correctly configured

## Security Notes

- Never commit your `.env` file to version control
- Keep your API keys secure and private
- Regularly update dependencies for security patches
- Use strong passwords for user accounts

---

**Developed BY Samriddhi**
*Tech Mahindra AI Assistant Platform* 