# SC-2: MLAS Suite V1 - Architecture Document

**Version:** 1.0.0  
**Date:** January 30, 2026  
**Status:** 🟢 Complete  
**Canonical Reference:** [SC-2: MLAS Suite V1](https://github.com/webwakaagent1/webwaka-governance/blob/main/docs/planning/wave4/PROMPT_SC-2_MLAS_SUITE.md)

---

## 1. Executive Summary

The SC-2 MLAS Suite V1 is a comprehensive suite that exposes the full power of the CB-1 MLAS Capability. It provides partners and clients with UI and APIs to manage their own affiliate and revenue-sharing ecosystems with configurable revenue sharing, multi-level attribution, abuse prevention, and flexible pricing.

**Key Capabilities:**
- **Revenue Sharing Configuration** - UI and API for complex revenue sharing rules
- **Multi-Level Attribution** - Track and attribute sales across multiple affiliate levels
- **Abuse Prevention** - Detect and prevent fraudulent activity
- **Flexible Pricing** - Partners and clients set their own pricing models

**Alignment with CB-1:**
- Leverages CB-1 MLAS Capability as configurable infrastructure
- Does not dictate policy, enables configuration (INV-006)
- Maintains all CB-1 commission calculation and payout logic
- Adds UI/UX layer for partner and client management

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     UI Layer (React)                        │
│  ┌──────────────┬──────────────┬──────────────┬──────────┐  │
│  │ Revenue      │ Attribution  │ Abuse        │ Pricing  │  │
│  │ Sharing UI   │ UI           │ Prevention   │ UI       │  │
│  │              │              │ UI           │          │  │
│  └──────────────┴──────────────┴──────────────┴──────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (Express.js)                   │
│  ┌──────────────┬──────────────┬──────────────┬──────────┐  │
│  │ Revenue      │ Attribution  │ Abuse        │ Pricing  │  │
│  │ Sharing API  │ API          │ Detection    │ API      │  │
│  │              │              │ API          │          │  │
│  └──────────────┴──────────────┴──────────────┴──────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                            │
│  ┌──────────────┬──────────────┬──────────────┬──────────┐  │
│  │ Revenue      │ Attribution  │ Abuse        │ Pricing  │  │
│  │ Sharing      │ Service      │ Detection    │ Service  │  │
│  │ Service      │              │ Service      │          │  │
│  └──────────────┴──────────────┴──────────────┴──────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              CB-1 MLAS Capability Layer                     │
│  ┌──────────────┬──────────────┬──────────────┬──────────┐  │
│  │ Attribution  │ Commission   │ Payout       │ Audit &  │  │
│  │ Service      │ Service      │ Service      │ Dispute  │  │
│  └──────────────┴──────────────┴──────────────┴──────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                               │
│  ┌──────────────┬──────────────┬──────────────┬──────────┐  │
│  │ PostgreSQL   │ Redis Cache  │ Audit Log    │ Event    │  │
│  │ (Primary)    │ (Sessions)   │ (Immutable)  │ Stream   │  │
│  └──────────────┴──────────────┴──────────────┴──────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Core Components

**Revenue Sharing Service**
- Manages revenue sharing configurations
- Supports 5 revenue models (flat, percentage, tiered, performance-based, hybrid)
- Calculates revenue based on configurable rules
- Integrates with CB-1 commission calculation

**Attribution Service**
- Tracks multi-level attribution
- Supports 6 attribution models (direct, referral, multi-touch, first-click, last-click, linear)
- Calculates attribution weights
- Integrates with CB-1 attribution tracking

**Abuse Detection Service**
- Detects fraudulent activity
- Supports 7 abuse types (click fraud, cookie stuffing, self-dealing, incentivized traffic, brand bidding, duplicate orders, unusual patterns)
- Implements configurable detection rules
- Generates abuse alerts with risk levels

**Pricing Service**
- Manages flexible pricing configurations
- Supports 4 pricing models (fixed, variable, dynamic, custom)
- Calculates dynamic prices based on rules
- Tracks pricing history and adjustments

---

## 3. Revenue Sharing Configuration

### 3.1 Revenue Sharing Models

| Model | Description | Use Case |
|-------|-------------|----------|
| **Flat Rate** | Fixed commission per sale | Simple affiliate programs |
| **Percentage** | Percentage of sale amount | Volume-based programs |
| **Tiered** | Different rates by sale amount | Performance incentives |
| **Performance-Based** | Rate varies by affiliate performance | High-volume affiliates |
| **Hybrid** | Combination of models | Complex programs |

### 3.2 Configuration Structure

```typescript
interface RevenueSharingConfiguration {
  id: string;
  tenantId: string;
  organizationId: string;
  name: string;
  description?: string;
  rules: RevenueSharingRule[];
  defaultRule?: RevenueSharingRule;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}
```

### 3.3 UI Components

- **Configuration Wizard** - Step-by-step configuration
- **Rule Builder** - Visual rule creation
- **Preview Calculator** - Preview revenue calculations
- **Performance Dashboard** - Track revenue metrics

---

## 4. Multi-Level Attribution

### 4.1 Attribution Models

| Model | Description | Credit Distribution |
|-------|-------------|---------------------|
| **Direct** | All credit to last touchpoint | 100% to last |
| **First-Click** | All credit to first touchpoint | 100% to first |
| **Last-Click** | All credit to last touchpoint | 100% to last |
| **Linear** | Equal credit to all touchpoints | Equal distribution |
| **Multi-Touch** | Weighted by recency | Recency-based |
| **Referral** | Credit to referrer and converter | 50/50 split |

### 4.2 Configuration Structure

```typescript
interface AttributionConfiguration {
  id: string;
  tenantId: string;
  organizationId: string;
  attributionType: AttributionType;
  lookbackWindow: number; // days
  maxAffiliateChainDepth: number;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}
```

### 4.3 UI Components

- **Attribution Model Selector** - Choose attribution model
- **Lookback Window Configuration** - Set attribution window
- **Attribution Report** - View attribution history
- **Weight Calculator** - Preview attribution weights

---

## 5. Abuse Prevention

### 5.1 Abuse Types

| Type | Description | Detection Method |
|------|-------------|------------------|
| **Click Fraud** | Fake clicks to inflate metrics | Click pattern analysis |
| **Cookie Stuffing** | Unauthorized cookie placement | Cookie tracking |
| **Self-Dealing** | Affiliate promoting own products | Sales pattern analysis |
| **Incentivized Traffic** | Paid traffic without disclosure | Traffic source analysis |
| **Brand Bidding** | Bidding on brand keywords | Keyword analysis |
| **Duplicate Orders** | Same order from multiple affiliates | Order deduplication |
| **Unusual Pattern** | Anomalous behavior | Statistical analysis |

### 5.2 Detection Rules

```typescript
interface AbuseDetectionRule {
  id: string;
  tenantId: string;
  name: string;
  abuseType: AbuseType;
  conditions: AbuseCondition[];
  riskLevel: AbuseRiskLevel;
  action: AbuseAction;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}
```

### 5.3 Risk Levels & Actions

| Risk Level | Action | Description |
|-----------|--------|-------------|
| **Low** | FLAG | Mark for review |
| **Medium** | HOLD | Hold payout pending review |
| **High** | REJECT | Reject transaction |
| **Critical** | SUSPEND | Suspend affiliate |

### 5.4 UI Components

- **Rule Builder** - Create detection rules
- **Alert Dashboard** - View abuse alerts
- **Pattern Analysis** - Analyze affiliate patterns
- **Alert Resolution** - Manage alert workflow

---

## 6. Flexible Pricing

### 6.1 Pricing Models

| Model | Description | Use Case |
|-------|-------------|----------|
| **Fixed** | Static price for all actors | Standard pricing |
| **Variable** | Price varies by conditions | Tiered pricing |
| **Dynamic** | Price calculated in real-time | AI-based pricing |
| **Custom** | Partner-defined pricing | Custom agreements |

### 6.2 Configuration Structure

```typescript
interface PricingConfiguration {
  id: string;
  tenantId: string;
  organizationId: string;
  actorId: string; // Affiliate or Partner
  actorType: 'AFFILIATE' | 'PARTNER' | 'CLIENT';
  modelType: PricingModelType;
  basePrice: Decimal;
  rules: PricingRule[];
  overrides?: PricingOverride[];
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}
```

### 6.3 Pricing Rules

```typescript
interface PricingRule {
  id: string;
  name: string;
  conditions: PricingCondition[];
  priceAdjustment: Decimal;
  adjustmentType: 'ABSOLUTE' | 'PERCENTAGE';
  priority: number;
}
```

### 6.4 UI Components

- **Pricing Configuration Panel** - Set base price and rules
- **Rule Priority Manager** - Manage rule execution order
- **Price Calculator** - Preview calculated prices
- **Pricing History** - View pricing adjustments

---

## 7. API Endpoints

### 7.1 Revenue Sharing Endpoints

```
POST   /api/revenue-sharing/configurations
GET    /api/revenue-sharing/configurations/:id
PUT    /api/revenue-sharing/configurations/:id
DELETE /api/revenue-sharing/configurations/:id
GET    /api/revenue-sharing/configurations
POST   /api/revenue-sharing/calculate
```

### 7.2 Attribution Endpoints

```
POST   /api/attribution/configurations
GET    /api/attribution/configurations/:id
PUT    /api/attribution/configurations/:id
GET    /api/attribution/configurations
POST   /api/attribution/track
GET    /api/attribution/history/:affiliateId
```

### 7.3 Abuse Detection Endpoints

```
POST   /api/abuse/rules
GET    /api/abuse/rules/:id
PUT    /api/abuse/rules/:id
DELETE /api/abuse/rules/:id
GET    /api/abuse/rules
POST   /api/abuse/detect
GET    /api/abuse/alerts
PATCH  /api/abuse/alerts/:id/resolve
```

### 7.4 Pricing Endpoints

```
POST   /api/pricing/configurations
GET    /api/pricing/configurations/:id
PUT    /api/pricing/configurations/:id
DELETE /api/pricing/configurations/:id
GET    /api/pricing/configurations
POST   /api/pricing/calculate
GET    /api/pricing/history/:actorId
```

---

## 8. Governance & Compliance

### 8.1 INV-006: MLAS as Infrastructure

**Principle:** The suite must adhere to the principle of MLAS as a configurable engine, not a policy dictator.

**Implementation:**
- All revenue sharing rules are configurable
- All attribution models are selectable
- All abuse detection rules are customizable
- All pricing models are flexible
- No hardcoded business logic
- Full audit trail of all configurations

### 8.2 INV-012v2: Multi-Repository Topology

**Principle:** All work must be committed to the `webwaka-suites` repository.

**Implementation:**
- All code in `/implementations/sc2-mlas-suite/`
- All documentation in `/implementations/sc2-mlas-suite/docs/`
- All tests in `/implementations/sc2-mlas-suite/tests/`

---

## 9. Integration with CB-1

### 9.1 CB-1 Capability Integration

The SC-2 MLAS Suite integrates with CB-1 MLAS Capability:

1. **Attribution Tracking** - Uses CB-1 attribution tracking
2. **Commission Calculation** - Uses CB-1 commission calculation engine
3. **Payout Routing** - Uses CB-1 payout routing
4. **Audit Logging** - Uses CB-1 audit logging
5. **Dispute Resolution** - Uses CB-1 dispute resolution

### 9.2 Configuration Alignment

- Revenue sharing rules map to CB-1 commission rules
- Attribution configurations align with CB-1 attribution models
- Pricing configurations are independent but compatible
- Abuse detection rules are independent

---

## 10. Testing Strategy

### 10.1 Unit Tests

- Revenue sharing calculation logic
- Attribution weight calculation
- Abuse detection rule matching
- Pricing calculation logic
- Configuration validation

### 10.2 Integration Tests

- End-to-end revenue sharing workflow
- Multi-level attribution tracking
- Abuse detection and alerting
- Dynamic pricing calculation
- Configuration persistence

### 10.3 End-to-End Tests

- Complete revenue sharing configuration and calculation
- Multi-level attribution tracking and reporting
- Abuse detection and alert resolution
- Flexible pricing application

---

## 11. Performance Considerations

### 11.1 Scalability

- Configuration caching for fast lookups
- Batch processing for abuse detection
- Asynchronous alert generation
- Efficient rule evaluation

### 11.2 Optimization

- Rule priority-based early exit
- Caching frequently used configurations
- Batch calculations for bulk operations
- Indexed queries for fast retrieval

---

## 12. Security & Compliance

### 12.1 Security Measures

- Role-based access control (RBAC)
- Configuration audit trail
- Encrypted sensitive data
- Rate limiting on API endpoints
- Input validation on all requests

### 12.2 Compliance

- GDPR: Data residency and right to delete
- SOC 2: Access controls and audit logging
- PCI DSS: Secure payment processing
- Financial regulations: Accurate record keeping

---

## 13. Deployment

### 13.1 Prerequisites

- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- CB-1 MLAS Capability deployed

### 13.2 Installation

```bash
npm install
npm run build
npm run migrate:up
npm start
```

---

## 14. Future Enhancements

- Advanced analytics and reporting
- Machine learning-based pricing optimization
- Real-time fraud detection
- Mobile app for affiliate management
- GraphQL API support

---

## 15. References

- [SC-2 MLAS Suite V1 Phase Definition](https://github.com/webwakaagent1/webwaka-governance/blob/main/docs/planning/wave4/PROMPT_SC-2_MLAS_SUITE.md)
- [CB-1 MLAS Capability](https://github.com/webwakaagent1/webwaka/blob/main/docs/phases/CB-1_MLAS_CAPABILITY.md)
- [MLAS Suite Implementation Summary](./IMPLEMENTATION_SUMMARY.md)

---

**Document Version:** 1.0.0  
**Last Updated:** January 30, 2026  
**Status:** 🟢 Complete

---

**End of Architecture Document**
