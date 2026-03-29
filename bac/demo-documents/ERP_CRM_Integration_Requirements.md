# ERP-CRM Integration Requirements

## Project Information
- **Project:** SAP S/4HANA to Salesforce Integration
- **Author:** David Park, Enterprise Integration Architect
- **Date:** February 2026
- **Version:** 2.0

---

## 1. Integration Overview

### 1.1 Purpose
Establish bidirectional real-time integration between SAP S/4HANA (ERP) and Salesforce Sales Cloud (CRM) to ensure consistent customer, product, and order data across sales and operations.

### 1.2 Systems in Scope

| System | Role | Version |
|--------|------|---------|
| SAP S/4HANA | ERP - Master data, orders, inventory | 2023 |
| Salesforce Sales Cloud | CRM - Leads, opportunities, accounts | Enterprise |
| MuleSoft Anypoint | Integration Platform | 4.4 |
| Azure Service Bus | Event messaging | Standard |

### 1.3 Integration Patterns
- **Real-time sync** for customer and product master data
- **Event-driven** for order creation and status updates
- **Batch sync** for pricing and inventory (hourly)
- **On-demand** for credit check requests

## 2. Business Objectives

1. **Single source of truth** for customer data (SAP as master)
2. **Real-time order visibility** in Salesforce for sales reps
3. **Accurate pricing** in Salesforce quotes from SAP price lists
4. **Automated order flow** from Salesforce CPQ to SAP SD
5. **Credit check integration** before quote finalization

## 3. Data Flows

### 3.1 Customer Master (SAP → Salesforce)
```
SAP S/4HANA (BP Master)
    │
    ├─ Real-time IDoc/RFC
    │
    ▼
MuleSoft Anypoint
    │
    ├─ Transform BAPI_BUPA → Account SObject
    │
    ▼
Salesforce Account
```

**Data Elements:**
| SAP Field | Salesforce Field | Direction |
|-----------|------------------|-----------|
| Business Partner ID | SAP_Customer_ID__c | SAP → SF |
| Customer Name | Name | SAP → SF |
| Address (multiple) | BillingAddress, ShippingAddress | SAP → SF |
| Credit Limit | Credit_Limit__c | SAP → SF |
| Payment Terms | Payment_Terms__c | SAP → SF |
| Customer Group | Customer_Segment__c | SAP → SF |

**Sync Trigger:** On BP create/change in SAP (real-time via IDoc)

### 3.2 Product Master (SAP → Salesforce)
```
SAP Material Master
    │
    ├─ Hourly batch extract
    │
    ▼
MuleSoft Batch Job
    │
    ├─ Transform MARA/MARC → Product2
    │
    ▼
Salesforce Product2 + PricebookEntry
```

**Data Elements:**
| SAP Field | Salesforce Field |
|-----------|------------------|
| Material Number | ProductCode |
| Description | Name |
| Material Group | Family |
| Base UoM | Quantity_UOM__c |
| Net Weight | Weight__c |
| Status | IsActive |

**Price Sync:** Condition records (PR00) → PricebookEntry (hourly)

### 3.3 Sales Order (Salesforce → SAP)
```
Salesforce Opportunity (Closed Won)
    │
    ├─ Platform Event
    │
    ▼
MuleSoft Flow
    │
    ├─ Build BAPI_SALESORDER_CREATEFROMDAT2
    │
    ▼
SAP Sales Order (VA01)
    │
    ├─ Return SO Number
    │
    ▼
Salesforce Order__c.SAP_Order_Number__c
```

**Data Elements:**
| Salesforce Field | SAP Field |
|------------------|-----------|
| Account.SAP_Customer_ID__c | SOLD_TO_PARTY |
| Shipping_Address__c | SHIP_TO_PARTY |
| OpportunityLineItem.ProductCode | MATERIAL |
| Quantity | TARGET_QTY |
| UnitPrice | COND_VALUE (PR00) |
| Requested_Delivery_Date__c | REQ_DATE_H |

### 3.4 Order Status (SAP → Salesforce)
```
SAP Order Status Change
    │
    ├─ Custom IDoc (ZSALESORD_STATUS)
    │
    ▼
Azure Service Bus Queue
    │
    ├─ MuleSoft Event Consumer
    │
    ▼
Salesforce Order__c.Status__c
```

**Status Mapping:**
| SAP Status | Salesforce Status |
|------------|-------------------|
| Created | Booked |
| Released | In Process |
| Partially Delivered | Partial Ship |
| Fully Delivered | Shipped |
| Invoiced | Invoiced |

### 3.5 Credit Check (Salesforce → SAP → Salesforce)
```
Salesforce Quote (Request Credit Check)
    │
    ├─ Synchronous API Call
    │
    ▼
MuleSoft API
    │
    ├─ BAPI_CREDITCHECK_SIMULATE
    │
    ▼
SAP Credit Check
    │
    ├─ Return: Approved/Declined/Amount
    │
    ▼
Salesforce Quote.Credit_Status__c
```

**Response Fields:**
- `credit_status`: Approved | Declined | Partial
- `available_credit`: Remaining limit
- `blocked_amount`: Amount exceeding limit
- `message`: Reason for decline

## 4. Technical Requirements

### 4.1 Integration Platform
- **MuleSoft Anypoint Platform** for orchestration
- CloudHub 2.0 deployment (2 vCores production)
- API-led connectivity (System, Process, Experience layers)

### 4.2 Connectivity
| System | Connector | Authentication |
|--------|-----------|----------------|
| SAP S/4HANA | SAP Connector (RFC/IDoc) | Service User + SSO |
| Salesforce | Salesforce Connector | OAuth 2.0 JWT Bearer |
| Azure Service Bus | AMQP Connector | SAS Token |

### 4.3 Error Handling
- Dead letter queue for failed messages
- Retry policy: 3 attempts with exponential backoff
- Alert notification via PagerDuty for critical failures
- Error logging to Splunk

### 4.4 Performance Requirements
| Flow | SLA | Volume |
|------|-----|--------|
| Customer sync | < 5 sec | 500/day |
| Product sync | < 1 hour batch | 50K products |
| Order create | < 10 sec | 2000/day |
| Status update | < 30 sec | 5000/day |
| Credit check | < 3 sec | 500/day |

## 5. Integration Scenarios

### 5.1 Scenario: New Customer in SAP
**Trigger:** Business Partner created in SAP (BP transaction)

1. SAP triggers IDoc DEBMAS06 on BP save
2. MuleSoft receives IDoc via SAP Connector
3. Transform BP data to Salesforce Account format
4. Check if Account exists (by SAP_Customer_ID__c)
5. If new: Create Account
6. If existing: Update Account fields
7. Log sync result, handle errors
8. Sales rep sees customer in Salesforce within 5 seconds

### 5.2 Scenario: Opportunity Closed Won
**Trigger:** Opportunity Stage = "Closed Won" in Salesforce

1. Salesforce triggers Platform Event: Order_Created__e
2. MuleSoft subscribes to Platform Event
3. Retrieve Opportunity, OpportunityLineItems, Account
4. Map to SAP Sales Order BAPI structure
5. Call BAPI_SALESORDER_CREATEFROMDAT2
6. Capture SAP Order Number from response
7. Update Salesforce Order__c with SAP_Order_Number__c
8. If error: Retry, then queue for manual review

### 5.3 Scenario: Credit Check Before Quote
**Trigger:** "Check Credit" button on Salesforce Quote

1. Sales rep clicks "Check Credit" on Quote
2. Salesforce invokes MuleSoft Experience API
3. MuleSoft calls SAP BAPI_CREDITCHECK_SIMULATE
4. SAP returns credit status and available limit
5. MuleSoft returns formatted response
6. Salesforce updates Quote.Credit_Status__c
7. Rep can proceed with quote or escalate

## 6. Security Requirements

### 6.1 Authentication & Authorization
- SAP: RFC user with limited authorizations (S_RFC, S_TABU_DIS)
- Salesforce: Integration user with API-only profile
- MuleSoft: Encrypted properties, secrets management

### 6.2 Data Protection
- TLS 1.3 for all connections
- PII fields encrypted in transit and at rest
- No sensitive data in logs (masking enabled)
- Data residency: EU region only

### 6.3 Audit & Compliance
- All transactions logged with correlation ID
- 90-day log retention
- SOX compliance for financial data flows

## 7. Testing Strategy

### 7.1 Test Types
| Type | Scope | Environment |
|------|-------|-------------|
| Unit | Individual Mule flows | Local |
| Integration | End-to-end data flows | QA |
| Performance | Load testing at 2x volume | Stage |
| UAT | Business scenarios | Pre-Prod |

### 7.2 Test Scenarios
- [ ] New customer sync within 5 seconds
- [ ] Customer update reflects in Salesforce
- [ ] Product price sync accuracy (100%)
- [ ] Order creation returns SAP order number
- [ ] Order status updates flow to Salesforce
- [ ] Credit check returns within 3 seconds
- [ ] Error handling and retry logic
- [ ] Duplicate prevention

## 8. Rollout Plan

### 8.1 Phases
| Phase | Scope | Timeline |
|-------|-------|----------|
| Phase 1 | Customer master sync | Month 1-2 |
| Phase 2 | Product and pricing | Month 2-3 |
| Phase 3 | Order creation | Month 3-4 |
| Phase 4 | Status updates | Month 4-5 |
| Phase 5 | Credit check | Month 5-6 |

### 8.2 Go-Live Criteria
- All test scenarios passed
- Performance SLAs met in staging
- Runbook and support documentation complete
- L1/L2 support team trained
- Rollback procedure tested

## 9. Support Model

### 9.1 Monitoring
- MuleSoft Anypoint Monitoring for API metrics
- Splunk dashboards for integration health
- PagerDuty alerts for P1/P2 issues

### 9.2 Support Tiers
| Tier | Responsibility | Response |
|------|----------------|----------|
| L1 | Triage, known issues | 15 min |
| L2 | Integration issues | 1 hour |
| L3 | Development/SAP/SF | 4 hours |

## 10. Appendix

### A. Glossary
- **BAPI:** Business Application Programming Interface (SAP)
- **IDoc:** Intermediate Document (SAP message format)
- **RFC:** Remote Function Call (SAP protocol)
- **CPQ:** Configure, Price, Quote
- **SD:** Sales and Distribution (SAP module)

### B. Reference Architecture
See enterprise integration architecture document (INT-ARCH-001)
