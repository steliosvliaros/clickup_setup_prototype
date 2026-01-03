# Custom Status Setup Guide

ClickUp custom statuses **cannot be created via API** and must be set up manually in the ClickUp UI. This guide provides step-by-step instructions for creating all required statuses.

## 📋 Table of Contents
- [Why Manual Setup?](#why-manual-setup)
- [Development Space Statuses](#development-space-statuses)
- [Operations Space Statuses](#operations-space-statuses)
- [How to Create Statuses](#how-to-create-statuses)
- [Verification](#verification)

---

## Why Manual Setup?

ClickUp's API has limitations:
- ✅ Can read existing statuses
- ❌ Cannot create custom statuses
- ❌ Cannot modify status colors
- ❌ Cannot set status types

Therefore, you must create custom statuses manually in the ClickUp UI **before running the setup script with examples**.

---

## Development Space Statuses

### Status List

| Status Name | Color | Type | Description |
|-------------|-------|------|-------------|
| Not Started | #d3d3d3 (Light Gray) | Open | Initial state for new tasks |
| In Planning | #6fddff (Light Blue) | Custom | Internal planning phase |
| Awaiting Partner | #b973ff (Purple) | Custom | Waiting for partner response/action |
| Partner In Progress | #ffcc00 (Yellow) | Custom | Partner actively working |
| Review Required | #ff9900 (Orange) | Custom | Internal review needed |
| Completed | #00cc66 (Green) | Closed | Task finished |
| Blocked | #ff0000 (Red) | Custom | Task blocked, needs attention |

### Usage Guidelines

- **Not Started**: Default for all new tasks
- **In Planning**: Director/PM is planning the task internally
- **Awaiting Partner**: Task assigned to partner, waiting for them to start
- **Partner In Progress**: Partner has confirmed they're working on it
- **Review Required**: Partner completed work, needs internal review before marking complete
- **Completed**: Fully done, reviewed, and approved
- **Blocked**: Something is preventing progress - must document blocker in description

---

## Operations Space Statuses

### Status List

| Status Name | Color | Type | Description |
|-------------|-------|------|-------------|
| Scheduled | #6fddff (Light Blue) | Open | Planned for future |
| In Progress | #ffcc00 (Yellow) | Custom | Currently being executed |
| Partner Assigned | #b973ff (Purple) | Custom | Assigned to O&M partner |
| Under Review | #ff9900 (Orange) | Custom | Reviewing results/reports |
| Completed | #00cc66 (Green) | Closed | Task finished |
| Issue/Escalated | #ff0000 (Red) | Custom | Critical issue requiring escalation |

### Usage Guidelines

- **Scheduled**: Maintenance or monitoring task planned for specific date
- **In Progress**: Task actively being executed by internal team or contractor
- **Partner Assigned**: O&M partner has been assigned and notified
- **Under Review**: Reviewing partner's work, reports, or results
- **Completed**: Task fully completed with documentation
- **Issue/Escalated**: Critical operational issue requiring immediate attention

---

## How to Create Statuses

### Step-by-Step Instructions

#### 1. Navigate to Your Space
- Open ClickUp
- Go to the Space where you want to add statuses
- For example: "Development Projects" or "Operations & Maintenance"

#### 2. Open Any List
- Click on any List within the Space
- You only need to do this once per Space (statuses are space-level)

#### 3. Access Status Settings
- Look for the current status column (usually says "To Do", "In Progress", "Complete")
- Click the status dropdown
- Click **"+ Add Status"** at the bottom

#### 4. Create Each Status

For each status in the tables above:

1. **Click "+ Add Status"**
2. **Enter Status Name** (exactly as shown in tables)
3. **Choose Color**:
   - Click the color picker
   - Enter the hex code (e.g., #6fddff)
   - Or choose visually to match
4. **Select Status Type**:
   - **Open**: For initial/starting statuses
   - **Custom**: For in-progress or intermediate statuses
   - **Closed**: For final completion statuses
5. **Click Save**

#### 5. Repeat for All Statuses
- Create all statuses for the Space
- Ensure names match exactly (script is case-insensitive, but exact names are best)

#### 6. Move to Next Space
- Repeat steps 1-5 for each Space
- Development Projects Space
- Operations & Maintenance Space
- Corporate & Shared Space (if you want custom statuses there)

---

## Detailed Setup by Space

### Development Projects Space

```
1. Not Started (Light Gray #d3d3d3) - Type: Open
   └─ Create this status
   └─ Set as Open type
   └─ Use light gray color

2. In Planning (Light Blue #6fddff) - Type: Custom
   └─ Create this status
   └─ Set as Custom type
   └─ Use light blue color

3. Awaiting Partner (Purple #b973ff) - Type: Custom
   └─ Create this status
   └─ Set as Custom type
   └─ Use purple color

4. Partner In Progress (Yellow #ffcc00) - Type: Custom
   └─ Create this status
   └─ Set as Custom type
   └─ Use yellow color

5. Review Required (Orange #ff9900) - Type: Custom
   └─ Create this status
   └─ Set as Custom type
   └─ Use orange color

6. Completed (Green #00cc66) - Type: Closed
   └─ Create this status
   └─ Set as Closed type
   └─ Use green color

7. Blocked (Red #ff0000) - Type: Custom
   └─ Create this status
   └─ Set as Custom type
   └─ Use red color
```

### Operations & Maintenance Space

```
1. Scheduled (Light Blue #6fddff) - Type: Open
   └─ Create this status
   └─ Set as Open type
   └─ Use light blue color

2. In Progress (Yellow #ffcc00) - Type: Custom
   └─ Create this status
   └─ Set as Custom type
   └─ Use yellow color

3. Partner Assigned (Purple #b973ff) - Type: Custom
   └─ Create this status
   └─ Set as Custom type
   └─ Use purple color

4. Under Review (Orange #ff9900) - Type: Custom
   └─ Create this status
   └─ Set as Custom type
   └─ Use orange color

5. Completed (Green #00cc66) - Type: Closed
   └─ Create this status
   └─ Set as Closed type
   └─ Use green color

6. Issue/Escalated (Red #ff0000) - Type: Custom
   └─ Create this status
   └─ Set as Custom type
   └─ Use red color
```

---

## Verification

### After Creating Statuses

1. **Visual Check**:
   - Open a List in the Space
   - Click the status dropdown
   - Verify all statuses appear with correct colors

2. **Test a Task**:
   - Create a test task
   - Try moving it through all statuses
   - Ensure all statuses are available

3. **Run the Setup Script**:
   ```powershell
   python .\src\clickup_python_setup.py
   ```
   - Script will verify statuses exist
   - If successful, examples will be created
   - If statuses are missing, script will list them

### Verification Output

**Success**:
```
✓ All required statuses exist
✅ All custom statuses verified! Proceeding with example creation...
```

**Failure**:
```
⚠️ WARNING: Custom statuses cannot be created via API!
Missing statuses: In Planning, Awaiting Partner, Partner In Progress
Please create these statuses manually in ClickUp UI before running examples.
```

---

## Troubleshooting

### "Statuses not verified" error

**Problem**: Script reports missing statuses even though you created them

**Solutions**:
1. Check spelling - status names must match exactly
2. Ensure you created statuses in the correct Space
3. Try refreshing ClickUp
4. Verify status type (Open/Custom/Closed) matches
5. Re-run the script

### Can't find status dropdown

**Problem**: Can't locate where to add statuses

**Solutions**:
1. Make sure you're in a List (not Space or Folder view)
2. Look for the status column in Board or List view
3. Try switching to Board view where statuses are more visible

### Status colors don't match

**Problem**: Colors look different than expected

**Solution**:
- Colors are cosmetic and don't affect script functionality
- Use hex codes for exact matching
- Visual approximation is acceptable

### Too many default statuses

**Problem**: ClickUp has default statuses you don't need

**Solution**:
- You can archive or hide unused default statuses
- Click status dropdown → Settings → Archive status
- Custom statuses will coexist with defaults

---

## Status Workflow Examples

### Development Project Workflow

```
New Task
   ↓
Not Started → In Planning
   ↓               ↓
   ↓         Awaiting Partner
   ↓               ↓
   ↓         Partner In Progress
   ↓               ↓
   ↓         Review Required
   ↓               ↓
   └───────────→ Completed

Blocked ← (Can happen from any status)
```

### Operations Workflow

```
New Maintenance Task
   ↓
Scheduled → In Progress
   ↓            ↓
   ↓        Partner Assigned
   ↓            ↓
   ↓        Under Review
   ↓            ↓
   └────────→ Completed

Issue/Escalated ← (Critical issues from any status)
```

---

## Best Practices

1. **Create All at Once**: Set up all statuses for a Space in one session
2. **Follow Color Coding**: Colors help team quickly identify task states
3. **Consistent Naming**: Use exact names from config.yaml
4. **Document Changes**: If you modify statuses, update config.yaml too
5. **Train Team**: Ensure team understands status meanings and workflow

---

## Color Reference

### Quick Color Guide

| Color | Hex Code | Usage |
|-------|----------|-------|
| Light Gray | #d3d3d3 | Not Started |
| Light Blue | #6fddff | Planning/Scheduled |
| Purple | #b973ff | Partner-related |
| Yellow | #ffcc00 | In Progress |
| Orange | #ff9900 | Review |
| Green | #00cc66 | Completed |
| Red | #ff0000 | Blocked/Issues |

### Color Psychology

- **Gray**: Neutral, waiting to start
- **Blue**: Planning, thinking, preparing
- **Purple**: External dependency (partners)
- **Yellow**: Active work happening
- **Orange**: Attention needed (review)
- **Green**: Success, completion
- **Red**: Stop, problem, urgent attention

---

## Next Steps

After creating all statuses:

1. ✅ Run the setup script: `python .\src\clickup_python_setup.py`
2. ✅ Verify examples are created successfully
3. ✅ Set up automations (see AUTOMATIONS_GUIDE.md)
4. ✅ Create custom views
5. ✅ Invite team members
6. ✅ Train team on status meanings and workflow

---

**Last Updated**: January 2026  
**Reference**: config.yaml statuses section  
**Support**: Check README.md for additional help
