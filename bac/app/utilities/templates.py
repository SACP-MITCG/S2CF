"""
BAC - Blueprint Templates
Pre-defined templates for Use Case Descriptions
"""
from ..models.irm import UseCaseDescription, SectionType


# Template definitions
TEMPLATES = {
    "regulatory_change": {
        "id": "regulatory_change",
        "name": "Regulatory Change",
        "description": "Template for use cases driven by regulatory requirements",
        "sections": [
            {"type": SectionType.OVERVIEW, "title": "Overview", "content": "## Business Context\n\n_Describe the regulatory driver and business impact_\n\n## Scope\n\n_Define what is in and out of scope_"},
            {"type": SectionType.OBJECTIVES, "title": "Objectives", "content": "## SMART Objectives\n\n### Objective 1\n- **Specific**: _What exactly needs to be achieved?_\n- **Measurable**: _How will success be measured?_\n- **Achievable**: _Is this realistic?_\n- **Relevant**: _Why does this matter?_\n- **Time-bound**: _By when?_"},
            {"type": SectionType.CONTEXT, "title": "Regulatory Context", "content": "## Regulation Details\n\n_Reference the specific regulation(s)_\n\n## Compliance Requirements\n\n_List specific requirements to address_\n\n## Penalties/Risks for Non-Compliance\n\n_What happens if we don't comply?_"},
            {"type": SectionType.USER_JOURNEYS, "title": "Affected User Journeys", "content": "## Journey 1: [Name]\n\n**Actor**: _Who is performing this journey?_\n\n**Steps**:\n1. _Step 1_\n2. _Step 2_\n\n**Changes Required**: _What changes to comply?_"},
            {"type": SectionType.ASSUMPTIONS, "title": "Assumptions & Constraints", "content": "## Assumptions\n\n- _Assumption 1_\n\n## Constraints\n\n- _Constraint 1_\n\n## Dependencies\n\n- _Dependency 1_"},
            {"type": SectionType.OPEN_QUESTIONS, "title": "Open Questions", "content": "## Questions to Resolve\n\n- [ ] _Question 1_\n- [ ] _Question 2_"},
        ]
    },

    "process_improvement": {
        "id": "process_improvement",
        "name": "Process Improvement",
        "description": "Template for optimizing existing business processes",
        "sections": [
            {"type": SectionType.OVERVIEW, "title": "Overview", "content": "## Problem Statement\n\n_What problem are we solving?_\n\n## Current State (AS-IS)\n\n_Describe the current process and its pain points_\n\n## Desired State (TO-BE)\n\n_Describe the target state_"},
            {"type": SectionType.OBJECTIVES, "title": "Improvement Objectives", "content": "## Key Performance Indicators\n\n| KPI | Current | Target | Improvement |\n|-----|---------|--------|-------------|\n| _KPI 1_ | _X_ | _Y_ | _Z%_ |"},
            {"type": SectionType.USER_JOURNEYS, "title": "User Journeys", "content": "## Current Journey (AS-IS)\n\n_Describe current flow_\n\n## Improved Journey (TO-BE)\n\n_Describe optimized flow_"},
            {"type": SectionType.ASSUMPTIONS, "title": "Assumptions & Risks", "content": "## Assumptions\n\n- _Assumption 1_\n\n## Risks\n\n| Risk | Likelihood | Impact | Mitigation |\n|------|------------|--------|------------|\n| _Risk 1_ | _M_ | _H_ | _Mitigation_ |"},
        ]
    },

    "new_capability": {
        "id": "new_capability",
        "name": "New Capability",
        "description": "Template for adding new business capabilities",
        "sections": [
            {"type": SectionType.OVERVIEW, "title": "Capability Overview", "content": "## Business Need\n\n_Why do we need this capability?_\n\n## Strategic Alignment\n\n_How does this align with business strategy?_"},
            {"type": SectionType.OBJECTIVES, "title": "Success Criteria", "content": "## Business Outcomes\n\n_What business outcomes will this enable?_\n\n## Measurable Goals\n\n- _Goal 1_"},
            {"type": SectionType.CONTEXT, "title": "Business Context", "content": "## Stakeholders\n\n| Stakeholder | Role | Interest |\n|-------------|------|----------|\n| _Name_ | _Role_ | _Interest_ |\n\n## Related Capabilities\n\n_What existing capabilities does this relate to?_"},
            {"type": SectionType.USER_JOURNEYS, "title": "User Journeys", "content": "## Primary Journey\n\n**Actor**: _Primary user_\n\n**Goal**: _What they want to achieve_\n\n**Steps**:\n1. _Step 1_\n2. _Step 2_"},
            {"type": SectionType.BAM_REFERENCES, "title": "Architecture References", "content": "## Related Architecture Elements\n\n_Link to capabilities, processes, and applications in HOPEX_"},
            {"type": SectionType.ASSUMPTIONS, "title": "Assumptions & Dependencies", "content": "## Assumptions\n\n- _Assumption 1_\n\n## Dependencies\n\n- _Dependency 1_"},
        ]
    },

    "integration": {
        "id": "integration",
        "name": "System Integration",
        "description": "Template for integration use cases",
        "sections": [
            {"type": SectionType.OVERVIEW, "title": "Integration Overview", "content": "## Purpose\n\n_Why is this integration needed?_\n\n## Systems Involved\n\n| System | Role | Owner |\n|--------|------|-------|\n| _System A_ | _Source_ | _Team X_ |"},
            {"type": SectionType.OBJECTIVES, "title": "Integration Goals", "content": "## Data Flow Requirements\n\n_What data needs to flow where?_\n\n## Non-Functional Requirements\n\n- **Latency**: _Target_\n- **Availability**: _Target_\n- **Volume**: _Expected_"},
            {"type": SectionType.USER_JOURNEYS, "title": "Integration Scenarios", "content": "## Scenario 1: [Name]\n\n**Trigger**: _What initiates this flow?_\n\n**Flow**:\n1. _Step 1_\n2. _Step 2_\n\n**Expected Outcome**: _What should happen?_"},
            {"type": SectionType.ASSUMPTIONS, "title": "Technical Constraints", "content": "## API Constraints\n\n_Any API limitations?_\n\n## Security Requirements\n\n_Authentication, authorization needs_"},
        ]
    },

    "blank": {
        "id": "blank",
        "name": "Blank Template",
        "description": "Start from scratch with minimal structure",
        "sections": [
            {"type": SectionType.OVERVIEW, "title": "Overview", "content": ""},
            {"type": SectionType.OBJECTIVES, "title": "Objectives", "content": ""},
        ]
    }
}


def get_available_templates() -> list[dict]:
    """Get list of available templates."""
    return [
        {
            "id": t["id"],
            "name": t["name"],
            "description": t["description"],
            "sectionCount": len(t["sections"]),
        }
        for t in TEMPLATES.values()
    ]


def get_template(template_id: str) -> dict | None:
    """Get a specific template by ID."""
    return TEMPLATES.get(template_id)


def apply_template(use_case: UseCaseDescription, template_id: str) -> None:
    """Apply a template to a use case, creating sections."""
    template = TEMPLATES.get(template_id)
    if not template:
        return

    use_case.template_id = template_id

    for i, section_def in enumerate(template["sections"]):
        use_case.add_section(
            section_type=section_def["type"].value if isinstance(section_def["type"], SectionType) else section_def["type"],
            title=section_def["title"],
            content=section_def["content"],
        )
