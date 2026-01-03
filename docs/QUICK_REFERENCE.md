# Quick Reference Guide

## 🚀 Quick Start

```powershell
# 1. Setup environment
conda activate clickup-prototype

# 2. Configure credentials (one time)
cp .env.example .env
# Edit .env with your API token and Team ID

# 3. Run setup
python .\src\clickup_python_setup.py

# 4. Create statuses manually (see docs/STATUS_SETUP_GUIDE.md)
# 5. Re-run script to create examples
```

## 📋 Status Quick Reference

### Development Space (7 Statuses)

| Status | Color | Type | When to Use |
|--------|-------|------|-------------|
| Not Started | Gray | Open | New tasks |
| In Planning | Blue | Custom | Internal planning |
| Awaiting Partner | Purple | Custom | Waiting for partner |
| Partner In Progress | Yellow | Custom | Partner working |
| Review Required | Orange | Custom | Need internal review |
| Completed | Green | Closed | Done |
| Blocked | Red | Custom | Blocked |

### Operations Space (6 Statuses)

| Status | Color | Type | When to Use |
|--------|-------|------|-------------|
| Scheduled | Blue | Open | Future planned tasks |
| In Progress | Yellow | Custom | Currently executing |
| Partner Assigned | Purple | Custom | Assigned to O&M partner |
| Under Review | Orange | Custom | Reviewing results |
| Completed | Green | Closed | Done |
| Issue/Escalated | Red | Custom | Critical issue |

## 🤖 Automation Quick Reference

### Development (4 Automations)

1. **Blocked Alert**: Status → Blocked → Post comment warning
2. **Overdue Alert**: Overdue + High Priority → Post comment
3. **Review After Partner**: Partner In Progress → Completed → Change to Review Required
4. **Partner Wait**: Status → Awaiting Partner → Post tracking reminder

### Operations (4 Automations)

1. **Critical Issues**: Status → Issue/Escalated → Post urgent alert
2. **Maintenance Reminder**: 3 days before due + Maintenance list → Post reminder
3. **Completion Reminder**: Status → Completed → Post documentation reminder
4. **Partner Tracking**: Status → Partner Assigned → Post tracking reminder

## 📊 View Quick Reference

### Development Views (5 Total)

1. **Director Dashboard**: Board by status, high priority only
2. **Partner Timeline**: Timeline grouped by partner, partner statuses only
3. **Budget Overview**: Table grouped by budget status
4. **Risk Management**: Board by risk level
5. **Active Projects**: Gantt timeline with dependencies

### Operations Views (5 Total)

1. **Daily Operations**: Board by status, all priorities
2. **Partner Performance**: Table grouped by O&M partner
3. **Maintenance Calendar**: Calendar view of maintenance schedule
4. **Revenue Tracking**: Table with financial metrics
5. **Issues & Escalations**: List of urgent issues only

## 🎯 Custom Fields Quick Reference

### Development Fields (10)

- Project Value (Currency EUR)
- Capacity/Size (Text)
- Development Stage (Dropdown: 7 options)
- Expected COD (Date)
- Location (Text)
- Lead Partner (Text)
- Budget Status (Dropdown: 4 options)
- Risk Level (Dropdown: 4 options)
- Last Partner Meeting (Date)
- Next Milestone (Text)

### Operations Fields (10)

- Asset Value (Currency EUR)
- Capacity/Size (Text)
- Revenue MTD (Currency EUR)
- Revenue YTD (Currency EUR)
- Availability % (Number)
- Last Inspection Date (Date)
- Next Maintenance (Date)
- O&M Partner (Text)
- Compliance Status (Dropdown: 3 options)
- Performance vs Target (Dropdown: 3 options)

## 📁 Workspace Structure

```
Development Projects
├── Solar PV Development (7 lists)
├── Datacenters Development (7 lists)
├── Hotels Development (7 lists)
└── Hydroponic Farms Development (7 lists)

Operations & Maintenance
├── Solar PV Operations (5 lists)
├── Wind Farms Operations (5 lists)
└── Hotels Operations (5 lists)

Corporate & Shared
├── Financial Management (3 lists)
├── HR & Administration (3 lists)
├── Partner Management (3 lists)
└── Strategic Initiatives (2 lists)
```

## 🔗 File Locations

| What | Where |
|------|-------|
| All configuration | `config.yaml` |
| Main script | `src/clickup_python_setup.py` |
| Full documentation | `README.md` |
| Status setup guide | `docs/STATUS_SETUP_GUIDE.md` |
| Automation guide | `docs/AUTOMATIONS_GUIDE.md` |
| Setup summary | `docs/SETUP_COMPLETE.md` |
| Credentials | `.env` (create from `.env.example`) |

## ⚠️ Must Do Manually

1. **Create Custom Statuses** (Required for examples)
   - Development: 7 statuses
   - Operations: 6 statuses
   - See: docs/STATUS_SETUP_GUIDE.md

2. **Create Automations** (Optional)
   - 8 total automations
   - See: docs/AUTOMATIONS_GUIDE.md

3. **Verify/Customize Views** (Optional)
   - 10 pre-configured views
   - May need manual adjustment

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| "Statuses not verified" | Create statuses manually (see guide) |
| "Failed to create field" | Check field config in config.yaml |
| API rate limit | Script handles automatically (waits 60s) |
| "Failed to create view" | Create manually in ClickUp UI |
| Missing credentials | Create .env from .env.example |

## 💡 Tips

- **Always run from project root**: `python .\src\clickup_python_setup.py`
- **Check config.yaml first**: All settings are there
- **Create statuses before examples**: Examples need custom statuses
- **Test automations**: Use test tasks before going live
- **Update config**: Keep config.yaml synced with ClickUp changes

## 📞 Help & Documentation

- **Overview**: README.md
- **Status Setup**: docs/STATUS_SETUP_GUIDE.md
- **Automation Setup**: docs/AUTOMATIONS_GUIDE.md
- **Complete Summary**: docs/SETUP_COMPLETE.md
- **ClickUp API**: https://clickup.com/api

## 🎓 Workflow Summary

```
1. Configure .env
   ↓
2. Run python script
   ↓
3. Workspace created (spaces, folders, lists, fields)
   ↓
4. Check if statuses exist
   ↓
   ├─ Yes → Create examples (45+ tasks)
   └─ No → Show instructions → Create manually → Re-run
      ↓
5. Setup automations (manual, see guide)
   ↓
6. Customize views (verify/adjust)
   ↓
7. Invite team & start using!
```

## 🎯 Success Checklist

- [ ] Environment activated
- [ ] .env configured with credentials
- [ ] Script runs successfully
- [ ] All spaces/folders/lists created
- [ ] Custom fields visible
- [ ] Custom statuses created (manual)
- [ ] Examples created (if statuses OK)
- [ ] Automations set up (manual)
- [ ] Views verified
- [ ] Team invited
- [ ] Documentation reviewed

---

**Quick Start**: `conda activate clickup-prototype && python .\src\clickup_python_setup.py`

**Need Help?**: Check README.md or docs/ folder
