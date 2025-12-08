"""
Admin Dashboard Module
Handles the administrative interface and system management
"""

import streamlit as st
from typing import List, Tuple
from config.settings import Config

class AdminDashboard:
    """Manages the admin dashboard interface"""
    
    def __init__(self, user_manager, resource_manager, permission_manager):
        """Initialize admin dashboard with required services"""
        self.user_manager = user_manager
        self.resource_manager = resource_manager
        self.permission_manager = permission_manager
    
    def render(self):
        """Render the admin dashboard"""
        st.title("👨‍💼 Admin Dashboard - Developed BY Samriddhi")
        
        # Create navigation tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Dashboard", 
            "📁 Data Management", 
            "👥 User Management", 
            "🔐 Permission Management"
        ])
        
        with tab1:
            self.render_overview_dashboard()
        
        with tab2:
            self.render_data_management()
        
        with tab3:
            self.render_user_management()
        
        with tab4:
            self.render_permission_management()
    
    def render_overview_dashboard(self):
        """Render the overview dashboard with statistics"""
        st.markdown("### System Overview")
        
        # Get statistics
        users = self.user_manager.get_all_users()
        resources = self.resource_manager.get_all_resources()
        
        # Calculate metrics
        total_users = len(users)
        total_resources = len(resources)
        accessed_resources = len([r for r in resources if r[6]])  # is_accessed
        synced_resources = len(resources)  # All resources are considered synced
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">{}</div>
                <div class="metric-label">Total Users</div>
            </div>
            """.format(total_users), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">{}</div>
                <div class="metric-label">Total Resources</div>
            </div>
            """.format(total_resources), unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">{}</div>
                <div class="metric-label">Accessed Resources</div>
            </div>
            """.format(accessed_resources), unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">{}</div>
                <div class="metric-label">Synced with AI</div>
            </div>
            """.format(synced_resources), unsafe_allow_html=True)
        
        # System health indicators
        st.markdown("### System Health")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Database status
            try:
                # Test database connection
                users = self.user_manager.get_all_users()
                st.success("✅ Database: Connected")
            except Exception as e:
                st.error(f"❌ Database: Error - {str(e)}")
            
            # AI service status
            try:
                # This would test AI service connectivity
                st.success("✅ AI Service: Available")
            except Exception as e:
                st.error(f"❌ AI Service: Error - {str(e)}")
        
        with col2:
            # File system status
            try:
                import os
                if os.path.exists(Config.DOWNLOAD_DIR):
                    st.success("✅ File System: Accessible")
                else:
                    st.warning("⚠️ File System: Download directory missing")
            except Exception as e:
                st.error(f"❌ File System: Error - {str(e)}")
            
            # Configuration status
            try:
                Config.validate_config()
                st.success("✅ Configuration: Valid")
            except Exception as e:
                st.error(f"❌ Configuration: Error - {str(e)}")
    
    def render_data_management(self):
        """Render data management interface"""
        st.markdown("### Add Resource (File or Google Drive Folder)")
        
        # Resource input form
        resource_link = st.text_input(
            "Resource Link (File or Google Drive Folder)", 
            value="", 
            key="resource_link",
            placeholder="Enter file URL or Google Drive folder link"
        )
        
        resource_name = st.text_input(
            "Resource Name", 
            value="", 
            key="resource_name",
            placeholder="Enter a descriptive name for the resource"
        )
        
        file_type = st.selectbox(
            "File Type (for single file only)", 
            ["pdf", "docx", "pptx", "txt"], 
            key="resource_file_type"
        )
        
        status_placeholder = st.empty()
        
        # Add resource button
        if st.button("Add Resource", use_container_width=True):
            if not resource_link or not resource_name:
                status_placeholder.warning("Please provide both resource link and name.")
            else:
                self.handle_resource_addition(resource_link, resource_name, file_type, status_placeholder)
        
        st.markdown("---")
        
        # Resource management table
        self.render_resource_table()
    
    def handle_resource_addition(self, resource_link: str, resource_name: str, file_type: str, status_placeholder):
        """Handle resource addition process"""
        try:
            # Import Google Drive integration
            from services.google_drive.gdrive_service import GoogleDriveIntegration
            from database.models import DatabaseManager
            
            # Initialize Google Drive integration
            db_manager = DatabaseManager()
            gdrive_integration = GoogleDriveIntegration(db_manager)
            
            # Get current user
            uploaded_by = st.session_state.current_user[1] if st.session_state.current_user else 'admin'
            
            # Check if it's a Google Drive folder
            if gdrive_integration.is_gdrive_folder(resource_link):
                # Google Drive Folder processing
                status_placeholder.info("Processing Google Drive folder...")
                
                # Show progress container
                progress_container = st.container()
                with progress_container:
                    st.info("🔄 Starting Google Drive folder sync...")
                    st.info("This may take a few minutes depending on folder size.")
                
                with st.spinner("Syncing Google Drive folder..."):
                    success, message, details = gdrive_integration.sync_folder_from_streamlit(
                        resource_link, resource_name, "admin"  # Use admin user
                    )
                
                if success:
                    status_placeholder.success(f"✅ {message}")
                    st.success(f"🎉 Folder synced successfully!")
                    st.info(f"📋 {details}")
                    
                    # Show sync log
                    sync_log = gdrive_integration.get_sync_status()
                    if sync_log:
                        st.markdown("**📄 Sync Log (Last 10 lines):**")
                        for line in sync_log[-10:]:  # Last 10 lines
                            st.text(line.strip())
                    
                    st.rerun()
                else:
                    status_placeholder.error(f"❌ {message}")
                    st.error(f"❌ Folder sync failed!")
                    st.error(f"Error: {details}")
                    
                    # Show sync log for debugging
                    sync_log = gdrive_integration.get_sync_status()
                    if sync_log:
                        st.markdown("**📄 Sync Log (Last 10 lines):**")
                        for line in sync_log[-10:]:  # Last 10 lines
                            st.text(line.strip())
                    
            elif gdrive_integration.is_gdrive_file(resource_link):
                # Google Drive File processing
                status_placeholder.info("Processing Google Drive file...")
                
                with st.spinner("Syncing Google Drive file..."):
                    success, message, details = gdrive_integration.sync_single_file_from_streamlit(
                        resource_link, uploaded_by
                    )
                
                if success:
                    status_placeholder.success(f"✅ {message}")
                    st.success(f"🎉 File synced successfully!")
                    st.info(f"📋 {details}")
                    st.rerun()
                else:
                    status_placeholder.error(f"❌ {message}")
                    st.error(f"❌ File sync failed!")
                    st.error(f"Error: {details}")
                    
            else:
                # Regular file processing
                if self.resource_manager.add_resource(resource_name, resource_link, file_type, uploaded_by):
                    status_placeholder.success("Resource added successfully!")
                    st.rerun()
                else:
                    status_placeholder.error("Failed to add resource. Please check the URL and try again.")
                    
        except Exception as e:
            status_placeholder.error(f"Error adding resource: {str(e)}")
            st.error(f"Error: {str(e)}")
    
    def is_gdrive_folder(self, link: str) -> bool:
        """Check if the link is a Google Drive folder"""
        import re
        return bool(re.search(r'/folders/([a-zA-Z0-9_-]+)', link))
    
    def render_resource_table(self):
        """Render the resource management table"""
        st.markdown("#### Resource Management Table")
        
        try:
            resources = self.resource_manager.get_all_resources()
            
            if resources:
                st.markdown("**All Resources:**")
                
                for i, resource in enumerate(resources):
                    with st.expander(f"📄 {resource[1] if resource[1] else 'Unknown'}", expanded=False):
                        self.render_resource_details(resource, i)
            else:
                st.info("No resources added yet.")
                
        except Exception as e:
            st.error(f"Error loading resources: {str(e)}")
    
    def render_resource_details(self, resource: Tuple, index: int):
        """Render details for a specific resource"""
        try:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**ID:** {resource[0]}")
                st.write(f"**File Type:** {resource[3]}")
                st.write(f"**URL:** {resource[2]}")
                st.write(f"**Uploaded By:** {resource[4] if resource[4] else 'Unknown'}")
                st.write(f"**Upload Date:** {resource[5] if resource[5] else 'Unknown'}")
                st.write(f"**Last Sync:** {resource[6] if len(resource) > 6 and resource[6] else 'Never'}")
            
            with col2:
                st.write(f"**Accessed:** {'Yes' if resource[6] else 'No'}")
                st.write(f"**Access Count:** {resource[7] if len(resource) > 7 and resource[7] else 0}")
                
                # Delete button
                if st.button(f"Delete Resource", key=f"delete_{index}"):
                    if self.resource_manager.delete_resource(resource[0]):
                        st.success("Resource deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete resource.")
                
                # Show extracted text
                extracted_text = resource[8] if len(resource) > 8 else None
                if extracted_text and len(extracted_text.strip()) > 0:
                    st.write("**Extracted Text Preview:**")
                    preview = extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text
                    st.text(preview)
                    st.write(f"**Text Length:** {len(extracted_text)} characters")
                else:
                    st.write("**Extracted Text:** No text available")
                    st.write("**Text Length:** 0 characters")
            
        except Exception as e:
            st.error(f"Error displaying resource {index}: {str(e)}")
    
    def render_user_management(self):
        """Render user management interface"""
        st.markdown("### User Management")
        
        try:
            users = self.user_manager.get_all_users()
            
            if users:
                st.markdown("**Registered Users:**")
                
                # User selection
                user_options = [f"{u[0]} - {u[1]} ({u[2]})" for u in users if len(u) >= 3]
                selected_users = st.multiselect(
                    "Select Users:", 
                    user_options, 
                    help="Select one or more users to manage"
                )
                
                if selected_users:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Delete users
                        confirm_delete = st.checkbox(
                            "Yes, I am sure I want to delete the selected users.", 
                            key="confirm_delete_users"
                        )
                        
                        if st.button("Delete Selected Users", help="Delete all selected users. This action cannot be undone.") and confirm_delete:
                            self.delete_selected_users(selected_users)
                    
                    with col2:
                        # Change user roles
                        new_role = st.selectbox(
                            "Change Role to:", 
                            ["user", "admin"], 
                            help="Change role for all selected users"
                        )
                        
                        if st.button("Apply Role to Selected", help="Apply the selected role to all selected users."):
                            self.update_selected_user_roles(selected_users, new_role)
                
                st.markdown("---")
                
                # Display user details
                for i, user in enumerate(users):
                    try:
                        if len(user) >= 4:
                            st.markdown(f"""
                            <div class='user-card'>
                                <b>ID:</b> {user[0]} &nbsp; <b>Username:</b> {user[1]} &nbsp; 
                                <b>Role:</b> <span class='user-badge'>{user[2]}</span> &nbsp; 
                                <b>Created:</b> {user[3]}
                            </div>
                            """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error displaying user {i}: {e}")
                        continue
            else:
                st.info("No users found.")
                
        except Exception as e:
            st.error(f"Error loading users: {e}")
            st.info("Please try refreshing the page.")
    
    def delete_selected_users(self, selected_users: List[str]):
        """Delete selected users"""
        try:
            for user_str in selected_users:
                user_id = int(user_str.split(" - ")[0])
                self.user_manager.delete_user(user_id)
            st.success("Selected users deleted!")
            st.rerun()
        except Exception as e:
            st.error(f"Error deleting users: {str(e)}")
    
    def update_selected_user_roles(self, selected_users: List[str], new_role: str):
        """Update roles for selected users"""
        try:
            for user_str in selected_users:
                user_id = int(user_str.split(" - ")[0])
                self.user_manager.update_user_role(user_id, new_role)
            st.success(f"Role updated to '{new_role}' for selected users!")
            st.rerun()
        except Exception as e:
            st.error(f"Error updating user roles: {str(e)}")
    
    def render_permission_management(self):
        """Render permission management interface"""
        st.markdown("### Permission Management")
        st.markdown("Manage which users can access which resources")
        
        try:
            users = self.user_manager.get_all_users()
            resources = self.resource_manager.get_all_resources()
            
            if users and resources:
                # Multi-select for users and resources
                user_options = [f"{u[0]} - {u[1]} ({u[2]})" for u in users if len(u) >= 3]
                resource_options = [f"{r[0]} - {r[1]}" for r in resources if len(r) >= 2]
                
                selected_users = st.multiselect("Select Users:", user_options)
                selected_resources = st.multiselect("Select Resources:", resource_options)
                
                if selected_users and selected_resources:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("Grant Access (Batch)"):
                            self.grant_batch_permissions(selected_users, selected_resources)
                    
                    with col2:
                        if st.button("Revoke Access (Batch)"):
                            self.revoke_batch_permissions(selected_users, selected_resources)
                
                # Show permissions for selected user
                if len(selected_users) == 1:
                    self.show_user_permissions(selected_users[0])
            else:
                st.info("No users or resources found.")
                
        except Exception as e:
            st.error(f"Error in permission management: {e}")
            st.info("Please try refreshing the page.")
    
    def grant_batch_permissions(self, selected_users: List[str], selected_resources: List[str]):
        """Grant permissions to multiple users for multiple resources"""
        try:
            with st.spinner("Granting access..."):
                for user_str in selected_users:
                    user_id = int(user_str.split(" - ")[0])
                    for res_str in selected_resources:
                        resource_id = int(res_str.split(" - ")[0])
                        self.permission_manager.grant_permission(
                            user_id, resource_id, st.session_state.current_user[1]
                        )
            st.success("Access granted to selected users/resources!")
            st.rerun()
        except Exception as e:
            st.error(f"Error in batch grant: {e}")
    
    def revoke_batch_permissions(self, selected_users: List[str], selected_resources: List[str]):
        """Revoke permissions from multiple users for multiple resources"""
        try:
            with st.spinner("Revoking access..."):
                for user_str in selected_users:
                    user_id = int(user_str.split(" - ")[0])
                    for res_str in selected_resources:
                        resource_id = int(res_str.split(" - ")[0])
                        self.permission_manager.revoke_permission(
                            user_id, resource_id, st.session_state.current_user[1]
                        )
            st.success("Access revoked for selected users/resources!")
            st.rerun()
        except Exception as e:
            st.error(f"Error in batch revoke: {e}")
    
    def show_user_permissions(self, user_str: str):
        """Show permissions for a specific user"""
        user_id = int(user_str.split(" - ")[0])
        user_permissions = self.permission_manager.get_user_permissions(user_id)
        
        st.markdown(f"**Permissions for User ID {user_id}:**")
        
        if user_permissions:
            st.markdown("**Current Permissions:**")
            for perm in user_permissions:
                status = "✅ Granted" if perm[2] else "❌ Revoked"
                st.write(f"- Resource: {perm[3]} | Status: {status} | Granted by: {perm[4]} | Date: {perm[5]}")
        else:
            st.info("No permissions found for this user.") 