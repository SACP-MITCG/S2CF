# CSRD Carbon Footprint Tracking Requirements

## Document Information
- **Author:** Sarah Chen, Sustainability Lead
- **Date:** January 2026
- **Version:** 1.2
- **Classification:** Internal

---

## 1. Executive Summary

As part of our Corporate Sustainability Reporting Directive (CSRD) compliance initiative, we must implement comprehensive carbon footprint tracking across all operations by Q3 2026. This document outlines the business requirements for tracking Scope 1, 2, and 3 emissions in alignment with GHG Protocol standards.

## 2. Regulatory Context

### 2.1 CSRD Requirements
The European Union's CSRD mandates that large companies report on:
- Direct emissions from owned sources (Scope 1)
- Indirect emissions from purchased energy (Scope 2)
- Value chain emissions (Scope 3)

### 2.2 Compliance Timeline
| Milestone | Date | Requirement |
|-----------|------|-------------|
| System Selection | March 2026 | Choose carbon tracking platform |
| Data Integration | May 2026 | Connect to ERP, procurement systems |
| Initial Reporting | Q3 2026 | First quarterly carbon report |
| Full Compliance | Q1 2027 | Annual CSRD-compliant report |

## 3. Business Objectives

### 3.1 Primary Objectives
1. **Track all emission sources** across 47 facilities in 12 countries
2. **Automate data collection** from energy invoices, fuel purchases, and logistics data
3. **Calculate carbon footprint** using emission factors aligned with GHG Protocol
4. **Generate regulatory reports** meeting CSRD Article 29b requirements

### 3.2 Success Metrics
- 95% automated data capture (vs manual entry)
- Monthly emission reports within 5 business days of period close
- Audit-ready documentation for external verification
- 10% reduction in carbon intensity by 2027

## 4. Stakeholder Analysis

| Stakeholder | Role | Interest |
|-------------|------|----------|
| CFO Office | Sponsor | Financial reporting integration |
| Sustainability Team | Owner | Day-to-day operations |
| IT Department | Enabler | System integration |
| Operations | Data Provider | Facility-level data |
| External Auditors | Validator | Report verification |

## 5. High-Level Requirements

### 5.1 Data Collection
- REQ-001: System shall import energy consumption data from SAP S/4HANA
- REQ-002: System shall capture fuel purchase data from procurement system
- REQ-003: System shall integrate with logistics providers for transport emissions
- REQ-004: System shall support manual entry for data gaps with audit trail

### 5.2 Calculation Engine
- REQ-010: Calculate emissions using location-based and market-based methods
- REQ-011: Apply emission factors from recognized databases (DEFRA, EPA, IEA)
- REQ-012: Support custom emission factors for regional specificity
- REQ-013: Handle unit conversions (kWh, GJ, liters, gallons)

### 5.3 Reporting
- REQ-020: Generate CSRD-compliant sustainability reports
- REQ-021: Provide drill-down from total emissions to source level
- REQ-022: Export data in XBRL format for regulatory submission
- REQ-023: Create executive dashboards for leadership review

## 6. User Journeys

### 6.1 Monthly Data Ingestion
1. Sustainability Analyst logs into carbon platform
2. System automatically imports last month's energy data from SAP
3. Analyst reviews flagged anomalies (>20% variance from baseline)
4. Analyst approves or corrects flagged data points
5. System calculates emissions and updates dashboards

### 6.2 Quarterly Reporting
1. Sustainability Manager initiates quarterly report generation
2. System aggregates emissions by scope, region, and business unit
3. Manager reviews draft report and adds commentary
4. CFO reviews and approves report
5. Report exported for external auditor review

## 7. Integration Requirements

### 7.1 Source Systems
- SAP S/4HANA (energy and utilities)
- Ariba (procurement and supplier data)
- TMS - Transportation Management System
- Facilities Management System

### 7.2 Target Systems
- Power BI (executive dashboards)
- GRI Standards Platform (sustainability reporting)
- XBRL filing system (regulatory submission)

## 8. Assumptions and Constraints

### 8.1 Assumptions
- All facilities have smart meters or reliable manual readings
- Emission factors will be updated annually
- Scope 3 data from suppliers available via CDP disclosure

### 8.2 Constraints
- Budget: €500,000 for implementation
- Timeline: 6-month implementation window
- Resources: 2 FTE dedicated to sustainability data management

## 9. Open Questions

1. Should we include Scope 3 Category 15 (investments) in Phase 1?
2. What is the process for handling data gaps when supplier data unavailable?
3. How frequently should emission factors be refreshed?
4. What level of third-party assurance is required for first year?

## 10. Appendix

### A. Glossary
- **GHG Protocol**: Greenhouse Gas Protocol, global standard for emission accounting
- **CSRD**: Corporate Sustainability Reporting Directive
- **Scope 1**: Direct emissions from owned/controlled sources
- **Scope 2**: Indirect emissions from purchased energy
- **Scope 3**: All other indirect emissions in value chain

### B. Reference Documents
- EU CSRD Directive 2022/2464
- GHG Protocol Corporate Standard
- ESRS E1: Climate Change Reporting Standard
