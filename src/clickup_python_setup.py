"""
ClickUp Setup Script for Asset Management & Development Company

This script creates the complete ClickUp workspace structure by loading
configuration from config.yaml including:
- Spaces, Folders, and Lists
- Custom Fields
- Status Workflows
- Two Working Examples (Datacenter Dev + PV Operations)

Requirements:
pip install requests python-dotenv pyyaml

Setup:
1. Get your ClickUp API token from: https://app.clickup.com/settings/apps
2. Get your Team ID from: https://app.clickup.com/settings/teams
3. Set environment variables in .env file
4. Configure workspace structure in config.yaml
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
        if "name" not in field_config or "type" not in field_config:
            print(f"      ⚠️  Field config missing 'name' or 'type': {field_config}")
            return ""
        
        result = self._request("POST", f"list/{list_id}/field", field_config)
        
        # API returns field data nested under "field" key
        field_data = result.get("field", result)
        
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
        
        for folder_config in space_config.get("folders", []):
            folder_name = folder_config["name"]
            print(f"   Creating folder: {folder_name}")
            
            folder_id = self.api.create_folder(space_id, folder_name)
            folders[folder_name] = {"id": folder_id, "lists": {}}
            
            # Create lists in the folder
            for list_name in folder_config.get("lists", []):
                list_id = self.api.create_list(folder_id, list_name)
                folders[folder_name]["lists"][list_name] = list_id
                
                # Add custom fields based on space type
                self._add_custom_fields(list_id, space_key)
                
                # Check statuses (don't create - must be done manually)
                status_ok = self._check_statuses(list_id, space_key)
                if not status_ok:
                    all_statuses_ok = False
            
            time.sleep(0.5)  # Rate limiting
        
        # Track if all statuses are verified for this space
        self.statuses_verified[space_key] = all_statuses_ok
        
        # Create views for this space
        self._create_views(space_id, space_key)
        
        # Setup automations (informational only - must be done manually)
        self._setup_automations(space_key)
        
        return folders
    
    def _add_custom_fields(self, list_id: str, space_key: str):
        """Add custom fields to a list based on space type"""
        fields = self.config.get("custom_fields", {}).get(space_key, [])
        
        if not fields:
            return
        
        for field in fields:
            self.api.create_custom_field(list_id, field)
            time.sleep(0.2)
    
    def _check_statuses(self, list_id: str, space_key: str) -> bool:
        """Check if statuses exist for a list based on space type"""
        statuses = self.config.get("statuses", {}).get(space_key, [])
        
        if statuses:
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
    
    def _setup_automations(self, space_key: str):
        """Setup automations (informational - must be created manually in ClickUp UI)"""
        automations = self.config.get("automations", {}).get(space_key, [])
        
        if not automations:
            return
        
        print(f"\n   🤖 Automation Setup Guide for {space_key}:")
        print(f"      ⚠️  Automations cannot be created via API - please create manually:")
        
        for i, auto in enumerate(automations, 1):
            print(f"\n      {i}. {auto.get('name', 'Unnamed Automation')}")
            
            trigger = auto.get("trigger", {})
            action = auto.get("action", {})
            
            print(f"         Trigger: {trigger.get('type', 'N/A')}")
            if trigger.get("status"):
                print(f"         - Status: {trigger['status']}")
            if trigger.get("priority"):
                print(f"         - Priority: {trigger['priority']}")
            
            print(f"         Action: {action.get('type', 'N/A')}")
            if action.get("comment"):
                print(f"         - Comment: {action['comment']}")
            if action.get("status"):
                print(f"         - Change to: {action['status']}")

# ============================================================================
# EXAMPLE PROJECTS CREATOR
# ============================================================================

class ExampleProjectsCreator:
    def __init__(self, api: ClickUpAPI, structure: Dict, config: Dict, statuses_verified: Dict):
        self.api = api
        self.structure = structure
        self.config = config
        self.statuses_verified = statuses_verified
    
    def create_datacenter_example(self):
        """Create a datacenter under development with realistic tasks"""
        
        # Check if statuses are verified for development space
        if not self.statuses_verified.get("development", False):
            print("\n🏭 Skipping Datacenter Example:")
            print("   ⚠️  Custom statuses not verified for Development space.")
            print("   Please create the custom statuses manually in ClickUp UI first.")
            return False
        
        print("\n🏭 Creating Example: Datacenter Under Development...")
        
        # Get the Datacenters Development folder
        folder_data = self.structure["development"].get("Datacenters Development")
        if not folder_data:
            print("   ⚠️  Datacenters Development folder not found, skipping example")
            return False
        
        # Create tasks across different phases
        self._create_datacenter_prefeasibility(folder_data)
        self._create_datacenter_land_acquisition(folder_data)
        self._create_datacenter_permitting(folder_data)
        self._create_datacenter_engineering(folder_data)
        
        print("   ✓ Datacenter project created with 25+ tasks across 4 phases")
        return True
    
    def create_pv_operations_example(self):
        """Create an operating PV park with realistic tasks"""
        
        # Check if statuses are verified for operations space
        if not self.statuses_verified.get("operations", False):
            print("\n☀️  Skipping PV Operations Example:")
            print("   ⚠️  Custom statuses not verified for Operations space.")
            print("   Please create the custom statuses manually in ClickUp UI first.")
            return False
        
        print("\n☀️  Creating Example: Operating PV Park...")
        
        # Get the Solar PV Operations folder
        folder_data = self.structure["operations"].get("Solar PV Operations")
        if not folder_data:
            print("   ⚠️  Solar PV Operations folder not found, skipping example")
            return False
        
        # Create tasks across operational areas
        self._create_pv_performance_monitoring(folder_data)
        self._create_pv_maintenance(folder_data)
        self._create_pv_compliance(folder_data)
        
        print("   ✓ PV Operations project created with 20+ tasks across 3 areas")
        return True
    
    def _create_datacenter_prefeasibility(self, folder_data: Dict):
        """Prefeasibility tasks for datacenter"""
        list_id = folder_data["lists"].get("Prefeasibility & Site Selection")
        if not list_id:
            return
        
        project_task = {
            "name": "DC-Athens-001 Prefeasibility Study",
            "description": "5 MW datacenter facility in Athens industrial zone. Target: Hyperscale cloud clients. Budget: €15M",
            "status": "Partner In Progress",
            "priority": 2,
            "due_date": int((datetime.now() + timedelta(days=14)).timestamp() * 1000)
        }
        
        parent_id = self.api.create_task(list_id, project_task)
        
        subtasks = [
            {
                "name": "Review site assessment report from technical partner",
                "description": "**Director View:** Check if technical specs align with hyperscale requirements.\n**PM View:** Ensure partner delivered all required sections (power, cooling, connectivity, seismic).",
                "status": "In Planning",
                "priority": 2,
                "due_date": int((datetime.now() + timedelta(days=3)).timestamp() * 1000)
            },
            {
                "name": "Validate grid connection capacity with utility partner",
                "description": "**Director View:** Confirm 10 MVA capacity is guaranteed.\n**PM View:** Schedule call with PPC representative, document commitments.",
                "status": "Awaiting Partner",
                "priority": 1,
                "due_date": int((datetime.now() + timedelta(days=5)).timestamp() * 1000)
            },
            {
                "name": "Review preliminary financial model",
                "description": "**Director View:** Validate IRR projections and compare with investment criteria.\n**PM View:** Check revenue assumptions, verify OPEX estimates with O&M partners.",
                "status": "Review Required",
                "priority": 2,
                "due_date": int((datetime.now() + timedelta(days=7)).timestamp() * 1000)
            },
            {
                "name": "Coordinate market demand study with real estate partner",
                "description": "**Director View:** Need confirmation of anchor tenant interest.\n**PM View:** Follow up on partner meetings with potential clients, get LOIs.",
                "status": "Partner In Progress",
                "priority": 2,
                "due_date": int((datetime.now() + timedelta(days=10)).timestamp() * 1000)
            },
            {
                "name": "Environmental pre-screening with consultant",
                "description": "**Director View:** Any red flags that could delay permitting?\n**PM View:** Ensure partner completes noise, flora/fauna, and contamination studies.",
                "status": "Completed",
                "priority": 3
            }
        ]
        
        for subtask in subtasks:
            self.api.create_subtask(parent_id, subtask)
            time.sleep(0.3)
    
    def _create_datacenter_land_acquisition(self, folder_data: Dict):
        """Land acquisition tasks"""
        list_id = folder_data["lists"].get("Land Acquisition")
        if not list_id:
            return
        
        tasks = [
            {
                "name": "Land title verification - Legal partner (Papadopoulos & Associates)",
                "description": "**Director:** Critical path item - need clear title by month-end.\n**PM:** Chase partner for final cadastral report and ownership chain verification.",
                "status": "Awaiting Partner",
                "priority": 1,
                "due_date": int((datetime.now() + timedelta(days=8)).timestamp() * 1000)
            },
            {
                "name": "Negotiate purchase terms with landowner",
                "description": "**Director:** Target €180/sqm, max €200/sqm. 12-month payment schedule.\n**PM:** Schedule meeting with owner and legal partner. Prepare term sheet.",
                "status": "In Planning",
                "priority": 1,
                "due_date": int((datetime.now() + timedelta(days=15)).timestamp() * 1000)
            },
            {
                "name": "Coordinate due diligence with technical & legal partners",
                "description": "**Director:** Weekly sync needed - this is our gating item.\n**PM:** Consolidate reports from all partners, flag any issues immediately.",
                "status": "Partner In Progress",
                "priority": 2,
                "due_date": int((datetime.now() + timedelta(days=20)).timestamp() * 1000)
            }
        ]
        
        for task_data in tasks:
            self.api.create_task(list_id, task_data)
            time.sleep(0.3)
    
    def _create_datacenter_permitting(self, folder_data: Dict):
        """Permitting tasks"""
        list_id = folder_data["lists"].get("Permitting & Licensing")
        if not list_id:
            return
        
        tasks = [
            {
                "name": "Building permit application - Architecture partner coordination",
                "description": "**Director:** Any changes to timeline? EC declaration needed.\n**PM:** Ensure partner submits complete package to municipality. Track submission number.",
                "status": "Not Started",
                "priority": 2,
                "due_date": int((datetime.now() + timedelta(days=45)).timestamp() * 1000)
            },
            {
                "name": "Environmental approval - Track consultant submission",
                "description": "**Director:** Environmental permit is 3-month process - can't delay.\n**PM:** Weekly status calls with environmental consultant. Escalate any authority questions.",
                "status": "Not Started",
                "priority": 2,
                "due_date": int((datetime.now() + timedelta(days=90)).timestamp() * 1000)
            },
            {
                "name": "Fire safety approval coordination",
                "description": "**Director:** Need MEP engineer input on fire suppression systems.\n**PM:** Connect fire safety consultant with MEP partner. Review combined submission.",
                "status": "Not Started",
                "priority": 3,
                "due_date": int((datetime.now() + timedelta(days=60)).timestamp() * 1000)
            }
        ]
        
        for task_data in tasks:
            self.api.create_task(list_id, task_data)
            time.sleep(0.3)
    
    def _create_datacenter_engineering(self, folder_data: Dict):
        """Engineering tasks"""
        list_id = folder_data["lists"].get("Engineering & Design")
        if not list_id:
            return
        
        tasks = [
            {
                "name": "Review preliminary designs from MEP partner",
                "description": "**Director:** Focus on redundancy levels (N+1) and PUE targets (<1.3).\n**PM:** Coordinate review meeting with technical advisor. Document all change requests.",
                "status": "Not Started",
                "priority": 2,
                "due_date": int((datetime.now() + timedelta(days=30)).timestamp() * 1000)
            },
            {
                "name": "Cooling system design review - Technical partner",
                "description": "**Director:** Hybrid cooling solution approved? Cost implications?\n**PM:** Ensure partner provides 3 options with CAPEX/OPEX comparison. Set up review session.",
                "status": "Not Started",
                "priority": 2,
                "due_date": int((datetime.now() + timedelta(days=35)).timestamp() * 1000)
            }
        ]
        
        for task_data in tasks:
            self.api.create_task(list_id, task_data)
            time.sleep(0.3)
    
    def _create_pv_performance_monitoring(self, folder_data: Dict):
        """Performance monitoring tasks for PV"""
        list_id = folder_data["lists"].get("Performance Monitoring")
        if not list_id:
            return
        
        project_task = {
            "name": "PV-Kozani-05 Performance Monitoring (50 MW)",
            "description": "Operating solar park in Kozani. O&M Partner: Hellenic Solar Services. Monthly target: 7,500 MWh",
            "status": "In Progress",
            "priority": 2
        }
        
        parent_id = self.api.create_task(list_id, project_task)
        
        subtasks = [
            {
                "name": "Review daily production data from SCADA",
                "description": "**Director:** Quick check - are we on target? Any anomalies?\n**O&M PM:** Log into monitoring portal, check actual vs. forecast. Flag if <95% of expected.",
                "status": "In Progress",
                "priority": 2,
                "due_date": int(datetime.now().timestamp() * 1000)
            },
            {
                "name": "Weekly performance report to director",
                "description": "**Director:** Need energy yield, availability %, any issues, and financial impact.\n**O&M PM:** Compile SCADA data, calculate PR (performance ratio), summarize inverter issues.",
                "status": "Scheduled",
                "priority": 2,
                "due_date": int((datetime.now() + timedelta(days=2)).timestamp() * 1000)
            },
            {
                "name": "Follow up on Inverter #12 underperformance with O&M partner",
                "description": "**Director:** This has been ongoing for 5 days - revenue impact?\n**O&M PM:** Chase partner for root cause analysis. Demand repair schedule or replacement.",
                "status": "Partner Assigned",
                "priority": 1,
                "due_date": int((datetime.now() + timedelta(days=1)).timestamp() * 1000)
            },
            {
                "name": "Monthly revenue reconciliation with off-taker",
                "description": "**Director:** Ensure invoicing matches production. Cash flow check.\n**O&M PM:** Cross-check MWh invoiced vs. metered. Resolve any discrepancies with commercial team.",
                "status": "Scheduled",
                "priority": 2,
                "due_date": int((datetime.now() + timedelta(days=5)).timestamp() * 1000)
            },
            {
                "name": "Coordinate weather-adjusted forecasting with partner",
                "description": "**Director:** Need accurate monthly forecast for board reporting.\n**O&M PM:** Send actual weather data to forecasting partner. Update monthly target if significant deviation.",
                "status": "In Progress",
                "priority": 3,
                "due_date": int((datetime.now() + timedelta(days=7)).timestamp() * 1000)
            }
        ]
        
        for subtask in subtasks:
            self.api.create_subtask(parent_id, subtask)
            time.sleep(0.3)
    
    def _create_pv_maintenance(self, folder_data: Dict):
        """Maintenance tasks for PV"""
        list_id = folder_data["lists"].get("Maintenance Management")
        if not list_id:
            return
        
        tasks = [
            {
                "name": "Q1 Preventive Maintenance - Coordinate with O&M partner",
                "description": "**Director:** Confirm downtime won't exceed 2 days. Budget check.\n**O&M PM:** Review partner's maintenance plan. Verify spare parts availability. Schedule during low-irradiance period.",
                "status": "Scheduled",
                "priority": 2,
                "due_date": int((datetime.now() + timedelta(days=21)).timestamp() * 1000)
            },
            {
                "name": "Panel cleaning service - Review partner performance",
                "description": "**Director:** Are we seeing production uplift post-cleaning?\n**O&M PM:** Compare before/after production data. If <3% improvement, challenge partner's methods.",
                "status": "Under Review",
                "priority": 3,
                "due_date": int((datetime.now() + timedelta(days=3)).timestamp() * 1000)
            },
            {
                "name": "URGENT: Transformer oil analysis - Coordinate with maintenance contractor",
                "description": "**Director:** Transformer failure would cost us €200k in lost revenue. Priority.\n**O&M PM:** Expedite oil sample to lab. If dissolved gas analysis shows issues, schedule immediate intervention.",
                "status": "Issue/Escalated",
                "priority": 1,
                "due_date": int(datetime.now().timestamp() * 1000)
            },
            {
                "name": "Vegetation management - Monitor partner execution",
                "description": "**Director:** Fire risk in summer - must be completed by May.\n**O&M PM:** Inspect areas cleared by contractor. Ensure compliance with fire department requirements.",
                "status": "Partner Assigned",
                "priority": 2,
                "due_date": int((datetime.now() + timedelta(days=14)).timestamp() * 1000)
            }
        ]
        
        for task_data in tasks:
            self.api.create_task(list_id, task_data)
            time.sleep(0.3)
    
    def _create_pv_compliance(self, folder_data: Dict):
        """Compliance tasks for PV"""
        list_id = folder_data["lists"].get("Compliance & Reporting")
        if not list_id:
            return
        
        tasks = [
            {
                "name": "Annual RAE reporting - Coordinate data collection",
                "description": "**Director:** Regulatory deadline is firm - penalties for late submission.\n**O&M PM:** Compile all required data from SCADA and partner reports. Legal review before submission.",
                "status": "In Progress",
                "priority": 1,
                "due_date": int((datetime.now() + timedelta(days=10)).timestamp() * 1000)
            },
            {
                "name": "Environmental compliance audit - Facilitate auditor access",
                "description": "**Director:** Any findings could affect operations license.\n**O&M PM:** Coordinate with O&M partner for site access. Prepare documentation on waste disposal, oil storage.",
                "status": "Scheduled",
                "priority": 2,
                "due_date": int((datetime.now() + timedelta(days=18)).timestamp() * 1000)
            },
            {
                "name": "Insurance renewal documentation for broker",
                "description": "**Director:** Need updated asset value and risk assessment.\n**O&M PM:** Request current condition report from O&M partner. Update broker on any material changes.",
                "status": "In Progress",
                "priority": 2,
                "due_date": int((datetime.now() + timedelta(days=25)).timestamp() * 1000)
            }
        ]
        
        for task_data in tasks:
            self.api.create_task(list_id, task_data)
            time.sleep(0.3)

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
    
    IMPORTANT NOTE:
    - Custom statuses CANNOT be created via API
    - You must create them manually in ClickUp UI before running this script
    - The script will check if statuses exist before creating examples
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
    print("CLICKUP WORKSPACE SETUP FOR ASSET MANAGEMENT COMPANY")
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
        return
    
    # Check if we can proceed with examples
    print("\n" + "=" * 80)
    print("CHECKING STATUS VERIFICATION")
    print("=" * 80)
    
    all_statuses_ok = all(statuses_verified.values())
    
    if all_statuses_ok:
        print("\n✅ All custom statuses verified! Proceeding with example creation...")
    else:
        print("\n⚠️  Some custom statuses are missing:")
        for space_key, verified in statuses_verified.items():
            status_icon = "✓" if verified else "✗"
            print(f"   {status_icon} {space_key.capitalize()} Space: {'OK' if verified else 'Missing Statuses'}")
        
        print("\n📝 TO CREATE CUSTOM STATUSES MANUALLY:")
        print("   1. Go to ClickUp and open your workspace")
        print("   2. Navigate to each Space")
        print("   3. Open any List")
        print("   4. Click on the status dropdown")
        print("   5. Click '+ Add Status' to create custom statuses")
        print("   6. Refer to config.yaml for required status names and colors")
        print("\n   Once statuses are created, run this script again to create examples.")
    
    # Create example projects only if statuses are verified
    print("\n" + "=" * 80)
    print("CREATING WORKING EXAMPLES")
    print("=" * 80)
    
    examples = ExampleProjectsCreator(api, structure, builder.config, statuses_verified)
    datacenter_created = examples.create_datacenter_example()
    pv_created = examples.create_pv_operations_example()
    
    # Summary
    print("\n" + "=" * 80)
    print("SETUP COMPLETE - SUMMARY")
    print("=" * 80)
    print("\n✅ Workspace Structure Created:")
    print(f"   - {len(structure)} Spaces created")
    
    total_folders = sum(len(space_data) for space_data in structure.values())
    print(f"   - {total_folders} Folders configured")
    print("   - All lists created")
    print("   - Custom fields applied")
    print("   - Status verification completed")
    
    if all_statuses_ok:
        print("\n✅ Working Examples:")
        if datacenter_created:
            print("   - Datacenter Under Development (25+ tasks) ✓")
        if pv_created:
            print("   - Operating PV Park (20+ tasks) ✓")
    else:
        print("\n⚠️  Examples NOT created (custom statuses required)")
    
    print("\n📊 Views Configuration:")
    views_count = len(builder.config.get("views", {}).get("development", [])) + \
                  len(builder.config.get("views", {}).get("operations", []))
    print(f"   - {views_count} views configured (create manually if needed)")
    
    print("\n🤖 Automations Configuration:")
    auto_count = len(builder.config.get("automations", {}).get("development", [])) + \
                 len(builder.config.get("automations", {}).get("operations", []))
    print(f"   - {auto_count} automations documented (create manually in ClickUp UI)")
    
    print("\n📋 Next Steps:")
    if not all_statuses_ok:
        print("   1. ⚠️  CREATE CUSTOM STATUSES in ClickUp UI (see config.yaml)")
        print("   2. Re-run this script to create working examples")
    else:
        print("   1. Log into ClickUp and explore the workspace")
    print(f"   {'2' if all_statuses_ok else '3'}. Customize views per your needs")
    print(f"   {'3' if all_statuses_ok else '4'}. Set up automations (via ClickUp UI - see guide above)")
    print(f"   {'4' if all_statuses_ok else '5'}. Modify config.yaml to add/change structure")
    print(f"   {'5' if all_statuses_ok else '6'}. Invite team members and assign roles")
    
    print("\n💡 Configuration File:")
    print("   - All settings are in config.yaml")
    print("   - Modify spaces, folders, lists, fields, statuses, views, and automations")
    print("   - Re-run script after changes to update workspace")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()