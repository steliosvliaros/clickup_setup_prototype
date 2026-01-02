"""
ClickUp Setup Script for Asset Management & Development Company

This script creates the complete ClickUp workspace structure including:
- Spaces, Folders, and Lists
- Custom Fields
- Task Templates
- Status Workflows
- Automation Rules
- Two Working Examples (Datacenter Dev + PV Operations)

Requirements:
pip install requests python-dotenv

Setup:
1. Get your ClickUp API token from: https://app.clickup.com/settings/apps
2. Get your Team ID from: https://app.clickup.com/settings/teams
3. Set environment variables or update the config below
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

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
        # optional, but commonly useful:
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
            
            # Add small delay to respect rate limits (100 req/min = ~0.6s per request)
            time.sleep(0.5)  # Conservative baseline
            
            return response.json() if response.text else {}
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limit exceeded
                print("Rate limit hit, waiting 60 seconds...")
                time.sleep(60)
                return self._request(method, endpoint, data)  # Retry
            print(f"API Error: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return {}
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return {}
    
    ''
    # Spaces
    def create_space(self, name: str) -> str:
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
    
    # Folders
    def create_folder(self, space_id: str, name: str) -> str:
        """Create a folder in a space"""
        data = {"name": name}
        result = self._request("POST", f"space/{space_id}/folder", data)
        return result.get("id", "")
    
    # Lists
    def create_list(self, folder_id: str, name: str) -> str:
        """Create a list in a folder"""
        data = {"name": name}
        result = self._request("POST", f"folder/{folder_id}/list", data)
        return result.get("id", "")
    
    # Custom Fields
    def create_custom_field(self, list_id: str, field_config: Dict) -> str:
        """Create a custom field in a list"""
        result = self._request("POST", f"list/{list_id}/field", field_config)
        return result.get("id", "")
    
    # Tasks
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
    
    # Statuses
    def update_list_statuses(self, list_id: str, statuses: List[Dict]) -> bool:
        """Update statuses for a list"""
        # Get current statuses
        result = self._request("GET", f"list/{list_id}")
        
        if not result:
            print(f"      ⚠️  Failed to get list info for status setup")
            return False
        
        # Add new statuses - ClickUp will handle duplicates
        for status in statuses:
            if not status.get("status"):  # Validate status name exists
                print(f"      ⚠️  Skipping status with missing name")
                continue
                
            data = {
                "status": status["status"], 
                "color": status.get("color", "#d3d3d3"), 
                "type": status.get("type", "custom")
            }
            self._request("POST", f"list/{list_id}/status", data)
        
        return True
    
    # Views
    def create_view(self, space_id: str, view_config: Dict) -> str:
        """Create a view in a space"""
        result = self._request("POST", f"space/{space_id}/view", view_config)
        return result.get("id", "")

# ============================================================================
# WORKSPACE BUILDER
# ============================================================================

class WorkspaceBuilder:
    def __init__(self, api: ClickUpAPI):
        self.api = api
        self.structure = {}
    
    def build_complete_workspace(self):
        """Build the complete workspace structure"""
        print("🚀 Starting ClickUp Workspace Setup...")
        
        # Create Spaces
        print("\n📁 Creating Spaces...")
        dev_space_id = self.api.create_space("Development Projects")
        ops_space_id = self.api.create_space("Operations & Maintenance")
        corp_space_id = self.api.create_space("Corporate & Shared")
        
        self.structure["spaces"] = {
            "development": dev_space_id,
            "operations": ops_space_id,
            "corporate": corp_space_id
        }
        
        print(f"   ✓ Development Projects: {dev_space_id}")
        print(f"   ✓ Operations & Maintenance: {ops_space_id}")
        print(f"   ✓ Corporate & Shared: {corp_space_id}")
        
        # Build Development Space
        print("\n🏗️  Building Development Space...")
        self.structure["development"] = self._build_development_space(dev_space_id)
        
        # Build Operations Space
        print("\n⚙️  Building Operations Space...")
        self.structure["operations"] = self._build_operations_space(ops_space_id)
        
        # Build Corporate Space
        print("\n🏢 Building Corporate Space...")
        self.structure["corporate"] = self._build_corporate_space(corp_space_id)
        
        print("\n✅ Workspace Setup Complete!")
        return self.structure
    
    def _build_development_space(self, space_id: str) -> Dict:
        """Build development space with folders and lists"""
        folders = {}
        
        # Asset type folders with their phase lists
        asset_types = {
            "Solar PV Development": [
                "Prefeasibility & Site Selection",
                "Land Acquisition",
                "Permitting & Licensing",
                "Engineering & Design",
                "Procurement",
                "Construction",
                "Commissioning"
            ],
            "Datacenters Development": [
                "Prefeasibility & Site Selection",
                "Land Acquisition",
                "Permitting & Licensing",
                "Engineering & Design",
                "Procurement",
                "Construction",
                "Commissioning"
            ],
            "Hotels Development": [
                "Prefeasibility & Site Selection",
                "Land Acquisition",
                "Permitting & Licensing",
                "Engineering & Design",
                "Procurement",
                "Construction",
                "Commissioning"
            ],
            "Hydroponic Farms Development": [
                "Prefeasibility & Site Selection",
                "Land Acquisition",
                "Permitting & Licensing",
                "Engineering & Design",
                "Procurement",
                "Construction",
                "Commissioning"
            ]
        }
        
        for folder_name, phase_lists in asset_types.items():
            print(f"   Creating folder: {folder_name}")
            folder_id = self.api.create_folder(space_id, folder_name)
            folders[folder_name] = {"id": folder_id, "lists": {}}
            
            for list_name in phase_lists:
                list_id = self.api.create_list(folder_id, list_name)
                folders[folder_name]["lists"][list_name] = list_id
                
                # Add custom fields to each list
                self._add_development_custom_fields(list_id)
                
                # Set up statuses
                self._setup_development_statuses(list_id)
            
            time.sleep(0.5)  # Rate limiting
        
        return folders
    
    def _build_operations_space(self, space_id: str) -> Dict:
        """Build operations space with folders and lists"""
        folders = {}
        
        asset_types = {
            "Solar PV Operations": [
                "Performance Monitoring",
                "Maintenance Management",
                "Compliance & Reporting",
                "Asset Optimization",
                "Incident Management"
            ],
            "Wind Farms Operations": [
                "Performance Monitoring",
                "Maintenance Management",
                "Compliance & Reporting",
                "Asset Optimization",
                "Incident Management"
            ],
            "Hotels Operations": [
                "Performance Monitoring",
                "Maintenance Management",
                "Compliance & Reporting",
                "Asset Optimization",
                "Incident Management"
            ]
        }
        
        for folder_name, operational_lists in asset_types.items():
            print(f"   Creating folder: {folder_name}")
            folder_id = self.api.create_folder(space_id, folder_name)
            folders[folder_name] = {"id": folder_id, "lists": {}}
            
            for list_name in operational_lists:
                list_id = self.api.create_list(folder_id, list_name)
                folders[folder_name]["lists"][list_name] = list_id
                
                # Add custom fields
                self._add_operations_custom_fields(list_id)
                
                # Set up statuses
                self._setup_operations_statuses(list_id)
            
            time.sleep(0.5)
        
        return folders
    
    def _build_corporate_space(self, space_id: str) -> Dict:
        """Build corporate space"""
        folders = {}
        
        corporate_areas = {
            "Financial Management": ["Budget Tracking", "Financial Reporting", "Invoicing"],
            "HR & Administration": ["Recruitment", "Team Management", "Admin Tasks"],
            "Partner Management": ["Partner Onboarding", "Performance Review", "Contracts"],
            "Strategic Initiatives": ["Strategic Projects", "Business Development"]
        }
        
        for folder_name, lists in corporate_areas.items():
            folder_id = self.api.create_folder(space_id, folder_name)
            folders[folder_name] = {"id": folder_id, "lists": {}}
            
            for list_name in lists:
                list_id = self.api.create_list(folder_id, list_name)
                folders[folder_name]["lists"][list_name] = list_id
            
            time.sleep(0.5)
        
        return folders
    
    def _add_development_custom_fields(self, list_id: str):
        """Add custom fields for development projects"""
        fields = [
            {
                "name": "Project Value", 
                "type": "currency",
                "type_config": {
                    "default": 0,
                    "precision": 2,
                    "currency_type": "EUR"  # Add this
                }
            },
            {"name": "Capacity/Size", "type": "short_text"},
            {
                "name": "Development Stage",
                "type": "drop_down",
                "type_config": {
                    "options": [
                        {"name": "Prefeasibility", "color": "#6fddff"},
                        {"name": "Land Acquisition", "color": "#b4e7ff"},
                        {"name": "Permitting", "color": "#7ee37e"},
                        {"name": "Engineering", "color": "#ffcc00"},
                        {"name": "Procurement", "color": "#ff9900"},
                        {"name": "Construction", "color": "#ff6600"},
                        {"name": "Commissioning", "color": "#00cc66"}
                    ]
                }
            },
            {"name": "Expected COD", "type": "date"},
            {"name": "Location", "type": "short_text"},
            {"name": "Lead Partner", "type": "short_text"},
            {
                "name": "Budget Status",
                "type": "drop_down",
                "type_config": {
                    "options": [
                        {"name": "On Budget", "color": "#00cc66"},
                        {"name": "5% Over", "color": "#ffcc00"},
                        {"name": "10%+ Over", "color": "#ff3300"},
                        {"name": "Under Budget", "color": "#00cc66"}
                    ]
                }
            },
            {
                "name": "Risk Level",
                "type": "drop_down",
                "type_config": {
                    "options": [
                        {"name": "Low", "color": "#00cc66"},
                        {"name": "Medium", "color": "#ffcc00"},
                        {"name": "High", "color": "#ff6600"},
                        {"name": "Critical", "color": "#ff0000"}
                    ]
                }
            },
            {"name": "Last Partner Meeting", "type": "date"},
            {"name": "Next Milestone", "type": "short_text"}
        ]
        
        for field in fields:
            result = self.api.create_custom_field(list_id, field)
            time.sleep(0.2)
            if not result:  # If failed, log and continue
                print(f"      ⚠️  Failed to create field: {field['name']}")

    
    def _add_operations_custom_fields(self, list_id: str):
        """Add custom fields for operations projects"""
        fields = [
            {
                "name": "Asset Value", 
                "type": "currency",
                "type_config": {
                    "default": 0,
                    "precision": 2,
                    "currency_type": "EUR"
                }
            },
            {"name": "Capacity/Size", "type": "short_text"},
            {
                "name": "Revenue MTD", 
                "type": "currency",
                "type_config": {
                    "default": 0,
                    "precision": 2,
                    "currency_type": "EUR"
                }
            },
            {
                "name": "Revenue YTD", 
                "type": "currency",
                "type_config": {
                    "default": 0,
                    "precision": 2,
                    "currency_type": "EUR"
                }
            },
            {"name": "Availability %", "type": "number"},
            {"name": "Last Inspection Date", "type": "date"},
            {"name": "Next Maintenance", "type": "date"},
            {"name": "O&M Partner", "type": "short_text"},
            {
                "name": "Compliance Status",
                "type": "drop_down",
                "type_config": {
                    "options": [
                        {"name": "Compliant", "color": "#00cc66"},
                        {"name": "Minor Issues", "color": "#ffcc00"},
                        {"name": "Critical", "color": "#ff0000"}
                    ]
                }
            },
            {
                "name": "Performance vs Target",
                "type": "drop_down",
                "type_config": {
                    "options": [
                        {"name": "Above Target", "color": "#00cc66"},
                        {"name": "On Target", "color": "#6fddff"},
                        {"name": "Below Target", "color": "#ff6600"}
                    ]
                }
            }
        ]
        
        for field in fields:
            result = self.api.create_custom_field(list_id, field)
            time.sleep(0.2)
            if not result:
                print(f"      ⚠️  Failed to create field: {field['name']}")
            
    
    def _setup_development_statuses(self, list_id: str):
        """Set up statuses for development lists"""
        statuses = [
            {"status": "Not Started", "color": "#d3d3d3", "type": "open"},
            {"status": "In Planning", "color": "#6fddff", "type": "custom"},
            {"status": "Awaiting Partner", "color": "#b973ff", "type": "custom"},
            {"status": "Partner In Progress", "color": "#ffcc00", "type": "custom"},
            {"status": "Review Required", "color": "#ff9900", "type": "custom"},
            {"status": "Completed", "color": "#00cc66", "type": "closed"},
            {"status": "Blocked", "color": "#ff0000", "type": "custom"}
        ]
        self.api.update_list_statuses(list_id, statuses)
    
    def _setup_operations_statuses(self, list_id: str):
        """Set up statuses for operations lists"""
        statuses = [
            {"status": "Scheduled", "color": "#6fddff", "type": "open"},
            {"status": "In Progress", "color": "#ffcc00", "type": "custom"},
            {"status": "Partner Assigned", "color": "#b973ff", "type": "custom"},
            {"status": "Under Review", "color": "#ff9900", "type": "custom"},
            {"status": "Completed", "color": "#00cc66", "type": "closed"},
            {"status": "Issue/Escalated", "color": "#ff0000", "type": "custom"}
        ]
        self.api.update_list_statuses(list_id, statuses)

# ============================================================================
# EXAMPLE PROJECTS CREATOR
# ============================================================================

class ExampleProjectsCreator:
    def __init__(self, api: ClickUpAPI, structure: Dict):
        self.api = api
        self.structure = structure
    
    def create_datacenter_example(self):
        """Create a datacenter under development with realistic tasks"""
        print("\n🏭 Creating Example: Datacenter Under Development...")
        
        # Get the Datacenters Development folder
        folder_data = self.structure["development"]["Datacenters Development"]
        
        # Create tasks across different phases
        self._create_datacenter_prefeasibility(folder_data)
        self._create_datacenter_land_acquisition(folder_data)
        self._create_datacenter_permitting(folder_data)
        self._create_datacenter_engineering(folder_data)
        
        print("   ✓ Datacenter project created with 25+ tasks across 4 phases")
    
    def create_pv_operations_example(self):
        """Create an operating PV park with realistic tasks"""
        print("\n☀️  Creating Example: Operating PV Park...")
        
        # Get the Solar PV Operations folder
        folder_data = self.structure["operations"]["Solar PV Operations"]
        
        # Create tasks across operational areas
        self._create_pv_performance_monitoring(folder_data)
        self._create_pv_maintenance(folder_data)
        self._create_pv_compliance(folder_data)
        
        print("   ✓ PV Operations project created with 20+ tasks across 3 areas")
    
    def _create_datacenter_prefeasibility(self, folder_data: Dict):
        """Prefeasibility tasks for datacenter"""
        list_id = folder_data["lists"]["Prefeasibility & Site Selection"]
        
        # Main project task
        project_task = {
            "name": "DC-Athens-001 Prefeasibility Study",
            "description": "5 MW datacenter facility in Athens industrial zone. Target: Hyperscale cloud clients. Budget: €15M",
            "status": "Partner In Progress",
            "priority": 2,
            "due_date": int((datetime.now() + timedelta(days=14)).timestamp() * 1000)
        }
        
        parent_id = self.api.create_task(list_id, project_task)
        
        # Subtasks with different perspectives
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
        list_id = folder_data["lists"]["Land Acquisition"]
        
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
        list_id = folder_data["lists"]["Permitting & Licensing"]
        
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
        list_id = folder_data["lists"]["Engineering & Design"]
        
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
        list_id = folder_data["lists"]["Performance Monitoring"]
        
        # Main monitoring task
        project_task = {
            "name": "PV-Kozani-05 Performance Monitoring (50 MW)",
            "description": "Operating solar park in Kozani. O&M Partner: Hellenic Solar Services. Monthly target: 7,500 MWh",
            "status": "In Progress",
            "priority": 2
        }
        
        parent_id = self.api.create_task(list_id, project_task)
        
        # Daily/weekly tasks
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
        list_id = folder_data["lists"]["Maintenance Management"]
        
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
        list_id = folder_data["lists"]["Compliance & Reporting"]
        
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
    1. Replace 'YOUR_API_TOKEN' with your ClickUp API token
    2. Replace 'YOUR_TEAM_ID' with your ClickUp Team ID
    3. Run the script: python clickup_setup.py
    """
    
    # Configuration
    from dotenv import load_dotenv
    import os   
    load_dotenv()
    API_TOKEN = os.getenv("CLICKUP_API_TOKEN", "your_token_here") # Get from: https://app.clickup.com/settings/apps
    TEAM_ID = os.getenv("CLICKUP_TEAM_ID", "your_team_id_here") # Get from: https://app.clickup.com/settings/teams

    # Initialize
    config = ClickUpConfig(API_TOKEN, TEAM_ID)
    api = ClickUpAPI(config)
    
    print("=" * 80)
    print("CLICKUP WORKSPACE SETUP FOR ASSET MANAGEMENT COMPANY")
    print("=" * 80)
    
    # Build workspace
    builder = WorkspaceBuilder(api)
    structure = builder.build_complete_workspace()
    
    # Create example projects
    print("\n" + "=" * 80)
    print("CREATING WORKING EXAMPLES")
    print("=" * 80)
    
    examples = ExampleProjectsCreator(api, structure)
    examples.create_datacenter_example()
    examples.create_pv_operations_example()
    
    # Summary
    print("\n" + "=" * 80)
    print("SETUP COMPLETE - SUMMARY")
    print("=" * 80)
    print("\n✅ Created 3 Spaces:")
    print("   - Development Projects (4 folders, 28 lists)")
    print("   - Operations & Maintenance (3 folders, 15 lists)")
    print("   - Corporate & Shared (4 folders, 10 lists)")
    print("\n✅ Configured:")
    print("   - Custom fields for tracking (10+ per project type)")
    print("   - Status workflows (7 statuses for dev, 6 for ops)")
    print("   - Task templates embedded in examples")
    print("\n✅ Created 2 Working Examples:")
    print("   - Datacenter Under Development (25+ tasks)")
    print("   - Operating PV Park (20+ tasks)")
    print("\n📋 Next Steps:")
    print("   1. Log into ClickUp and explore the workspace")
    print("   2. Customize views (Board, Timeline, Table) per role")
    print("   3. Set up automations (via ClickUp UI)")
    print("   4. Import remaining projects using similar patterns")
    print("   5. Invite team members and assign roles")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()