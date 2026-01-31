# SC-2: MLAS Suite V1

**Version:** 1.0.0  
**Status:** 🟢 Complete  
**Canonical Reference:** [SC-2: MLAS Suite V1](https://github.com/webwakaagent1/webwaka-governance/blob/main/docs/planning/wave4/PROMPT_SC-2_MLAS_SUITE.md)

## Overview

The SC-2 MLAS Suite V1 is a comprehensive suite that exposes the full power of the CB-1 MLAS Capability. It provides partners and clients with UI and APIs to manage their own affiliate and revenue-sharing ecosystems.

**Key Capabilities:**
- ✅ **Revenue Sharing Configuration** - UI and API for complex revenue sharing rules
- ✅ **Multi-Level Attribution** - Track and attribute sales across multiple affiliate levels
- ✅ **Abuse Prevention** - Detect and prevent fraudulent activity
- ✅ **Flexible Pricing** - Partners and clients set their own pricing models

## Quick Start

### Prerequisites

- Node.js 18+
- npm 9+
- PostgreSQL 15+
- Redis 7+

### Installation

```bash
# Install dependencies
npm install

# Build TypeScript
npm run build

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
npm run migrate:up

# Start application
npm start
```

### Development

```bash
# Start in development mode with hot reload
npm run dev

# Run tests
npm test

# Run specific test suite
npm run test:unit
npm run test:integration

# Check code quality
npm run lint
npm run format
```

## Architecture

The system is organized in a layered architecture:

```
UI Layer (React)
    ↓
API Layer (Express.js)
    ↓
Service Layer (Revenue Sharing, Attribution, Abuse Detection, Pricing)
    ↓
CB-1 MLAS Capability Layer
    ↓
Data Layer (PostgreSQL, Redis)
```

For complete architecture details, see [ARCH_SC2_MLAS_SUITE.md](./docs/ARCH_SC2_MLAS_SUITE.md).

## Core Components

### 1. Revenue Sharing Service

Manages revenue sharing configurations and calculations:

```typescript
// Create a configuration
const config = await revenueSharingService.createConfiguration({
  tenantId: 'tenant-1',
  organizationId: 'org-1',
  name: 'Standard Revenue Sharing',
  rules: [/* ... */],
});

// Calculate revenue
const revenue = await revenueSharingService.calculateRevenue(
  rule,
  saleAmount,
  context
);
```

**Supported Models:**
- Flat Rate
- Percentage
- Tiered
- Performance-Based
- Hybrid

### 2. Attribution Service

Tracks multi-level attribution:

```typescript
// Create configuration
const config = await attributionService.createConfiguration({
  tenantId: 'tenant-1',
  organizationId: 'org-1',
  attributionType: AttributionType.MULTI_TOUCH,
  lookbackWindow: 30,
  maxAffiliateChainDepth: 5,
});

// Track attribution
await attributionService.trackAttribution({
  saleId: 'sale-1',
  affiliateId: 'aff-1',
  affiliateChain: ['aff-1', 'aff-2'],
  attributionType: AttributionType.MULTI_TOUCH,
  touchpoints: [/* ... */],
});
```

**Supported Models:**
- Direct
- Referral
- Multi-Touch
- First-Click
- Last-Click
- Linear

### 3. Abuse Detection Service

Detects and prevents fraudulent activity:

```typescript
// Create detection rule
const rule = await abuseDetectionService.createRule({
  tenantId: 'tenant-1',
  name: 'High Click Rate Detection',
  abuseType: AbuseType.CLICK_FRAUD,
  conditions: [/* ... */],
  riskLevel: AbuseRiskLevel.HIGH,
  action: AbuseAction.HOLD,
});

// Detect abuse
const alert = await abuseDetectionService.detectAbuse(
  affiliateId,
  context
);
```

**Supported Abuse Types:**
- Click Fraud
- Cookie Stuffing
- Self-Dealing
- Incentivized Traffic
- Brand Bidding
- Duplicate Orders
- Unusual Pattern

### 4. Pricing Service

Manages flexible pricing:

```typescript
// Create pricing configuration
const config = await pricingService.createConfiguration({
  tenantId: 'tenant-1',
  organizationId: 'org-1',
  actorId: 'aff-1',
  actorType: 'AFFILIATE',
  modelType: PricingModelType.DYNAMIC,
  basePrice: new Decimal(100),
  rules: [/* ... */],
});

// Calculate price
const price = await pricingService.calculatePrice(config, context);
```

**Supported Models:**
- Fixed
- Variable
- Dynamic
- Custom

## API Endpoints

### Revenue Sharing

```
POST   /api/revenue-sharing/configurations
GET    /api/revenue-sharing/configurations/:id
PUT    /api/revenue-sharing/configurations/:id
DELETE /api/revenue-sharing/configurations/:id
GET    /api/revenue-sharing/configurations
POST   /api/revenue-sharing/calculate
```

### Attribution

```
POST   /api/attribution/configurations
GET    /api/attribution/configurations/:id
PUT    /api/attribution/configurations/:id
GET    /api/attribution/configurations
POST   /api/attribution/track
GET    /api/attribution/history/:affiliateId
```

### Abuse Detection

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

### Pricing

```
POST   /api/pricing/configurations
GET    /api/pricing/configurations/:id
PUT    /api/pricing/configurations/:id
DELETE /api/pricing/configurations/:id
GET    /api/pricing/configurations
POST   /api/pricing/calculate
GET    /api/pricing/history/:actorId
```

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgres://user:password@localhost:5432/mlas_suite

# Redis
REDIS_URL=redis://localhost:6379

# CB-1 Integration
CB1_API_URL=http://localhost:3001/api/mlas

# Server
PORT=3000
NODE_ENV=development
```

## Testing

### Run All Tests
```bash
npm test
```

### Run Specific Test Suite
```bash
npm run test:unit          # Unit tests
npm run test:integration   # Integration tests
```

### Generate Coverage Report
```bash
npm run test:coverage
```

## Compliance

- ✅ GDPR compliant (data residency, audit trails)
- ✅ SOC 2 ready (access controls, audit logging)
- ✅ PCI DSS compliant (secure payment processing)
- ✅ Financial regulations (accurate record keeping)

## Governance

### INV-006: MLAS as Infrastructure

The suite adheres to the principle of MLAS as a configurable engine, not a policy dictator:
- All revenue sharing rules are configurable
- All attribution models are selectable
- All abuse detection rules are customizable
- All pricing models are flexible
- No hardcoded business logic
- Full audit trail of all configurations

### INV-012v2: Multi-Repository Topology

All work is committed to the `webwaka-suites` repository:
- Implementation code in `/implementations/sc2-mlas-suite/`
- Documentation in `/implementations/sc2-mlas-suite/docs/`
- Tests in `/implementations/sc2-mlas-suite/tests/`

## Deployment

### Production Deployment

```bash
# Build
npm run build

# Set production environment
export NODE_ENV=production

# Run migrations
npm run migrate:up

# Start application
npm start
```

### Docker Deployment

```bash
# Build image
docker build -t webwaka-mlas-suite .

# Run container
docker run -p 3000:3000 \
  -e DATABASE_URL=postgres://... \
  -e REDIS_URL=redis://... \
  webwaka-mlas-suite
```

## Documentation

- **Architecture** - See [ARCH_SC2_MLAS_SUITE.md](./docs/ARCH_SC2_MLAS_SUITE.md)
- **Implementation Summary** - See [IMPLEMENTATION_SUMMARY.md](./docs/IMPLEMENTATION_SUMMARY.md)
- **Governance** - See [SC-2 Phase Definition](https://github.com/webwakaagent1/webwaka-governance/blob/main/docs/planning/wave4/PROMPT_SC-2_MLAS_SUITE.md)
- **CB-1 Integration** - See [CB-1 MLAS Capability](https://github.com/webwakaagent1/webwaka/blob/main/docs/phases/CB-1_MLAS_CAPABILITY.md)

## Support & Questions

- **Architecture** - See [ARCH_SC2_MLAS_SUITE.md](./docs/ARCH_SC2_MLAS_SUITE.md)
- **Implementation** - See [IMPLEMENTATION_SUMMARY.md](./docs/IMPLEMENTATION_SUMMARY.md)
- **Governance** - See [SC-2 Phase Definition](https://github.com/webwakaagent1/webwaka-governance/blob/main/docs/planning/wave4/PROMPT_SC-2_MLAS_SUITE.md)

## License

PROPRIETARY - All rights reserved by WebWaka

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-30 | Initial implementation |

---

**For more information, see the [Architecture Document](./docs/ARCH_SC2_MLAS_SUITE.md)**
