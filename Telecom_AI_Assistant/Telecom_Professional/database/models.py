"""
Database models and schema definitions
Defines the structure of our SQLite database tables
"""

import sqlite3
import hashlib
from datetime import datetime
from typing import Optional, List, Tuple, Dict, Any

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, db_path: str = "telecom.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection with timeout and better concurrency"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=MEMORY")
        return conn
    
    def init_database(self):
        """Initialize database tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table - stores user accounts and authentication
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Resources table - stores uploaded documents and files
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                file_type TEXT NOT NULL,
                uploaded_by TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_accessed BOOLEAN DEFAULT FALSE,
                access_count INTEGER DEFAULT 0,
                extracted_text TEXT,
                last_sync_time TIMESTAMP
            )
        ''')
        
        # Permissions table - manages user access to resources
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                resource_id INTEGER,
                can_access BOOLEAN DEFAULT TRUE,
                granted_by TEXT NOT NULL,
                granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (resource_id) REFERENCES resources (id)
            )
        ''')
        
        # Chat history table - stores conversation logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create default admin user if it doesn't exist
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            admin_password_hash = self._hash_password("admin123")
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                ("admin", admin_password_hash, "admin")
            )
        
        conn.commit()
        conn.close()
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def get_resource_manager(self) -> 'ResourceManager':
        """Get a ResourceManager instance"""
        return ResourceManager(self)
    
    def get_user_manager(self) -> 'UserManager':
        """Get a UserManager instance"""
        return UserManager(self)
    
    def get_permission_manager(self) -> 'PermissionManager':
        """Get a PermissionManager instance"""
        return PermissionManager(self)
    
    def get_chat_history_manager(self) -> 'ChatHistoryManager':
        """Get a ChatHistoryManager instance"""
        return ChatHistoryManager(self)

class UserManager:
    """Manages user-related database operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_user(self, username: str, password: str, role: str = "user") -> bool:
        """Create a new user account"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            password_hash = self.db_manager._hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, role)
            )
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Username already exists
            return False
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def verify_user(self, username: str, password: str) -> Optional[Tuple]:
        """Verify user credentials and return user data"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            password_hash = self.db_manager._hash_password(password)
            cursor.execute(
                "SELECT * FROM users WHERE username = ? AND password_hash = ?",
                (username, password_hash)
            )
            
            user = cursor.fetchone()
            conn.close()
            return user
        except Exception as e:
            print(f"Error verifying user: {e}")
            return None
    
    def get_all_users(self) -> List[Tuple]:
        """Get all users from database"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role, created_at FROM users")
            users = cursor.fetchall()
            conn.close()
            return users
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    def update_user_role(self, user_id: int, new_role: str) -> bool:
        """Update user role"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating user role: {e}")
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user account"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False

class ResourceManager:
    """Manages resource-related database operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def add_resource(self, name: str, url: str, file_type: str, uploaded_by: str, extracted_text: str = None) -> bool:
        """Add a new resource to the database"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            print(f"Adding resource: {name} (URL: {url[:50]}...)")
            
            # Check if resource already exists
            cursor.execute("SELECT id FROM resources WHERE url = ?", (url,))
            existing_resource = cursor.fetchone()
            
            if existing_resource:
                # Update existing resource
                print(f"Updating existing resource: {name}")
                cursor.execute('''
                    UPDATE resources 
                    SET name = ?, file_type = ?, uploaded_by = ?, last_sync_time = CURRENT_TIMESTAMP,
                        extracted_text = COALESCE(?, extracted_text)
                    WHERE url = ?
                ''', (name, file_type, uploaded_by, extracted_text, url))
            else:
                # Insert new resource
                print(f"Inserting new resource: {name}")
                cursor.execute('''
                    INSERT INTO resources (name, url, file_type, uploaded_by, extracted_text)
                    VALUES (?, ?, ?, ?, ?)
                ''', (name, url, file_type, uploaded_by, extracted_text))
            
            # Get the resource ID for permission assignment
            cursor.execute("SELECT id FROM resources WHERE url = ?", (url,))
            resource_result = cursor.fetchone()
            if not resource_result:
                print(f"Error: Could not find resource after insert/update: {name}")
                conn.rollback()
                conn.close()
                return False
            
            resource_id = resource_result[0]
            print(f"Resource ID: {resource_id}")
            
            # Grant permission to the uploading user
            cursor.execute("SELECT id FROM users WHERE username = ?", (uploaded_by,))
            user_row = cursor.fetchone()
            if user_row:
                user_id = user_row[0]
                print(f"User ID: {user_id}")
                cursor.execute(
                    "INSERT OR REPLACE INTO permissions (user_id, resource_id, can_access, granted_by) VALUES (?, ?, ?, ?)",
                    (user_id, resource_id, True, uploaded_by)
                )
                print(f"Permission granted for user {uploaded_by}")
            else:
                print(f"Warning: User '{uploaded_by}' not found, skipping permission assignment")
            
            conn.commit()
            print(f"Successfully saved resource: {name}")
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding resource '{name}': {str(e)}")
            print(f"Error type: {type(e).__name__}")
            try:
                conn.rollback()
                conn.close()
            except:
                pass
            return False
    
    def get_all_resources(self) -> List[Tuple]:
        """Get all resources from database"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM resources")
            resources = cursor.fetchall()
            conn.close()
            return resources
        except Exception as e:
            print(f"Error getting resources: {e}")
            return []
    
    def get_user_accessible_resources(self, user_id: int) -> List[Tuple]:
        """Get resources accessible to a specific user with extracted text"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # First, get the user's role
            cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
            user_result = cursor.fetchone()
            user_role = user_result[0] if user_result else "user"
            
            # If user is admin, they have access to all resources
            if user_role == "admin":
                cursor.execute("""
                    SELECT * FROM resources 
                    WHERE extracted_text IS NOT NULL 
                    AND extracted_text != ''
                    AND extracted_text NOT LIKE '[ERROR%'
                """)
                resources = cursor.fetchall()
                conn.close()
                return resources
            
            # For regular users, only return resources they have explicit permission to access
            cursor.execute("""
                SELECT r.* FROM resources r
                INNER JOIN permissions p ON r.id = p.resource_id AND p.user_id = ?
                WHERE p.can_access = TRUE
                AND r.extracted_text IS NOT NULL 
                AND r.extracted_text != ''
                AND r.extracted_text NOT LIKE '[ERROR%'
            """, (user_id,))
            resources = cursor.fetchall()
            conn.close()
            return resources
        except Exception as e:
            print(f"Error getting user resources: {e}")
            return []
    
    def delete_resource(self, resource_id: int) -> bool:
        """Delete a resource from database"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM resources WHERE id = ?", (resource_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting resource: {e}")
            return False
    
    def update_resource_access(self, resource_id: int) -> bool:
        """Update resource access statistics"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE resources SET is_accessed = TRUE, access_count = access_count + 1 WHERE id = ?",
                (resource_id,)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating resource access: {e}")
            return False

class PermissionManager:
    """Manages permission-related database operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def grant_permission(self, user_id: int, resource_id: int, granted_by: str) -> bool:
        """Grant access permission to a user for a resource"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO permissions (user_id, resource_id, can_access, granted_by) VALUES (?, ?, ?, ?)",
                (user_id, resource_id, True, granted_by)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error granting permission: {e}")
            return False
    
    def revoke_permission(self, user_id: int, resource_id: int, revoked_by: str) -> bool:
        """Revoke access permission from a user for a resource"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO permissions (user_id, resource_id, can_access, granted_by) VALUES (?, ?, ?, ?)",
                (user_id, resource_id, False, revoked_by)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error revoking permission: {e}")
            return False
    
    def get_user_permissions(self, user_id: int) -> List[Tuple]:
        """Get all permissions for a specific user"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, p.resource_id, p.can_access, r.name, p.granted_by, p.granted_at
                FROM permissions p
                JOIN resources r ON p.resource_id = r.id
                WHERE p.user_id = ?
            """, (user_id,))
            permissions = cursor.fetchall()
            conn.close()
            return permissions
        except Exception as e:
            print(f"Error getting user permissions: {e}")
            return []

class ChatHistoryManager:
    """Manages chat history database operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def save_chat_history(self, user_id: int, message: str, response: str) -> bool:
        """Save a chat interaction to database"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO chat_history (user_id, message, response) VALUES (?, ?, ?)",
                (user_id, message, response)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving chat history: {e}")
            return False
    
    def get_chat_history(self, user_id: int, limit: int = 50) -> List[Tuple]:
        """Get chat history for a specific user"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT message, response FROM chat_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                (user_id, limit)
            )
            history = cursor.fetchall()
            conn.close()
            return history
        except Exception as e:
            print(f"Error getting chat history: {e}")
            return [] 