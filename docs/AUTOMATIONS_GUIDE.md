# ClickUp Automations Setup Guide

This guide provides step-by-step instructions for creating all automations defined in `config.yaml`. Automations cannot be created via API and must be set up manually in the ClickUp UI.

## 📋 Table of Contents
- [Development Space Automations](#development-space-automations)
- [Operations Space Automations](#operations-space-automations)
- [How to Create Automations](#how-to-create-automations)

---

## Development Space Automations

### 1. Auto-notify on status change to Blocked

**Purpose**: Alert team when a task becomes blocked

**Setup Steps**:
1. Go to Development Projects Space
2. Click "Automate" button
3. Choose "When status changes"
4. Set trigger: Status changes to "Blocked"
5. Choose action: "Post comment"
6. Comment text: `⚠️ Task is blocked! Please review and add blocker details in the description.`
7. Save automation

**Expected Behavior**:
- Triggers when any task is moved to "Blocked" status
- Posts a comment to remind team to document the blocker
- Helps maintain visibility of blockers

---

### 2. Auto-notify on high priority overdue

**Purpose**: Escalate overdue high-priority tasks

**Setup Steps**:
1. Go to Development Projects Space
2. Click "Automate" button
3. Choose "When due date passes"
4. Add condition: Priority is "Urgent" OR Priority is "High"
5. Choose action: "Post comment"
6. Comment text: `🚨 High priority task is overdue! Please update status or extend deadline.`
7. Save automation

**Expected Behavior**:
- Triggers when high-priority tasks become overdue
- Posts alert comment
- Helps prevent critical delays

---

### 3. Auto-move to Review when Partner In Progress completed

**Purpose**: Ensure internal review after partner completes work

**Setup Steps**:
1. Go to Development Projects Space
2. Click "Automate" button
3. Choose "When status changes"
4. Set trigger: Status changes from "Partner In Progress" to "Completed"
5. Choose action: "Change status"
6. New status: "Review Required"
7. Save automation

**Expected Behavior**:
- Intercepts tasks marked complete by partners
- Moves them to Review Required instead
- Ensures director/PM review before final completion

---

### 4. Notify when task moves to Awaiting Partner

**Purpose**: Remind team to notify partner and track response

**Setup Steps**:
1. Go to Development Projects Space
2. Click "Automate" button
3. Choose "When status changes"
4. Set trigger: Status changes to "Awaiting Partner"
5. Choose action: "Post comment"
6. Comment text: `📧 Waiting for partner action. Please ensure partner is notified and track response time.`
7. Save automation

**Expected Behavior**:
- Triggers when task requires partner action
- Reminds PM to contact partner
- Helps track partner response times

---

## Operations Space Automations

### 5. Escalate critical issues

**Purpose**: Flag critical operational issues requiring immediate attention

**Setup Steps**:
1. Go to Operations & Maintenance Space
2. Click "Automate" button
3. Choose "When status changes"
4. Set trigger: Status changes to "Issue/Escalated"
5. Choose action: "Post comment"
6. Comment text: `🔴 CRITICAL: Issue escalated! Immediate attention required. Update every 4 hours.`
7. Optional: Add action "Send email notification" to directors
8. Save automation

**Expected Behavior**:
- Triggers on critical operational issues
- Posts urgent notification
- Sets expectation for 4-hour updates
- (Optional) Emails directors immediately

---

### 6. Remind for maintenance tasks

**Purpose**: Ensure maintenance tasks are prepared in advance

**Setup Steps**:
1. Go to Operations & Maintenance Space
2. Click "Automate" button
3. Choose "When due date is approaching"
4. Set: 3 days before due date
5. Add condition: List name contains "Maintenance"
6. Choose action: "Post comment"
7. Comment text: `⏰ Maintenance task due in 3 days. Ensure contractor is scheduled and materials are available.`
8. Save automation

**Expected Behavior**:
- Triggers 3 days before maintenance due date
- Posts preparation reminder
- Helps prevent last-minute scheduling issues

---

### 7. Auto-comment on completion

**Purpose**: Remind team to document completed work

**Setup Steps**:
1. Go to Operations & Maintenance Space
2. Click "Automate" button
3. Choose "When status changes"
4. Set trigger: Status changes to "Completed"
5. Choose action: "Post comment"
6. Comment text: `✅ Task completed. Please update custom fields with final data and attach documentation.`
7. Save automation

**Expected Behavior**:
- Triggers when task is completed
- Reminds to update all final data
- Ensures proper documentation

---

### 8. Partner assignment notification

**Purpose**: Track when tasks are assigned to O&M partners

**Setup Steps**:
1. Go to Operations & Maintenance Space
2. Click "Automate" button
3. Choose "When status changes"
4. Set trigger: Status changes to "Partner Assigned"
5. Choose action: "Post comment"
6. Comment text: `👥 Assigned to partner. Track progress and set follow-up reminder.`
7. Optional: Add action "Create subtask" named "Follow up with partner"
8. Save automation

**Expected Behavior**:
- Triggers when work is assigned to partner
- Posts tracking reminder
- (Optional) Creates follow-up subtask

---

## How to Create Automations

### General Steps

1. **Navigate to Space**
   - Open the Space where you want to add automation
   - Click the "Automate" button (top right)

2. **Choose Trigger**
   - Status changes
   - Due date changes
   - Field updates
   - Task created
   - Etc.

3. **Add Conditions (Optional)**
   - Filter by priority
   - Filter by list
   - Filter by custom field values
   - Multiple conditions can be combined

4. **Choose Actions**
   - Post comment
   - Change status
   - Update field
   - Send notification
   - Create subtask
   - Move to list
   - Assign to user

5. **Test and Save**
   - Click "Test" to verify behavior
   - Save automation
   - Enable/disable as needed

### Tips

- **Start Simple**: Create basic automations first, then enhance
- **Test Thoroughly**: Use test tasks to verify automation behavior
- **Monitor Performance**: Check if automations are triggering correctly
- **Document Changes**: Keep track of automation modifications
- **Review Regularly**: Assess if automations are providing value

### Troubleshooting

**Automation not triggering**:
- Check conditions are met
- Verify status names match exactly
- Ensure automation is enabled
- Check for conflicting automations

**Too many notifications**:
- Add more specific conditions
- Reduce trigger frequency
- Consider combining multiple automations

**Wrong action taken**:
- Review automation logic
- Check action configuration
- Verify field mappings

---

## Advanced Automation Ideas

### For Development Projects:

1. **Budget Alert**: When "Budget Status" changes to "10%+ Over", notify director and change priority to Urgent
2. **Risk Escalation**: When "Risk Level" is "Critical", automatically assign to director and post to dedicated Slack channel
3. **Milestone Tracking**: When "Development Stage" changes, update "Next Milestone" custom field automatically
4. **Partner Meeting Reminder**: 7 days after "Last Partner Meeting", create reminder task

### For Operations:

1. **Revenue Alert**: When "Revenue MTD" is below target (custom calculation), notify director
2. **Performance Warning**: When "Performance vs Target" is "Below Target" for 3 consecutive days, escalate to Issue status
3. **Compliance Deadline**: 30 days before annual compliance due, create checklist of required documents
4. **Availability Alert**: When "Availability %" drops below 95%, create urgent maintenance task

---

## Automation Templates

### Template: Status Change Notification
```
Trigger: When status changes to [STATUS_NAME]
Action: Post comment "[ICON] [MESSAGE]"
Optional: Send email notification to [USER/GROUP]
```

### Template: Due Date Reminder
```
Trigger: [X] days before due date
Condition: [FIELD] is [VALUE]
Action: Post comment "[REMINDER_MESSAGE]"
Optional: Change priority to [PRIORITY]
```

### Template: Field Update Cascade
```
Trigger: When [FIELD_1] changes to [VALUE]
Action: Update [FIELD_2] to [NEW_VALUE]
Action: Change status to [STATUS]
Action: Post comment "[EXPLANATION]"
```

---

## Best Practices

1. **Keep it Simple**: Start with essential automations, add complexity gradually
2. **Clear Naming**: Use descriptive names so team understands automation purpose
3. **Avoid Loops**: Be careful with automations that trigger other automations
4. **Regular Review**: Quarterly review of automation effectiveness
5. **Team Training**: Ensure team understands automation behavior
6. **Document Everything**: Maintain this guide as automations change

---

## Maintenance Schedule

- **Weekly**: Check automation logs for errors
- **Monthly**: Review automation trigger frequency and effectiveness
- **Quarterly**: Assess if automations still meet business needs
- **Annually**: Comprehensive audit of all automations

---

**Last Updated**: January 2026  
**Maintained by**: Project Team  
**Reference**: config.yaml automations section
