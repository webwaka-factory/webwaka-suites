/**
 * Integration Tests for SC-2 MLAS Suite
 * 
 * End-to-end tests for MLAS workflows including revenue sharing,
 * attribution, abuse detection, and pricing.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import Decimal from 'decimal.js';
import { RevenueSharingService } from '../../src/services/RevenueSharingService';
import { AbuseDetectionService } from '../../src/services/AbuseDetectionService';
import { AttributionService } from '../../src/services/AttributionService';
import { PricingService } from '../../src/services/PricingService';
import {
  RevenueSharingConfiguration,
  RevenueSharingRule,
  RevenueModelType,
  AbuseDetectionRule,
  AbuseType,
  AbuseRiskLevel,
  AbuseAction,
  AttributionConfiguration,
  AttributionEvent,
  AttributionType,
  PricingConfiguration,
  PricingModelType,
  PricingRule,
} from '../../src/types';

describe('MLAS Integration Tests', () => {
  let revenueSharingService: RevenueSharingService;
  let abuseDetectionService: AbuseDetectionService;
  let attributionService: AttributionService;
  let pricingService: PricingService;
  let tenantId: string;
  let organizationId: string;

  beforeEach(() => {
    revenueSharingService = new RevenueSharingService();
    abuseDetectionService = new AbuseDetectionService();
    attributionService = new AttributionService();
    pricingService = new PricingService();
    tenantId = 'tenant-integration-001';
    organizationId = 'org-integration-001';
  });

  describe('Complete Affiliate Sale Flow', () => {
    it('should process a complete affiliate sale with revenue sharing', async () => {
      // Step 1: Set up revenue sharing configuration
      const revenueRule: RevenueSharingRule = {
        id: 'rule-sale-001',
        tenantId,
        name: 'Standard Affiliate Commission',
        modelType: RevenueModelType.PERCENTAGE,
        baseRate: new Decimal(15),
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const revenueConfig: RevenueSharingConfiguration = {
        id: 'config-sale-001',
        tenantId,
        organizationId,
        name: 'Affiliate Program',
        rules: [revenueRule],
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      await revenueSharingService.createConfiguration(revenueConfig);

      // Step 2: Set up attribution configuration
      const attributionConfig: AttributionConfiguration = {
        id: 'attr-sale-001',
        tenantId,
        organizationId,
        attributionType: AttributionType.LAST_CLICK,
        lookbackWindow: 30,
        maxAffiliateChainDepth: 3,
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      await attributionService.createConfiguration(attributionConfig);

      // Step 3: Track attribution event
      const attributionEvent: AttributionEvent = {
        id: 'event-sale-001',
        tenantId,
        saleId: 'sale-001',
        affiliateId: 'affiliate-001',
        affiliateChain: ['affiliate-001'],
        attributionType: AttributionType.LAST_CLICK,
        attributionWeight: new Decimal(1),
        touchpoints: [
          {
            affiliateId: 'affiliate-001',
            timestamp: new Date(),
            channel: 'blog',
            weight: new Decimal(1),
          },
        ],
        createdAt: new Date(),
      };

      await attributionService.trackAttribution(attributionEvent);

      // Step 4: Calculate revenue share
      const saleAmount = new Decimal(1000);
      const commission = await revenueSharingService.calculateRevenue(
        revenueRule,
        saleAmount
      );

      expect(commission.toNumber()).toBe(150); // 15% of 1000

      // Step 5: Verify attribution history
      const history = await attributionService.getAttributionHistory('affiliate-001');
      expect(history.length).toBe(1);
      expect(history[0].saleId).toBe('sale-001');
    });

    it('should detect and handle fraudulent activity', async () => {
      // Step 1: Set up abuse detection rules
      const clickFraudRule: AbuseDetectionRule = {
        id: 'rule-fraud-001',
        tenantId,
        name: 'Click Fraud Detection',
        abuseType: AbuseType.CLICK_FRAUD,
        conditions: [
          { metric: 'clickRate', operator: 'gt', threshold: 100 },
        ],
        riskLevel: AbuseRiskLevel.HIGH,
        action: AbuseAction.HOLD,
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      await abuseDetectionService.createRule(clickFraudRule);

      // Step 2: Process suspicious activity
      const alert = await abuseDetectionService.detectAbuse('affiliate-suspicious', {
        tenantId,
        clickRate: 500, // Abnormally high
        saleId: 'sale-suspicious-001',
      });

      expect(alert).not.toBeNull();
      expect(alert?.abuseType).toBe(AbuseType.CLICK_FRAUD);
      expect(alert?.action).toBe(AbuseAction.HOLD);

      // Step 3: Verify alert is recorded
      const alerts = await abuseDetectionService.getAbuseAlerts(tenantId);
      expect(alerts.length).toBe(1);

      // Step 4: Resolve alert after investigation
      await abuseDetectionService.resolveAlert(alert!.id, 'Verified as false positive');

      const updatedAlerts = await abuseDetectionService.getAbuseAlerts(tenantId);
      expect(updatedAlerts[0].status).toBe('RESOLVED');
    });
  });

  describe('Multi-Touch Attribution Flow', () => {
    it('should handle multi-touch attribution with multiple affiliates', async () => {
      // Set up attribution configuration for multi-touch
      const config: AttributionConfiguration = {
        id: 'attr-multi-001',
        tenantId,
        organizationId,
        attributionType: AttributionType.MULTI_TOUCH,
        lookbackWindow: 30,
        maxAffiliateChainDepth: 5,
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      await attributionService.createConfiguration(config);

      // Track multi-touch attribution
      const event: AttributionEvent = {
        id: 'event-multi-001',
        tenantId,
        saleId: 'sale-multi-001',
        affiliateId: 'affiliate-001',
        affiliateChain: ['affiliate-001', 'affiliate-002', 'affiliate-003'],
        attributionType: AttributionType.MULTI_TOUCH,
        attributionWeight: new Decimal(0.33),
        touchpoints: [
          {
            affiliateId: 'affiliate-001',
            timestamp: new Date(Date.now() - 86400000 * 7),
            channel: 'email',
            weight: new Decimal(0.25),
          },
          {
            affiliateId: 'affiliate-002',
            timestamp: new Date(Date.now() - 86400000 * 3),
            channel: 'social',
            weight: new Decimal(0.35),
          },
          {
            affiliateId: 'affiliate-003',
            timestamp: new Date(),
            channel: 'direct',
            weight: new Decimal(0.40),
          },
        ],
        createdAt: new Date(),
      };

      await attributionService.trackAttribution(event);

      // Verify attribution was tracked
      const history = await attributionService.getAttributionHistory('affiliate-001');
      expect(history.length).toBe(1);
      expect(history[0].touchpoints.length).toBe(3);

      // Calculate revenue for each affiliate based on weight
      const saleAmount = new Decimal(10000);
      const baseCommissionRate = new Decimal(10);

      const totalCommission = saleAmount.times(baseCommissionRate).dividedBy(100);
      
      const affiliate1Commission = totalCommission.times(0.25);
      const affiliate2Commission = totalCommission.times(0.35);
      const affiliate3Commission = totalCommission.times(0.40);

      expect(affiliate1Commission.toNumber()).toBe(250);
      expect(affiliate2Commission.toNumber()).toBe(350);
      expect(affiliate3Commission.toNumber()).toBe(400);
    });
  });

  describe('Dynamic Pricing Flow', () => {
    it('should apply dynamic pricing based on context', async () => {
      // Set up pricing rules
      const rules: PricingRule[] = [
        {
          id: 'rule-volume-001',
          name: 'Volume Discount',
          conditions: [
            { field: 'quantity', operator: 'gte', value: 100 },
          ],
          priceAdjustment: new Decimal(-15),
          adjustmentType: 'PERCENTAGE',
          priority: 1,
        },
        {
          id: 'rule-loyalty-001',
          name: 'Loyalty Discount',
          conditions: [
            { field: 'customerTier', operator: 'eq', value: 'gold' },
          ],
          priceAdjustment: new Decimal(-5),
          adjustmentType: 'PERCENTAGE',
          priority: 2,
        },
        {
          id: 'rule-promo-001',
          name: 'Promotional Discount',
          conditions: [
            { field: 'promoCode', operator: 'eq', value: 'SAVE10' },
          ],
          priceAdjustment: new Decimal(-10),
          adjustmentType: 'ABSOLUTE',
          priority: 3,
        },
      ];

      const config: PricingConfiguration = {
        id: 'config-dynamic-001',
        tenantId,
        organizationId,
        actorId: 'partner-001',
        actorType: 'PARTNER',
        modelType: PricingModelType.DYNAMIC,
        basePrice: new Decimal(1000),
        rules,
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      await pricingService.createConfiguration(config);

      // Calculate price with all discounts applied
      const finalPrice = await pricingService.calculatePrice(config, {
        quantity: 150,
        customerTier: 'gold',
        promoCode: 'SAVE10',
      });

      // Base: 1000
      // After volume (-15%): 850
      // After loyalty (-5%): 807.5
      // After promo (-10): 797.5
      expect(finalPrice.toNumber()).toBeCloseTo(797.5, 1);
    });
  });

  describe('Tiered Revenue Sharing Flow', () => {
    it('should apply tiered commission rates based on performance', async () => {
      const rule: RevenueSharingRule = {
        id: 'rule-tiered-001',
        tenantId,
        name: 'Tiered Commission',
        modelType: RevenueModelType.TIERED,
        baseRate: new Decimal(5),
        tierLevels: [
          { threshold: new Decimal(10000), rate: new Decimal(7) },
          { threshold: new Decimal(50000), rate: new Decimal(10) },
          { threshold: new Decimal(100000), rate: new Decimal(15) },
        ],
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const config: RevenueSharingConfiguration = {
        id: 'config-tiered-001',
        tenantId,
        organizationId,
        name: 'Performance-Based Program',
        rules: [rule],
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      await revenueSharingService.createConfiguration(config);

      // Test different tiers
      const tier1Commission = await revenueSharingService.calculateRevenue(rule, 5000);
      expect(tier1Commission.toNumber()).toBe(250); // 5% of 5000

      const tier2Commission = await revenueSharingService.calculateRevenue(rule, 25000);
      expect(tier2Commission.toNumber()).toBe(1750); // 7% of 25000

      const tier3Commission = await revenueSharingService.calculateRevenue(rule, 75000);
      expect(tier3Commission.toNumber()).toBe(7500); // 10% of 75000

      const tier4Commission = await revenueSharingService.calculateRevenue(rule, 150000);
      expect(tier4Commission.toNumber()).toBe(22500); // 15% of 150000
    });
  });

  describe('Nigeria-First Flow (INV-007)', () => {
    it('should handle Nigeria-specific MLAS operations', async () => {
      // Set up Nigeria-specific revenue sharing
      const nigeriaRule: RevenueSharingRule = {
        id: 'rule-ng-001',
        tenantId,
        name: 'Nigeria Affiliate Commission',
        modelType: RevenueModelType.PERCENTAGE,
        baseRate: new Decimal(12), // Competitive rate for Nigeria market
        conditions: [
          { field: 'region', operator: 'eq', value: 'Nigeria' },
        ],
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const config: RevenueSharingConfiguration = {
        id: 'config-ng-001',
        tenantId,
        organizationId,
        name: 'Nigeria Affiliate Program',
        rules: [nigeriaRule],
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      await revenueSharingService.createConfiguration(config);

      // Calculate commission for Nigeria sale (in NGN)
      const saleAmountNGN = new Decimal(500000); // 500,000 NGN
      const commission = await revenueSharingService.calculateRevenue(
        nigeriaRule,
        saleAmountNGN,
        { region: 'Nigeria' }
      );

      expect(commission.toNumber()).toBe(60000); // 12% of 500,000

      // Set up Nigeria-specific abuse detection
      const nigeriaAbuseRule: AbuseDetectionRule = {
        id: 'rule-ng-abuse-001',
        tenantId,
        name: 'Nigeria Duplicate Order Detection',
        abuseType: AbuseType.DUPLICATE_ORDERS,
        conditions: [
          { metric: 'duplicateOrdersPerHour', operator: 'gt', threshold: 5 },
          { metric: 'region', operator: 'eq', threshold: 'Nigeria' },
        ],
        riskLevel: AbuseRiskLevel.MEDIUM,
        action: AbuseAction.FLAG,
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      await abuseDetectionService.createRule(nigeriaAbuseRule);

      // Test abuse detection for Nigeria
      const alert = await abuseDetectionService.detectAbuse('affiliate-ng-001', {
        tenantId,
        duplicateOrdersPerHour: 10,
        region: 'Nigeria',
      });

      expect(alert).not.toBeNull();
      expect(alert?.action).toBe(AbuseAction.FLAG);
    });

    it('should track attribution through Nigerian channels', async () => {
      // Track attribution through popular Nigerian channels
      const event: AttributionEvent = {
        id: 'event-ng-001',
        tenantId,
        saleId: 'sale-ng-001',
        affiliateId: 'affiliate-ng-001',
        affiliateChain: ['affiliate-ng-001'],
        attributionType: AttributionType.REFERRAL,
        attributionWeight: new Decimal(1),
        touchpoints: [
          {
            affiliateId: 'affiliate-ng-001',
            timestamp: new Date(),
            channel: 'whatsapp', // Very popular in Nigeria
            weight: new Decimal(1),
          },
        ],
        createdAt: new Date(),
      };

      await attributionService.trackAttribution(event);

      const history = await attributionService.getAttributionHistory('affiliate-ng-001');
      expect(history.length).toBe(1);
      expect(history[0].touchpoints[0].channel).toBe('whatsapp');
    });
  });

  describe('MLAS as Infrastructure (INV-006)', () => {
    it('should support multiple tenants with isolated configurations', async () => {
      // Tenant A configuration
      const tenantAConfig: RevenueSharingConfiguration = {
        id: 'config-tenant-a',
        tenantId: 'tenant-a',
        organizationId: 'org-a',
        name: 'Tenant A Program',
        rules: [
          {
            id: 'rule-tenant-a',
            tenantId: 'tenant-a',
            name: 'Tenant A Commission',
            modelType: RevenueModelType.PERCENTAGE,
            baseRate: new Decimal(10),
            isActive: true,
            createdAt: new Date(),
            updatedAt: new Date(),
          },
        ],
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      // Tenant B configuration
      const tenantBConfig: RevenueSharingConfiguration = {
        id: 'config-tenant-b',
        tenantId: 'tenant-b',
        organizationId: 'org-b',
        name: 'Tenant B Program',
        rules: [
          {
            id: 'rule-tenant-b',
            tenantId: 'tenant-b',
            name: 'Tenant B Commission',
            modelType: RevenueModelType.PERCENTAGE,
            baseRate: new Decimal(20),
            isActive: true,
            createdAt: new Date(),
            updatedAt: new Date(),
          },
        ],
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      await revenueSharingService.createConfiguration(tenantAConfig);
      await revenueSharingService.createConfiguration(tenantBConfig);

      // Verify tenant isolation
      const tenantAConfigs = await revenueSharingService.listConfigurations('tenant-a');
      const tenantBConfigs = await revenueSharingService.listConfigurations('tenant-b');

      expect(tenantAConfigs.length).toBe(1);
      expect(tenantBConfigs.length).toBe(1);
      expect(tenantAConfigs[0].rules[0].baseRate.toNumber()).toBe(10);
      expect(tenantBConfigs[0].rules[0].baseRate.toNumber()).toBe(20);
    });
  });
});
