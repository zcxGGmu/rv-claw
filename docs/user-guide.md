# RV-Claw User Guide

## Getting Started

### Login

1. Navigate to `http://localhost`
2. Use default admin credentials (change immediately):
   - Username: `admin`
   - Password: `admin123`
3. Update password in User Settings

## Chat Mode

### Starting a Chat

1. Click "New Chat" in the left sidebar
2. Type your question about RISC-V
3. The AI will respond with relevant information

### Available Tools

- **Search**: Find information in documentation
- **Files**: Browse and analyze code files
- **Terminal**: Execute commands (if enabled)
- **Browser**: Web navigation (if enabled)

## Pipeline Mode

### Creating a Case

1. Click "Cases" in the left sidebar
2. Click "Create Case" button
3. Enter:
   - Target Repository (e.g., `linux-riscv`)
   - Input Context (describe the contribution goal)
4. Click "Create"

### Pipeline Stages

1. **Explore**: AI scans for contribution opportunities
2. **Plan**: AI designs implementation strategy
3. **Develop**: AI generates code changes
4. **Review**: AI reviews code quality
5. **Test**: AI validates with QEMU

At each Human Gate, review the AI output and:
- **Approve**: Continue to next stage
- **Request Changes**: Provide feedback
- **Reject**: Abandon the case

### Monitoring Progress

- Real-time updates via SSE (Server-Sent Events)
- Event log shows all agent actions
- Review findings display in right panel

### Submitting Review

When Human Gate appears:
1. Review the artifacts (code, plan, test results)
2. Enter your decision and optional notes
3. Click Submit

## Best Practices

### For Chat Mode

- Be specific in questions
- Reference specific files or functions
- Use code blocks for clarity

### For Pipeline Mode

- Start with clear input context
- Review each stage carefully
- Don't approve if unsure
- Use iteration limits wisely

### Cost Management

- Each case consumes API tokens
- Review iterations add cost
- Set daily budget limits
- Monitor cost dashboard

## Troubleshooting

### SSE Connection Lost

- Page auto-reconnects
- Check network connection
- Refresh if needed

### Pipeline Stuck

- Check case status
- Contact admin if >30 min
- Review event log for errors

### Cannot Create Case

- Verify login status
- Check user permissions
- Contact admin for quota increase

## FAQ

**Q: Can I run multiple cases simultaneously?**
A: Yes, up to your user quota (default: 5 concurrent).

**Q: How long does a case take?**
A: 10-30 minutes depending on complexity and review rounds.

**Q: Can I edit AI-generated code?**
A: Yes, download patches and modify before submission.

**Q: Is my data secure?**
A: All data stored locally. API keys encrypted at rest.

## Support

Email: support@example.com
Docs: https://docs.rv-claw.io
Issues: https://github.com/org/rv-claw/issues
