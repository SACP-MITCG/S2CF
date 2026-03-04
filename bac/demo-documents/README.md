# BAC Demo Documents

These documents simulate realistic business analysis artifacts for demonstrating the BAC (Business Analysis Copilot) workflow.

## Available Documents

| File | Type | Expected Template |
|------|------|-------------------|
| `CSRD_Carbon_Footprint_Requirements.md` | Regulatory compliance | `regulatory_change` |
| `Order_to_Cash_Process_Improvement.md` | Process optimization | `process_improvement` |
| `Customer_360_Platform_Proposal.md` | New capability | `new_capability` |
| `ERP_CRM_Integration_Requirements.md` | System integration | `integration` |

## Demo Workflow

### 1. Start BAC
```bash
docker compose up
```
Open http://localhost:5001

### 2. Upload Document
Drag any document from this folder into the upload zone, or use the API:
```bash
curl -X POST http://localhost:5001/api/upload \
  -F "file=@demo-documents/CSRD_Carbon_Footprint_Requirements.md"
```

### 3. Create Use Case with Template
The AI will suggest the appropriate template based on document content.

### 4. Edit Sections
- Modify auto-generated section content
- Link to HOPEX architecture elements
- Add BAM references

### 5. Export
- **Markdown**: For documentation/wikis
- **Word**: For formal documents
- **IRM JSON-LD**: For SAC handover

## API Quick Reference

```bash
# List use cases
curl http://localhost:5001/api/usecases/

# Create use case
curl -X POST http://localhost:5001/api/usecases \
  -H "Content-Type: application/json" \
  -d '{"title": "Carbon Tracking", "templateId": "regulatory_change"}'

# Get HOPEX capabilities
curl http://localhost:5001/api/hopex/capabilities

# Export to Markdown
curl http://localhost:5001/api/export/markdown/{use_case_id}

# Export to IRM JSON-LD
curl http://localhost:5001/api/export/irm/{use_case_id}
```

## Notes

- **AI Features**: Require `OPENAI_API_KEY` in `.env`
- **HOPEX**: Falls back to mock data without credentials
- **Persistence**: Data is in-memory only (lost on restart)
