# ClickUp Workspace Setup - Asset Management & Development Company

Complete ClickUp workspace automation for asset management companies managing development projects and operational assets across multiple sectors (Solar PV, Datacenters, Hotels, Hydroponic Farms, Wind Farms).

## 🎯 Features

- **Automated Workspace Creation**: Build complete space/folder/list hierarchy from YAML config
- **Custom Fields**: Automatically applied based on space type (development vs operations)
- **Status Workflows**: Pre-configured status workflows with verification
- **Views Configuration**: Pre-defined views for directors, PMs, and partners
- **Automation Guide**: Documented automations (must be created manually in ClickUp UI)
- **Working Examples**: Realistic projects with 45+ tasks demonstrating best practices

## 📂 Project Structure

```
clickup_setup_prototype/
├── config.yaml                  # Complete workspace configuration
├── .env                         # API credentials (create from .env.example)
├── environment.yml              # Conda environment
├── README.md                    # This file
├── src/
│   └── clickup_python_setup.py  # Main setup script
├── scripts/
│   ├── activate_env.ps1         # Quick activation script
│   └── init_project.ps1         # Project initialization
└── notebooks/
    └── clickup_python_setup.ipynb  # Interactive notebook version
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10+
- ClickUp account with API access
- ClickUp API token and Team ID

### 2. Get ClickUp Credentials

1. **API Token**: Go to https://app.clickup.com/settings/apps → Generate API Token
2. **Team ID**: Go to https://app.clickup.com/settings/teams → Copy Team ID

### 3. Setup Environment

**Windows / PowerShell:**

```powershell
# Create conda environment
conda env create -f environment.yml

# Activate environment
conda activate clickup-prototype

# Or use the shortcut script
.\scripts\activate_env.ps1
```

### 4. Configure Credentials

Create a `.env` file in the root directory:

```env
CLICKUP_API_TOKEN=pk_your_token_here
CLICKUP_TEAM_ID=your_team_id_here
```

### 5. Run Setup

```powershell
python .\src\clickup_python_setup.py
```

## ⚙️ Configuration (config.yaml)

All workspace configuration is defined in `config.yaml`:

### Workspace Structure

```yaml
spaces:
  - name: "Development Projects"
    key: "development"
    folders:
      - name: "Solar PV Development"
        lists:
          - "Prefeasibility & Site Selection"
          - "Land Acquisition"
          # ... more lists
```

### Custom Fields

```yaml
custom_fields:
  development:
    - name: "Project Value"
      type: "currency"
      type_config:
        currency_type: "EUR"
    # ... more fields
```

### Status Workflows

```yaml
statuses:
  development:
    - name: "In Planning"
      color: "#6fddff"
      type: "custom"
    # ... more statuses
```

**⚠️ IMPORTANT**: Custom statuses **CANNOT** be created via API. You must create them manually in ClickUp UI.

### Views

```yaml
views:
  development:
    - name: "Director Dashboard"
      type: "board"
      grouping: "status"
      filters:
        priority: [1, 2]
    # ... more views
```

### Automations

```yaml
automations:
  development:
    - name: "Auto-notify on status change to Blocked"
      trigger:
        type: "status_updated"
        status: "Blocked"
      action:
        type: "post_comment"
        comment: "⚠️ Task is blocked!"
    # ... more automations
```

**⚠️ IMPORTANT**: Automations must be created manually in ClickUp UI. The script provides setup instructions.

### Example Projects

```yaml
examples:
  datacenter:
    enabled: true
    name: "DC-Athens-001"
    folder: "Datacenters Development"
    custom_field_values:
      "Project Value": 15000000
      # ... more values
```

## 📋 Workflow

The script follows this workflow:

1. **Create Spaces** → Creates all spaces defined in config
2. **Create Folders & Lists** → Builds hierarchy within each space
3. **Apply Custom Fields** → Adds fields based on space type
4. **Verify Statuses** → Checks if custom statuses exist (NOT created by API)
5. **Create Views** → Attempts to create views (may require manual creation)
6. **Document Automations** → Provides setup guide for manual creation
7. **Create Examples** → Only if statuses are verified
   - Datacenter Development Project (25+ tasks)
   - PV Operations Project (20+ tasks)

## ⚠️ Important Limitations

### Custom Statuses
- **Cannot be created via API**
- Must be created manually in ClickUp UI
- Script will verify if statuses exist
- Examples will NOT be created if statuses are missing

**To Create Custom Statuses:**
1. Go to ClickUp workspace
2. Navigate to each Space
3. Open any List
4. Click status dropdown → "+ Add Status"
5. Create statuses from `config.yaml`
6. Re-run script to create examples

### Automations
- **Cannot be created via API**
- Must be set up manually in ClickUp UI
- Script provides detailed setup instructions
- Refer to `config.yaml` for automation specifications

### Views
- Limited API support for views
- Some views may need manual creation
- Script provides configuration guide

## 🎯 Use Cases

### Development Projects Space
- **Use Case**: Track development projects across multiple sectors
- **Users**: Directors, Project Managers, Partners
- **Features**:
  - Budget tracking and risk management
  - Partner coordination workflows
  - Milestone and COD tracking
  - Multi-stage development pipeline

### Operations & Maintenance Space
- **Use Case**: Manage operational assets and O&M activities
- **Users**: Operations Directors, O&M Managers, Contractors
- **Features**:
  - Performance monitoring and revenue tracking
  - Maintenance scheduling
  - Compliance management
  - Issue escalation workflows

## 📊 Example Projects

### Datacenter Development (DC-Athens-001)
- **Phases**: Prefeasibility, Land Acquisition, Permitting, Engineering
- **Tasks**: 25+ realistic tasks with subtasks
- **Features**: Partner coordination, document tracking, milestone management

### PV Operations (PV-Kozani-05)
- **Areas**: Performance Monitoring, Maintenance, Compliance
- **Tasks**: 20+ operational tasks
- **Features**: Daily monitoring, partner tracking, issue escalation

## 🔧 Customization

### Adding a New Space

1. Edit `config.yaml`:

```yaml
spaces:
  - name: "New Space"
    key: "new_space"
    folders:
      - name: "New Folder"
        lists:
          - "List 1"
```

2. Add custom fields:

```yaml
custom_fields:
  new_space:
    - name: "Custom Field"
      type: "short_text"
```

3. Define statuses:

```yaml
statuses:
  new_space:
    - name: "Custom Status"
      color: "#00cc66"
      type: "custom"
```

4. Re-run script

### Modifying Existing Structure

- Edit `config.yaml`
- Re-run script
- New items will be created; existing items won't be duplicated

## 🐛 Troubleshooting

### "Custom statuses not verified"
- Create statuses manually in ClickUp UI
- Ensure status names match exactly (case-insensitive)
- Re-run script

### "Failed to create custom field"
- Check field type and configuration
- Verify list exists
- Check API rate limits

### Rate Limiting
- Script includes automatic rate limiting (0.5s between requests)
- If you hit 429 errors, script waits 60 seconds automatically

### API Errors
- Verify API token and Team ID in `.env`
- Check network connectivity
- Ensure sufficient API permissions

## 📚 Additional Resources

- [ClickUp API Documentation](https://clickup.com/api)
- [ClickUp Automations Guide](https://docs.clickup.com/en/articles/856285-intro-to-automations)
- [ClickUp Custom Fields](https://docs.clickup.com/en/articles/852456-custom-fields)

## 🔄 Updates and Maintenance

To update the workspace:
1. Modify `config.yaml`
2. Re-run setup script
3. New elements will be created
4. Existing elements remain unchanged

## 📝 License

This is a prototype/template for internal use. Modify as needed for your organization.

## 🤝 Support

For issues or questions:
1. Check `config.yaml` configuration
2. Review ClickUp API documentation
3. Verify manual setup requirements (statuses, automations)

---

**Last Updated**: January 2026  
**Version**: 2.0 - Full Configuration Management

