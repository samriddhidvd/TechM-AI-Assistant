"""
Google Drive Service
Handles Google Drive integration for file synchronization
"""

import os
import re
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from io import BytesIO
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import pandas as pd
import PyPDF2
from docx import Document
from database.models import DatabaseManager

# Import ChromaDB service
from services.ai.chroma_service import ChromaService

# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

class GoogleDriveService:
    """Service for Google Drive operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize Google Drive service"""
        self.db_manager = db_manager
        self.resource_manager = db_manager.get_resource_manager()
        
        # Setup paths
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.credentials_file = os.path.join(project_root, 'client_secret_671068610606-0dtubpgrm8d76kmfh19lcsueuruc3bpe.apps.googleusercontent.com.json')
        self.token_file = os.path.join(project_root, 'token.pickle')
        
        # Initialize ChromaDB service
        self.chroma_service = ChromaService()
        
        # Setup logging
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        # Get project root for log file
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        log_file = os.path.join(project_root, 'sync.log')
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def authenticate(self):
        """Authenticate with Google Drive API"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
                self.logger.info("Loaded existing token")
            except Exception as e:
                self.logger.warning(f"Error loading existing token: {e}")
                creds = None
        
        # Refresh or create new token
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    self.logger.info("Refreshing expired token...")
                    creds.refresh(Request())
                    self.logger.info("Token refreshed successfully")
                except Exception as e:
                    self.logger.warning(f"Token refresh failed: {e}")
                    creds = None
            
            # If still no valid creds, create new ones
            if not creds or not creds.valid:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(f"Credentials file not found: {self.credentials_file}")
                
                self.logger.info("Creating new authentication flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
                self.logger.info("New authentication completed")
            
            # Save token
            try:
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
                self.logger.info("Token saved successfully")
            except Exception as e:
                self.logger.error(f"Error saving token: {e}")
        
        self.logger.info("Google Drive authentication successful")
        return creds
    
    def build_service(self):
        """Build and return Google Drive service"""
        creds = self.authenticate()
        from googleapiclient.discovery import build
        return build('drive', 'v3', credentials=creds)
    
    def extract_folder_id(self, folder_url: str) -> str:
        """Extract folder ID from Google Drive URL"""
        match = re.search(r'/folders/([a-zA-Z0-9_-]+)', folder_url)
        if not match:
            raise ValueError(f"Invalid Google Drive folder URL: {folder_url}")
        return match.group(1)
    
    def extract_file_id(self, file_url: str) -> str:
        """Extract file ID from Google Drive URL"""
        match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', file_url)
        if not match:
            raise ValueError(f"Invalid Google Drive file URL: {file_url}")
        return match.group(1)
    
    def guess_file_type(self, name: str, mime_type: str) -> Optional[str]:
        """Determine file type from name and MIME type"""
        name_lower = name.lower()
        
        if mime_type == 'application/pdf' or name_lower.endswith('.pdf'):
            return 'pdf'
        elif (mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' 
              or name_lower.endswith('.docx')):
            return 'docx'
        elif (mime_type == 'application/vnd.openxmlformats-officedocument.presentationml.presentation' 
              or name_lower.endswith('.pptx')):
            return 'pptx'
        elif mime_type == 'text/plain' or name_lower.endswith('.txt'):
            return 'txt'
        elif (mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
              or name_lower.endswith('.xlsx')):
            return 'xlsx'
        elif mime_type == 'text/csv' or name_lower.endswith('.csv'):
            return 'csv'
        elif (mime_type == 'application/vnd.google-apps.document' 
              or mime_type == 'application/vnd.google-apps.spreadsheet'
              or mime_type == 'application/vnd.google-apps.presentation'):
            # Handle Google Docs/Sheets/Slides
            if 'document' in mime_type:
                return 'docx'
            elif 'spreadsheet' in mime_type:
                return 'xlsx'
            elif 'presentation' in mime_type:
                return 'pptx'
        
        return None
    
    def extract_text_from_bytes(self, file_bytes: BytesIO, file_type: str) -> str:
        """Extract text from file bytes based on type"""
        try:
            file_bytes.seek(0)  # Reset to beginning
            
            if file_type == 'pdf':
                return self._extract_pdf_text(file_bytes)
            elif file_type == 'docx':
                return self._extract_docx_text(file_bytes)
            elif file_type == 'txt':
                return self._extract_txt_text(file_bytes)
            elif file_type == 'xlsx':
                return self._extract_xlsx_text(file_bytes)
            elif file_type == 'csv':
                return self._extract_csv_text(file_bytes)
            else:
                return f"[Unsupported file type: {file_type}]"
        
        except Exception as e:
            self.logger.error(f"Error extracting text from {file_type} file: {str(e)}")
            return f"[ERROR extracting text: {str(e)}]"
    
    def _extract_pdf_text(self, file_bytes: BytesIO) -> str:
        """Extract text from PDF"""
        try:
            file_bytes.seek(0)  # Reset to beginning
            pdf_reader = PyPDF2.PdfReader(file_bytes)
            text_parts = []
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text_parts.append(page_text.strip())
                except Exception as e:
                    self.logger.warning(f"Error extracting text from PDF page {page_num}: {str(e)}")
                    text_parts.append(f"[Error on page {page_num + 1}]")
            
            extracted_text = "\n".join(text_parts)
            
            if extracted_text and len(extracted_text.strip()) > 0:
                self.logger.info(f"Successfully extracted {len(extracted_text)} characters from PDF")
                return extracted_text
            else:
                self.logger.warning("No text extracted from PDF - may be image-based or encrypted")
                return "[No text extracted from PDF - file may be image-based or encrypted]"
        
        except Exception as e:
            self.logger.error(f"PDF extraction failed: {str(e)}")
            return f"[PDF extraction error: {str(e)}]"
    
    def _extract_docx_text(self, file_bytes: BytesIO) -> str:
        """Extract text from DOCX"""
        try:
            doc = Document(file_bytes)
            text_parts = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
            
            return "\n".join(text_parts) if text_parts else "[No text extracted from DOCX]"
        
        except Exception as e:
            self.logger.error(f"DOCX extraction failed: {str(e)}")
            return f"[DOCX extraction error: {str(e)}]"
    
    def _extract_txt_text(self, file_bytes: BytesIO) -> str:
        """Extract text from TXT"""
        try:
            content = file_bytes.read().decode('utf-8', errors='ignore')
            return content if content.strip() else "[Empty text file]"
        except Exception as e:
            self.logger.error(f"TXT extraction failed: {str(e)}")
            return f"[TXT extraction error: {str(e)}]"
    
    def _extract_xlsx_text(self, file_bytes: BytesIO) -> str:
        """Extract text from XLSX"""
        try:
            df = pd.read_excel(file_bytes, engine='openpyxl')
            return df.to_string() if not df.empty else "[Empty Excel file]"
        except Exception as e:
            self.logger.error(f"XLSX extraction failed: {str(e)}")
            return f"[XLSX extraction error: {str(e)}]"
    
    def _extract_csv_text(self, file_bytes: BytesIO) -> str:
        """Extract text from CSV"""
        try:
            df = pd.read_csv(file_bytes)
            return df.to_string() if not df.empty else "[Empty CSV file]"
        except Exception as e:
            self.logger.error(f"CSV extraction failed: {str(e)}")
            return f"[CSV extraction error: {str(e)}]"
    
    def download_file_from_drive(self, service, file_id: str, timeout: int = 30) -> Tuple[BytesIO, str, int]:
        """Download file from Google Drive with timeout"""
        try:
            self.logger.info(f"Downloading file ID: {file_id}")
            
            # Get file metadata first
            file_metadata = service.files().get(fileId=file_id).execute()
            file_name = file_metadata.get('name', 'Unknown')
            file_size = int(file_metadata.get('size', 0))
            
            self.logger.info(f"File: {file_name}, Size: {file_size} bytes")
            
            # Download file
            fh = BytesIO()
            request = service.files().get_media(fileId=file_id)
            downloader = MediaIoBaseDownload(fh, request)
            
            start_time = time.time()
            done = False
            
            while not done:
                if time.time() - start_time > timeout:
                    raise TimeoutError(f"Download timeout after {timeout} seconds")
                
                status, done = downloader.next_chunk()
                if status:
                    self.logger.info(f"Download progress: {int(status.progress() * 100)}%")
            
            fh.seek(0)
            downloaded_size = len(fh.getvalue())
            self.logger.info(f"Download completed: {downloaded_size} bytes")
            
            return fh, file_name, file_size
        
        except Exception as e:
            self.logger.error(f"Download failed for file {file_id}: {str(e)}")
            raise
    
    def fetch_file_in_memory(self, file_id: str) -> BytesIO:
        """Fetch file from Google Drive and return as BytesIO object"""
        try:
            self.logger.info(f"Fetching file in-memory from Drive: {file_id}")
            
            # Authenticate
            creds = self.authenticate()
            service = build('drive', 'v3', credentials=creds)
            
            # Download file to memory
            fh = BytesIO()
            request = service.files().get_media(fileId=file_id)
            downloader = MediaIoBaseDownload(fh, request)
            
            try:
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    self.logger.info(f"Download progress: {status.progress() if status else 'unknown'}")
                fh.seek(0)
                self.logger.info(f"Finished in-memory download for file: {file_id}, size: {len(fh.getvalue())}")
                return fh
            except Exception as e:
                self.logger.error(f"Error during download: {str(e)}")
                raise
                
        except Exception as e:
            self.logger.error(f"Failed to fetch file {file_id}: {str(e)}")
            raise
    
    def sync_folder(self, folder_url: str, folder_name: str, uploaded_by: str = 'system') -> bool:
        """Main folder sync function"""
        try:
            self.logger.info(f"Starting sync for folder: {folder_name}")
            self.logger.info(f"Folder URL: {folder_url}")
            
            # Extract folder ID
            folder_id = self.extract_folder_id(folder_url)
            self.logger.info(f"Folder ID: {folder_id}")
            
            # Authenticate with better error handling
            try:
                creds = self.authenticate()
                service = build('drive', 'v3', credentials=creds)
                self.logger.info("Google Drive service built successfully")
            except Exception as auth_error:
                self.logger.error(f"Authentication failed: {str(auth_error)}")
                # If token is invalid, try to remove it and re-authenticate
                if "invalid_grant" in str(auth_error) or "expired" in str(auth_error):
                    self.logger.info("Removing invalid token and re-authenticating...")
                    if os.path.exists(self.token_file):
                        os.remove(self.token_file)
                    creds = self.authenticate()
                    service = build('drive', 'v3', credentials=creds)
                else:
                    raise auth_error
            
            # Get folder contents
            try:
                query = f"'{folder_id}' in parents and trashed = false"
                results = service.files().list(
                    q=query, 
                    fields="files(id, name, mimeType, size, modifiedTime)"
                ).execute()
                
                files = results.get('files', [])
                self.logger.info(f"Found {len(files)} files in folder")
            except Exception as list_error:
                self.logger.error(f"Error listing folder contents: {str(list_error)}")
                return False
            
            if not files:
                self.logger.warning("No files found in folder")
                return False
            
            # Process each file
            processed_count = 0
            error_count = 0
            
            for i, file in enumerate(files, 1):
                try:
                    file_id = file['id']
                    file_name = file['name']
                    mime_type = file['mimeType']
                    file_size = int(file.get('size', 0))
                    
                    self.logger.info(f"Processing file {i}/{len(files)}: {file_name}")
                    
                    # Determine file type
                    file_type = self.guess_file_type(file_name, mime_type)
                    if not file_type:
                        self.logger.warning(f"Skipping unsupported file: {file_name} ({mime_type})")
                        continue
                    
                    # Create file URL
                    file_url = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
                    
                    # Download file
                    file_bytes, downloaded_name, original_size = self.download_file_from_drive(
                        service, file_id, timeout=60
                    )
                    
                    # Extract text
                    self.logger.info(f"Extracting text from {file_name}")
                    extracted_text = self.extract_text_from_bytes(file_bytes, file_type)
                    
                    if not extracted_text or extracted_text.strip() == "":
                        extracted_text = f"[No text content found in {file_name}]"
                    
                    self.logger.info(f"Extracted {len(extracted_text)} characters from {file_name}")
                    
                    # Save to database with extracted text
                    max_retries = 3
                    success = False
                    
                    for attempt in range(max_retries):
                        try:
                            success = self.resource_manager.add_resource(
                                file_name, file_url, file_type, uploaded_by, extracted_text
                            )
                            if success:
                                break
                            else:
                                self.logger.warning(f"Database save attempt {attempt + 1} failed for {file_name}")
                                if attempt < max_retries - 1:
                                    import time
                                    time.sleep(1)  # Wait 1 second before retry
                        except Exception as db_error:
                            self.logger.error(f"Database error on attempt {attempt + 1} for {file_name}: {str(db_error)}")
                            if attempt < max_retries - 1:
                                import time
                                time.sleep(1)  # Wait 1 second before retry
                    
                    if success:
                        processed_count += 1
                        self.logger.info(f"✓ Successfully processed: {file_name}")
                        
                        # Store in ChromaDB for vector search
                        try:
                            chroma_success = self.chroma_service.upsert_document(
                                file_name, file_url, extracted_text
                            )
                            if chroma_success:
                                self.logger.info(f"✓ Stored in ChromaDB: {file_name}")
                            else:
                                self.logger.warning(f"⚠ Failed to store in ChromaDB: {file_name}")
                        except Exception as chroma_error:
                            self.logger.error(f"✗ ChromaDB error for {file_name}: {str(chroma_error)}")
                    else:
                        error_count += 1
                        self.logger.error(f"✗ Failed to save after {max_retries} attempts: {file_name}")
                    
                    # Close file bytes
                    file_bytes.close()
                    
                except Exception as e:
                    error_count += 1
                    self.logger.error(f"✗ Error processing file {file_name}: {str(e)}")
                    
                    # Save error entry to database
                    try:
                        file_url = f"https://drive.google.com/file/d/{file['id']}/view?usp=sharing"
                        error_text = f"[ERROR processing {file_name}: {str(e)}]"
                        self.resource_manager.add_resource(
                            file_name, file_url, 'unknown', uploaded_by
                        )
                    except Exception as db_error:
                        self.logger.error(f"Failed to save error entry: {str(db_error)}")
                    
                    continue
            
            self.logger.info(f"Sync completed: {processed_count} successful, {error_count} errors")
            return processed_count > 0
        
        except Exception as e:
            self.logger.error(f"Folder sync failed: {str(e)}")
            return False
    
    def sync_single_file(self, file_url: str, uploaded_by: str = 'system') -> bool:
        """Sync a single Google Drive file"""
        try:
            self.logger.info(f"Starting single file sync: {file_url}")
            
            # Extract file ID
            file_id = self.extract_file_id(file_url)
            self.logger.info(f"File ID: {file_id}")
            
            # Authenticate
            creds = self.authenticate()
            service = build('drive', 'v3', credentials=creds)
            
            # Get file metadata
            file_metadata = service.files().get(fileId=file_id).execute()
            file_name = file_metadata.get('name', 'Unknown')
            mime_type = file_metadata.get('mimeType', '')
            
            # Determine file type
            file_type = self.guess_file_type(file_name, mime_type)
            if not file_type:
                self.logger.warning(f"Unsupported file type: {file_name} ({mime_type})")
                return False
            
            # Download file
            file_bytes, downloaded_name, file_size = self.download_file_from_drive(
                service, file_id, timeout=60
            )
            
            # Extract text
            self.logger.info(f"Extracting text from {file_name}")
            extracted_text = self.extract_text_from_bytes(file_bytes, file_type)
            
            if not extracted_text or extracted_text.strip() == "":
                extracted_text = f"[No text content found in {file_name}]"
            
            self.logger.info(f"Extracted {len(extracted_text)} characters from {file_name}")
            
            # Save to database with extracted text
            success = self.resource_manager.add_resource(
                file_name, file_url, file_type, uploaded_by, extracted_text
            )
            
            # Close file bytes
            file_bytes.close()
            
            if success:
                self.logger.info(f"✓ Successfully processed: {file_name}")
                
                # Store in ChromaDB for vector search
                try:
                    chroma_success = self.chroma_service.upsert_document(
                        file_name, file_url, extracted_text
                    )
                    if chroma_success:
                        self.logger.info(f"✓ Stored in ChromaDB: {file_name}")
                    else:
                        self.logger.warning(f"⚠ Failed to store in ChromaDB: {file_name}")
                except Exception as chroma_error:
                    self.logger.error(f"✗ ChromaDB error for {file_name}: {str(chroma_error)}")
                
                return True
            else:
                self.logger.error(f"✗ Failed to save: {file_name}")
                return False
        
        except Exception as e:
            self.logger.error(f"Single file sync failed: {str(e)}")
            return False
    
    def is_gdrive_folder(self, url: str) -> bool:
        """Check if URL is a Google Drive folder"""
        return bool(re.search(r'/folders/([a-zA-Z0-9_-]+)', url))
    
    def is_gdrive_file(self, url: str) -> bool:
        """Check if URL is a Google Drive file"""
        return bool(re.search(r'/file/d/([a-zA-Z0-9_-]+)', url))
    
    def get_folder_files(self, folder_url: str) -> List[Dict[str, Any]]:
        """Get list of files in a Google Drive folder"""
        try:
            folder_id = self.extract_folder_id(folder_url)
            creds = self.authenticate()
            service = build('drive', 'v3', credentials=creds)
            
            query = f"'{folder_id}' in parents and trashed = false"
            results = service.files().list(
                q=query, 
                fields="files(id, name, mimeType, size, modifiedTime)"
            ).execute()
            
            return results.get('files', [])
        
        except Exception as e:
            self.logger.error(f"Error getting folder files: {str(e)}")
            return []
    
    def get_sync_status(self) -> List[str]:
        """Get the status of the last sync from log file"""
        try:
            if os.path.exists('sync.log'):
                with open('sync.log', 'r') as f:
                    lines = f.readlines()
                    if lines:
                        return lines[-10:]  # Last 10 lines
            return ["No sync log found"]
        except Exception as e:
            return [f"Error reading sync log: {str(e)}"]

class GoogleDriveIntegration:
    """Integration layer for Streamlit app"""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize Google Drive integration"""
        self.gdrive_service = GoogleDriveService(db_manager)
    
    def sync_folder_from_streamlit(self, folder_url: str, folder_name: str, uploaded_by: str = 'admin') -> Tuple[bool, str, str]:
        """
        Simple function to sync a folder from Streamlit
        Returns: (success, message, details)
        """
        try:
            # Ensure the user exists in database
            conn = self.gdrive_service.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (uploaded_by,))
            user_exists = cursor.fetchone()
            conn.close()
            
            if not user_exists:
                # Create the user if it doesn't exist
                from database.models import UserManager
                user_manager = UserManager(self.gdrive_service.db_manager)
                if user_manager.create_user(uploaded_by, "temp_password", "admin"):
                    print(f"Created user: {uploaded_by}")
                else:
                    print(f"User {uploaded_by} already exists")
            
            # Start sync
            success = self.gdrive_service.sync_folder(folder_url, folder_name, uploaded_by)
            
            if success:
                return True, "Folder synced successfully!", "Check sync.log for details"
            else:
                return False, "Sync failed", "Check sync.log for error details"
        
        except Exception as e:
            error_msg = f"Sync error: {str(e)}"
            return False, error_msg, "Check sync.log for full error details"
    
    def sync_single_file_from_streamlit(self, file_url: str, uploaded_by: str = 'admin') -> Tuple[bool, str, str]:
        """
        Sync a single file from Streamlit
        Returns: (success, message, details)
        """
        try:
            success = self.gdrive_service.sync_single_file(file_url, uploaded_by)
            
            if success:
                return True, "File synced successfully!", "Check sync.log for details"
            else:
                return False, "File sync failed", "Check sync.log for error details"
        
        except Exception as e:
            error_msg = f"File sync error: {str(e)}"
            return False, error_msg, "Check sync.log for full error details"
    
    def get_sync_status(self) -> List[str]:
        """Get the status of the last sync from log file"""
        return self.gdrive_service.get_sync_status()
    
    def is_gdrive_folder(self, url: str) -> bool:
        """Check if URL is a Google Drive folder"""
        return self.gdrive_service.is_gdrive_folder(url)
    
    def is_gdrive_file(self, url: str) -> bool:
        """Check if URL is a Google Drive file"""
        return self.gdrive_service.is_gdrive_file(url) 