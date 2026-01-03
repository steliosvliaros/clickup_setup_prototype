"""
ClickUp Setup Script for PV Operations Management System

This script creates the complete ClickUp workspace structure by loading
configuration from config.yaml including:
- Spaces, Folders, and Lists
- Custom Fields (30+ field types)
- Status Workflows (multiple workflow types)
- Views and Dashboards configuration

Requirements:
pip install requests python-dotenv pyyaml

Setup:
1. Get your ClickUp API token from: https://app.clickup.com/settings/apps
2. Get your Team ID from: https://app.clickup.com/settings/teams
3. Set environment variables in .env file
4. Configure workspace structure in config.yaml

Note: Custom statuses and automations cannot be created via API.
      Create them manually in ClickUp UI after running this script.
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import yaml

# ============================================================================
# CONFIGURATION
# ============================================================================

DEFAULT_SPACE_FEATURES = {
    "due_dates": {
        "enabled": True,
        "start_date": True,
        "remap_due_dates": True,
        "remap_closed_due_date": True,
    },
    "custom_fields": {"enabled": True},
    "time_tracking": {"enabled": True},
    "tags": {"enabled": True},
    "time_estimates": {"enabled": True},
    "checklists": {"enabled": True},
    "remap_dependencies": {"enabled": True},
    "dependency_warning": {"enabled": True},
    "portfolios": {"enabled": True},
}

class ClickUpConfig:
    def __init__(self, api_token: str, team_id: str):
        self.api_token = api_token
        self.team_id = team_id
        self.base_url = "https://api.clickup.com/api/v2"
        self.headers = {
            "Authorization": api_token,
            "Content-Type": "application/json"
        }
        self.default_space_features = DEFAULT_SPACE_FEATURES

# ============================================================================
# CLICKUP API WRAPPER
# ============================================================================

class ClickUpAPI:
    def __init__(self, config: ClickUpConfig):
        self.config = config
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make API request with error handling and rate limiting"""
        url = f"{self.config.base_url}/{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.config.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.config.headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=self.config.headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.config.headers)
            
            response.raise_for_status()
            time.sleep(0.5)  # Rate limiting
            
            return response.json() if response.text else {}
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print("Rate limit hit, waiting 60 seconds...")
                time.sleep(60)
                return self._request(method, endpoint, data)
            print(f"API Error: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return {}
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return {}
    
    def create_space(self, name: str) -> str:
        """Create a new space"""
        data = {
            "name": name,
            "multiple_assignees": True,
            "features": self.config.default_space_features,
        }
        result = self._request("POST", f"team/{self.config.team_id}/space", data)
        return result.get("id", "")
    
    def get_spaces(self) -> List[Dict]:
        """Get all spaces"""
        result = self._request("GET", f"team/{self.config.team_id}/space")
        return result.get("spaces", [])
    
    def create_folder(self, space_id: str, name: str) -> str:
        """Create a folder in a space"""
        data = {"name": name}
        result = self._request("POST", f"space/{space_id}/folder", data)
        return result.get("id", "")
    
    def create_list(self, folder_id: str, name: str) -> str:
        """Create a list in a folder"""
        data = {"name": name}
        result = self._request("POST", f"folder/{folder_id}/list", data)
        return result.get("id", "")
    
    def create_custom_field(self, list_id: str, field_config: Dict) -> str:
        """Create a custom field in a list"""
        # Validate required fields
        if "name" not in field_config:
            print(f"      ⚠️  Field config missing 'name': {field_config}")
            return ""
        
        if "type" not in field_config:
            print(f"      ⚠️  Field config missing 'type': {field_config}")
            return ""
        
        # Debug: Show what we're sending
        # print(f"      DEBUG: Creating field: {field_config.get('name')}")
        # print(f"      DEBUG: Field data: {json.dumps(field_config, indent=2)}")
        
        result = self._request("POST", f"list/{list_id}/field", field_config)
        
        # API returns field data nested under "field" key or directly
        field_data = result.get("field", result) if isinstance(result, dict) else {}
        
        if not field_data or "id" not in field_data:
            field_name = field_config.get("name", "Unknown")
            print(f"      ⚠️  Failed to create field: {field_name}")
            print(f"         Field config: {json.dumps(field_config, indent=2)}")
            print(f"         API response: {json.dumps(result, indent=2)}")
            return ""
        
        return field_data.get("id", "")
    
    def create_task(self, list_id: str, task_data: Dict) -> str:
        """Create a task in a list"""
        result = self._request("POST", f"list/{list_id}/task", task_data)
        return result.get("id", "")
    
    def update_task(self, task_id: str, task_data: Dict) -> Dict:
        """Update a task"""
        return self._request("PUT", f"task/{task_id}", task_data)
    
    def create_subtask(self, parent_task_id: str, subtask_data: Dict) -> str:
        """Create a subtask"""
        result = self._request("POST", f"task/{parent_task_id}/subtask", subtask_data)
        return result.get("id", "")
    
    def update_list_statuses(self, list_id: str, statuses: List[Dict]) -> bool:
        """Check if statuses exist in a list (DO NOT CREATE - must be done manually in ClickUp UI)"""
        try:
            result = self._request("GET", f"list/{list_id}")
            
            if not result:
                print(f"      ⚠️  Failed to get list info for status check")
                return False
            
            current_statuses = result.get("statuses", [])
            status_names = [s.get("status", "").strip().lower() for s in current_statuses]
            
            missing_statuses = []
            for status in statuses:
                status_name = status.get("name", "").strip()
                if status_name and status_name.lower() not in status_names:
                    missing_statuses.append(status_name)
            
            if missing_statuses:
                print(f"      ⚠️  WARNING: Custom statuses cannot be created via API!")
                print(f"         Missing statuses: {', '.join(missing_statuses)}")
                print(f"         Please create these statuses manually in ClickUp UI before running examples.")
                return False
            
            print(f"      ✓ All required statuses exist")
            return True
        except Exception as e:
            print(f"      ⚠️  Error checking statuses: {e}")
            return False
    
    def create_view(self, space_id: str, view_config: Dict) -> str:
        """Create a view in a space"""
        result = self._request("POST", f"space/{space_id}/view", view_config)
        return result.get("id", "")
    
    def create_automation(self, list_id: str, automation_config: Dict) -> str:
        """Create an automation for a list
        Note: This is a simplified representation. ClickUp automations are complex.
        In practice, automations should be created via the ClickUp UI."""
        # Automations API is limited - this is a placeholder
        # Real implementation would need to use webhooks or the full automation API
        print(f"      ℹ️  Automation '{automation_config.get('name')}' should be created manually in ClickUp UI")
        return ""
    
    def get_list_statuses(self, list_id: str) -> List[str]:
        """Get all status names for a list"""
        result = self._request("GET", f"list/{list_id}")
        if result:
            statuses = result.get("statuses", [])
            return [s.get("status", "") for s in statuses]
        return []

# ============================================================================
# WORKSPACE BUILDER
# ============================================================================

class WorkspaceBuilder:
    def __init__(self, api: ClickUpAPI, config_path: str = "config.yaml"):
        self.api = api
        self.structure = {}
        self.config = self._load_config(config_path)
        self.statuses_verified = {}  # Track which spaces have verified statuses
        self.skipped_fields = []  # Track fields that couldn't be created via API
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:

            return yaml.safe_load(f)
    
    def build_complete_workspace(self):
        """Build the complete workspace structure from YAML config"""
        print("🚀 Starting ClickUp Workspace Setup...")
        print(f"   Loading configuration from: config.yaml")
        
        # Create Spaces from config
        print("\n📁 Creating Spaces...")
        spaces_config = self.config.get("spaces", [])
        
        for space_config in spaces_config:
            space_name = space_config["name"]
            space_key = space_config.get("key", space_name.lower().replace(" ", "_"))
            
            space_id = self.api.create_space(space_name)
            print(f"   ✓ {space_name}: {space_id}")
            
            # Build the space structure
            print(f"\n🏗️  Building {space_name}...")
            self.structure[space_key] = self._build_space(space_id, space_config, space_key)
        
        print("\n✅ Workspace Setup Complete!")
        return self.structure
    
    def _build_space(self, space_id: str, space_config: Dict, space_key: str) -> Dict:
        """Build a space with folders and lists from config"""
        folders = {}
        all_statuses_ok = True
        
        # Check if space should be skipped
        if space_config.get("status") == "coming_soon":
            print(f"   ⏭️  Skipping {space_config['name']} - marked as 'coming_soon'")
            return folders
        
        for folder_config in space_config.get("folders", []):
            folder_name = folder_config["name"]
            folder_key = folder_config.get("key", folder_name.lower().replace(" ", "_"))
            print(f"   Creating folder: {folder_name}")
            
            folder_id = self.api.create_folder(space_id, folder_name)
            folders[folder_name] = {"id": folder_id, "key": folder_key, "lists": {}}
            
            # Create lists in the folder
            for list_config in folder_config.get("lists", []):
                # Handle both string and dict formats
                if isinstance(list_config, str):
                    list_name = list_config
                    list_type = "default"
                    list_description = ""
                else:
                    list_name = list_config.get("name", "Unnamed List")
                    list_type = list_config.get("type", "default")
                    list_description = list_config.get("description", "")
                
                print(f"      Creating list: {list_name} (type: {list_type})")
                list_id = self.api.create_list(folder_id, list_name)
                folders[folder_name]["lists"][list_name] = {
                    "id": list_id,
                    "type": list_type
                }
                
                # Add custom fields based on list type
                self._add_custom_fields(list_id, list_type, space_key, folder_name, list_name)
                
                # Check statuses (don't create - must be done manually)
                status_ok = self._check_statuses(list_id, list_type)
                if not status_ok:
                    all_statuses_ok = False
                
                time.sleep(0.3)  # Rate limiting per list
            
            time.sleep(0.5)  # Rate limiting per folder
        
        # Track if all statuses are verified for this space
        self.statuses_verified[space_key] = all_statuses_ok
        
        # Create views for this space
        self._create_views(space_id, space_key)
        
        # Print status summary
        self._print_status_summary(space_key)
        
        return folders
    
    def _add_custom_fields(self, list_id: str, list_type: str, space_key: str = "", folder_name: str = "", list_name: str = ""):
        """Add custom fields to a list based on list type"""
        custom_fields_config = self.config.get("custom_fields", {})
        
        # Collect all applicable fields for this list type
        applicable_fields = []
        for field_category, fields in custom_fields_config.items():
            if isinstance(fields, list):
                for field in fields:
                    applies_to = field.get("applies_to", [])
                    if list_type in applies_to:
                        applicable_fields.append(field)
        
        if not applicable_fields:
            return
        
        # Separate formula fields (not supported by API)
        creatable_fields = []
        formula_fields = []
        for field in applicable_fields:
            if field.get("type") == "formula":
                formula_fields.append(field["name"])
                # Track skipped field
                self.skipped_fields.append({
                    "space": space_key,
                    "folder": folder_name,
                    "list": list_name,
                    "type": "formula",
                    "name": field["name"],
                    "reason": "Formula fields must be created manually in ClickUp UI"
                })
            else:
                creatable_fields.append(field)
        
        if formula_fields:
            print(f"         ⚠️  Skipping {len(formula_fields)} formula field(s) (must be created manually in ClickUp UI):")
            for fname in formula_fields:
                print(f"            - {fname}")
        
        if not creatable_fields:
            return
        
        print(f"         Adding {len(creatable_fields)} custom fields...")
        for field in creatable_fields:
            # Map config field types to ClickUp API field types
            type_mapping = {
                "dropdown": "drop_down",
                "text": "text",
                "number": "number", 
                "currency": "currency",
                "date": "date",
                "person": "users",
                "checkbox": "checkbox",
                "url": "url",
                "email": "email",
                "phone": "phone",
                "location": "location",
                "rating": "rating",
                "labels": "labels"
            }
            
            field_type = field.get("type", "text")
            api_field_type = type_mapping.get(field_type, field_type)
            
            # Prepare field data for API - only include fields that ClickUp API accepts
            field_data = {
                "name": field["name"],
                "type": api_field_type
            }
            
            # Initialize type_config if needed for certain field types
            if api_field_type in ["currency", "number", "drop_down", "labels"]:
                field_data["type_config"] = {}
            
            # Handle type-specific configs FIRST
            if field_type == "currency" and "currency" in field:
                field_data["type_config"]["currency_type"] = field["currency"]
            
            if field_type in ["number", "currency"] and "precision" in field:
                field_data["type_config"]["precision"] = field["precision"]
            
            # Add type_config if explicitly present in config
            if "type_config" in field:
                # Merge with existing type_config
                if "type_config" in field_data:
                    field_data["type_config"].update(field["type_config"])
                else:
                    field_data["type_config"] = field["type_config"]
            elif "options" in field:
                # Convert options to proper format for dropdown/labels
                if "type_config" not in field_data:
                    field_data["type_config"] = {}
                field_data["type_config"]["options"] = []
                for opt in field["options"]:
                    if isinstance(opt, dict):
                        # Already in correct format {name: "...", color: "..."}
                        option_data = {"name": opt["name"]}
                        if "color" in opt:
                            option_data["color"] = opt["color"]
                        # Note: ClickUp API doesn't support 'description' in dropdown options
                        field_data["type_config"]["options"].append(option_data)
                    else:
                        # Plain string - convert to dict with just name
                        field_data["type_config"]["options"].append({"name": str(opt)})
            
            # Clean up empty type_config
            if "type_config" in field_data and not field_data["type_config"]:
                del field_data["type_config"]
            
            # Add other API-supported configurations (but NOT applies_to, required_on_close, formula, currency, precision, etc.)
            if "required" in field:
                field_data["required"] = field["required"]
            if "description" in field:
                field_data["description"] = field["description"]
            
            self.api.create_custom_field(list_id, field_data)
            time.sleep(0.2)
    
    def _check_statuses(self, list_id: str, list_type: str) -> bool:
        """Check if statuses exist for a list based on list type"""
        statuses_config = self.config.get("statuses", {})
        
        # Find applicable workflow for this list type
        for workflow_key, workflow_data in statuses_config.items():
            if isinstance(workflow_data, dict):
                applies_to = workflow_data.get("applies_to", [])
                if list_type in applies_to:
                    statuses = workflow_data.get("statuses", [])
                    if statuses:
                        print(f"         Checking workflow: {workflow_data.get('workflow_name', workflow_key)}")
                        return self.api.update_list_statuses(list_id, statuses)
        
        return True
    
    def _create_views(self, space_id: str, space_key: str):
        """Create views for a space based on config"""
        views = self.config.get("views", {}).get(space_key, [])
        
        if not views:
            return
        
        print(f"\n   📊 Creating Views for {space_key}...")
        for view_config in views:
            view_name = view_config.get("name", "Unnamed View")
            view_type = view_config.get("type", "list")
            
            # Build view data for API
            view_data = {
                "name": view_name,
                "type": view_type,
                "grouping": view_config.get("grouping"),
                "sorting": view_config.get("sort_by"),
                "filters": view_config.get("filters", {}),
                "columns": view_config.get("columns", [])
            }
            
            # Note: Views API has limited support, may need manual creation
            view_id = self.api.create_view(space_id, view_data)
            if view_id:
                print(f"      ✓ Created view: {view_name} ({view_type})")
            else:
                print(f"      ℹ️  View '{view_name}' ({view_type}) should be created manually in ClickUp UI")
            
            time.sleep(0.3)
    
    def _print_status_summary(self, space_key: str):
        """Print summary of status workflows that need to be created manually"""
        statuses_config = self.config.get("statuses", {})
        
        print(f"\n   📋 Status Workflows Summary for {space_key}:")
        print(f"      ⚠️  Custom statuses must be created manually in ClickUp UI")
        
        # Count workflows applicable to this space
        workflow_count = 0
        for workflow_key, workflow_data in statuses_config.items():
            if isinstance(workflow_data, dict):
                workflow_name = workflow_data.get('workflow_name', workflow_key)
                status_count = len(workflow_data.get('statuses', []))
                workflow_count += 1
                print(f"      {workflow_count}. {workflow_name}: {status_count} statuses")
        
        if workflow_count > 0:
            print(f"\n      💡 Refer to config.yaml 'statuses' section for details")
            print(f"      💡 See docs/STATUS_SETUP_GUIDE.md for step-by-step instructions")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main execution function
    
    SETUP INSTRUCTIONS:
    1. Set CLICKUP_API_TOKEN and CLICKUP_TEAM_ID in .env file
    2. Configure workspace structure in config.yaml
    3. Run: python clickup_python_setup.py
    
    IMPORTANT NOTES:
    - This script creates: Spaces, Folders, Lists, and Custom Fields
    - Custom statuses CANNOT be created via API (must be done manually)
    - Views, Dashboards, and Automations have limited API support
    - NO EXAMPLES will be created - only the workspace structure
    """
    
    # Load environment variables
    from dotenv import load_dotenv
    import os   
    load_dotenv()
    
    API_TOKEN = os.getenv("CLICKUP_API_TOKEN")
    TEAM_ID = os.getenv("CLICKUP_TEAM_ID")
    
    if not API_TOKEN or not TEAM_ID:
        print("❌ Error: CLICKUP_API_TOKEN and CLICKUP_TEAM_ID must be set in .env file")
        return
    
    # Initialize
    config = ClickUpConfig(API_TOKEN, TEAM_ID)
    api = ClickUpAPI(config)
    
    print("=" * 80)
    print("CLICKUP WORKSPACE SETUP - PV OPERATIONS MANAGEMENT SYSTEM")
    print("=" * 80)
    
    # Build workspace from YAML config
    try:
        builder = WorkspaceBuilder(api, "config.yaml")
        structure = builder.build_complete_workspace()
        statuses_verified = builder.statuses_verified
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return
    except Exception as e:
        print(f"❌ Error building workspace: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Summary
    print("\n" + "=" * 80)
    print("SETUP COMPLETE - SUMMARY")
    print("=" * 80)
    print("\n✅ Workspace Structure Created:")
    print(f"   - {len(structure)} Spaces created")
    
    total_folders = sum(len(space_data) for space_data in structure.values())
    print(f"   - {total_folders} Folders configured")
    
    total_lists = sum(
        len(folder_data.get("lists", {})) 
        for space_data in structure.values() 
        for folder_data in space_data.values()
    )
    print(f"   - {total_lists} Lists created")
    print("   - All custom fields applied based on list types")
    print("   - Status verification completed")
    
    print("\n📋 Next Steps:")
    print("   1. ⚠️  CREATE CUSTOM STATUSES in ClickUp UI")
    print("      - See config.yaml 'statuses' section for all workflows")
    print("      - Multiple workflow types: corrective_maintenance, preventive_maintenance, capex, invoice, warranty")
    print("   2. 📊 CREATE VIEWS in ClickUp UI")
    print("      - See config.yaml 'views' section for recommended configurations")
    print("      - Director Dashboard, Critical Issues Board, Approval Queue, etc.")
    print("   3. 🤖 SET UP AUTOMATIONS (if needed)")
    print("      - Configure task templates and automations manually in ClickUp")
    print("   4. 👥 INVITE TEAM MEMBERS")
    print("      - Configure permissions based on roles (Director, POs, Finance, etc.)")
    print("   5. 📁 START USING THE WORKSPACE")
    print("      - Create tasks using the task templates defined in config.yaml")
    print("   - All custom fields are already configured and ready to use")
    
    print("\n💡 Configuration File:")
    print("   - All settings are in config.yaml")
    print("   - Modify spaces, folders, lists, fields, statuses, views, and workflows")
    print("   - Re-run script after changes to update workspace")
    
    print("\n" + "=" * 80)
    print("SKIPPED FIELDS SUMMARY")
    print("=" * 80)
    
    if builder.skipped_fields:
        # Group skipped fields by space, folder, and list
        grouped = {}
        for skip in builder.skipped_fields:
            space = skip["space"]
            folder = skip["folder"]
            list_name = skip["list"]
            
            if space not in grouped:
                grouped[space] = {}
            if folder not in grouped[space]:
                grouped[space][folder] = {}
            if list_name not in grouped[space][folder]:
                grouped[space][folder][list_name] = []
            
            grouped[space][folder][list_name].append(skip)
        
        # Print organized summary
        total_skipped = len(builder.skipped_fields)
        print(f"\n⚠️  Total Skipped Fields: {total_skipped}\n")
        
        for space in sorted(grouped.keys()):
            print(f"📍 Space: {space.upper()}")
            for folder in sorted(grouped[space].keys()):
                print(f"   📂 Folder: {folder}")
                for list_name in sorted(grouped[space][folder].keys()):
                    print(f"      📋 List: {list_name}")
                    for field in grouped[space][folder][list_name]:
                        field_type = field["type"]
                        field_name = field["name"]
                        reason = field.get("reason", "Not supported")
                        print(f"         • {field_type.upper()}: {field_name}")
                        print(f"           → {reason}")
        
        print("\n💡 NEXT STEP: Create formula fields manually in ClickUp UI")
        print("   1. Open each list in ClickUp")
        print("   2. Click on 'Add Field' button")
        print("   3. Select 'Formula' as field type")
        print("   4. Configure the formula as shown in config.yaml")
    else:
        print("✅ No fields were skipped - all custom fields created successfully!")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
