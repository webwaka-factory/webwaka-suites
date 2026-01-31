/**
 * Unit Tests for Abuse Detection Service
 * 
 * Tests for abuse detection rules, alerts, and anomaly detection.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import Decimal from 'decimal.js';
import { AbuseDetectionService } from '../../src/services/AbuseDetectionService';
import {
  AbuseDetectionRule,
  AbuseType,
  AbuseRiskLevel,
  AbuseAction,
} from '../../src/types';

describe('AbuseDetectionService', () => {
  let service: AbuseDetectionService;
  let tenantId: string;

  beforeEach(() => {
    service = new AbuseDetectionService();
    tenantId = 'tenant-001';
  });

  describe('createRule', () => {
    it('should create an abuse detection rule', async () => {
      const rule: AbuseDetectionRule = {
        id: 'rule-001',
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

      const result = await service.createRule(rule);

      expect(result.id).toBe('rule-001');
      expect(result.name).toBe('Click Fraud Detection');
      expect(result.abuseType).toBe(AbuseType.CLICK_FRAUD);
    });

    it('should generate ID if not provided', async () => {
      const rule: AbuseDetectionRule = {
        id: '',
        tenantId,
        name: 'Auto ID Rule',
        abuseType: AbuseType.COOKIE_STUFFING,
        conditions: [
          { metric: 'cookieCount', operator: 'gt', threshold: 50 },
        ],
        riskLevel: AbuseRiskLevel.MEDIUM,
        action: AbuseAction.FLAG,
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const result = await service.createRule(rule);

      expect(result.id).toBeTruthy();
      expect(result.id.length).toBeGreaterThan(0);
    });
  });

  describe('updateRule', () => {
    it('should update an existing rule', async () => {
      const rule: AbuseDetectionRule = {
        id: 'rule-update-001',
        tenantId,
        name: 'Original Rule',
        abuseType: AbuseType.SELF_DEALING,
        conditions: [
          { metric: 'selfReferrals', operator: 'gt', threshold: 5 },
        ],
        riskLevel: AbuseRiskLevel.MEDIUM,
        action: AbuseAction.FLAG,
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      await service.createRule(rule);

      const updated = await service.updateRule('rule-update-001', {
        name: 'Updated Rule',
        riskLevel: AbuseRiskLevel.HIGH,
        action: AbuseAction.SUSPEND,
      });

      expect(updated.name).toBe('Updated Rule');
      expect(updated.riskLevel).toBe(AbuseRiskLevel.HIGH);
      expect(updated.action).toBe(AbuseAction.SUSPEND);
    });

    it('should throw error for non-existent rule', async () => {
      await expect(
        service.updateRule('non-existent', { name: 'New Name' })
      ).rejects.toThrow('Rule non-existent not found');
    });
  });

  describe('deleteRule', () => {
    it('should delete a rule', async () => {
      const rule: AbuseDetectionRule = {
        id: 'rule-delete-001',
        tenantId,
        name: 'Delete Test Rule',
        abuseType: AbuseType.BRAND_BIDDING,
        conditions: [
          { metric: 'brandKeywords', operator: 'gt', threshold: 0 },
        ],
        riskLevel: AbuseRiskLevel.HIGH,
        action: AbuseAction.REJECT,
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      await service.createRule(rule);
      await service.deleteRule('rule-delete-001');

      await expect(
        service.updateRule('rule-delete-001', { name: 'Test' })
      ).rejects.toThrow();
    });

    it('should throw error for non-existent rule', async () => {
      await expect(service.deleteRule('non-existent')).rejects.toThrow(
        'Rule non-existent not found'
      );
    });
  });

  describe('detectAbuse', () => {
    it('should detect abuse when rules match', async () => {
      const rule: AbuseDetectionRule = {
        id: 'rule-detect-001',
        tenantId,
        name: 'High Click Rate Detection',
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

      await service.createRule(rule);

      const alert = await service.detectAbuse('affiliate-001', {
        tenantId,
        clickRate: 150,
      });

      expect(alert).not.toBeNull();
      expect(alert?.abuseType).toBe(AbuseType.CLICK_FRAUD);
      expect(alert?.riskLevel).toBe(AbuseRiskLevel.HIGH);
      expect(alert?.action).toBe(AbuseAction.HOLD);
    });

    it('should return null when no rules match', async () => {
      const rule: AbuseDetectionRule = {
        id: 'rule-nomatch-001',
        tenantId,
        name: 'High Click Rate Detection',
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

      await service.createRule(rule);

      const alert = await service.detectAbuse('affiliate-001', {
        tenantId,
        clickRate: 50,
      });

      expect(alert).toBeNull();
    });

    it('should detect multiple abuse types', async () => {
      const clickFraudRule: AbuseDetectionRule = {
        id: 'rule-multi-001',
        tenantId,
        name: 'Click Fraud',
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

      const selfDealingRule: AbuseDetectionRule = {
        id: 'rule-multi-002',
        tenantId,
        name: 'Self Dealing',
        abuseType: AbuseType.SELF_DEALING,
        conditions: [
          { metric: 'selfReferrals', operator: 'gt', threshold: 5 },
        ],
        riskLevel: AbuseRiskLevel.CRITICAL,
        action: AbuseAction.SUSPEND,
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      await service.createRule(clickFraudRule);
      await service.createRule(selfDealingRule);

      const alert = await service.detectAbuse('affiliate-001', {
        tenantId,
        clickRate: 150,
        selfReferrals: 10,
      });

      expect(alert).not.toBeNull();
      expect(alert?.riskLevel).toBe(AbuseRiskLevel.CRITICAL);
      expect(alert?.detectedRules.length).toBe(2);
    });

    it('should skip inactive rules', async () => {
      const rule: AbuseDetectionRule = {
        id: 'rule-inactive-001',
        tenantId,
        name: 'Inactive Rule',
        abuseType: AbuseType.CLICK_FRAUD,
        conditions: [
          { metric: 'clickRate', operator: 'gt', threshold: 100 },
        ],
        riskLevel: AbuseRiskLevel.HIGH,
        action: AbuseAction.HOLD,
        isActive: false,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      await service.createRule(rule);

      const alert = await service.detectAbuse('affiliate-001', {
        tenantId,
        clickRate: 150,
      });

      expect(alert).toBeNull();
    });

    it('should handle Nigeria-specific fraud patterns (INV-007)', async () => {
      const rule: AbuseDetectionRule = {
        id: 'rule-ng-001',
        tenantId,
        name: 'Nigeria Duplicate Order Detection',
        abuseType: AbuseType.DUPLICATE_ORDERS,
        conditions: [
          { metric: 'duplicateOrderCount', operator: 'gt', threshold: 3 },
          { metric: 'region', operator: 'eq', threshold: 'Nigeria' },
        ],
        riskLevel: AbuseRiskLevel.HIGH,
        action: AbuseAction.HOLD,
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      await service.createRule(rule);

      const alert = await service.detectAbuse('affiliate-ng-001', {
        tenantId,
        duplicateOrderCount: 5,
        region: 'Nigeria',
      });

      expect(alert).not.toBeNull();
      expect(alert?.abuseType).toBe(AbuseType.DUPLICATE_ORDERS);
    });
  });

  describe('getAbuseAlerts', () => {
    it('should return alerts for a tenant', async () => {
      const rule: AbuseDetectionRule = {
        id: 'rule-alerts-001',
        tenantId,
        name: 'Alert Test Rule',
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

      await service.createRule(rule);

      await service.detectAbuse('affiliate-001', { tenantId, clickRate: 150 });
      await service.detectAbuse('affiliate-002', { tenantId, clickRate: 200 });

      const alerts = await service.getAbuseAlerts(tenantId);

      expect(alerts.length).toBe(2);
    });

    it('should filter alerts by tenant', async () => {
      const rule: AbuseDetectionRule = {
        id: 'rule-filter-001',
        tenantId: 'tenant-a',
        name: 'Tenant A Rule',
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

      await service.createRule(rule);

      await service.detectAbuse('affiliate-001', { tenantId: 'tenant-a', clickRate: 150 });

      const alertsA = await service.getAbuseAlerts('tenant-a');
      const alertsB = await service.getAbuseAlerts('tenant-b');

      expect(alertsA.length).toBe(1);
      expect(alertsB.length).toBe(0);
    });
  });

  describe('resolveAlert', () => {
    it('should resolve an alert', async () => {
      const rule: AbuseDetectionRule = {
        id: 'rule-resolve-001',
        tenantId,
        name: 'Resolve Test Rule',
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

      await service.createRule(rule);

      const alert = await service.detectAbuse('affiliate-001', {
        tenantId,
        clickRate: 150,
      });

      expect(alert).not.toBeNull();

      await service.resolveAlert(alert!.id, 'False positive');

      const alerts = await service.getAbuseAlerts(tenantId);
      const resolvedAlert = alerts.find((a) => a.id === alert!.id);

      expect(resolvedAlert?.status).toBe('RESOLVED');
      expect(resolvedAlert?.resolvedAt).toBeDefined();
    });

    it('should throw error for non-existent alert', async () => {
      await expect(
        service.resolveAlert('non-existent', 'Test')
      ).rejects.toThrow('Alert non-existent not found');
    });
  });

  describe('detectAnomalies', () => {
    it('should detect anomalies in metrics', async () => {
      const metrics = {
        clickRate: new Decimal(500),
        conversionRate: new Decimal(0.01),
      };

      const patterns = await service.detectAnomalies('affiliate-001', metrics);

      // Without historical data, should return empty patterns
      expect(Array.isArray(patterns)).toBe(true);
    });
  });

  describe('validateRule', () => {
    it('should validate a valid rule', () => {
      const rule: AbuseDetectionRule = {
        id: 'rule-valid-001',
        tenantId,
        name: 'Valid Rule',
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

      const result = service.validateRule(rule);

      expect(result.valid).toBe(true);
      expect(result.errors.length).toBe(0);
    });

    it('should return errors for invalid rule', () => {
      const rule: AbuseDetectionRule = {
        id: 'rule-invalid-001',
        tenantId: '',
        name: '',
        abuseType: '' as AbuseType,
        conditions: [],
        riskLevel: AbuseRiskLevel.HIGH,
        action: AbuseAction.HOLD,
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const result = service.validateRule(rule);

      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Tenant ID is required');
      expect(result.errors).toContain('Rule name is required');
      expect(result.errors).toContain('At least one condition is required');
    });
  });

  describe('toJSON', () => {
    it('should serialize alert to JSON', async () => {
      const rule: AbuseDetectionRule = {
        id: 'rule-json-001',
        tenantId,
        name: 'JSON Test Rule',
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

      await service.createRule(rule);

      const alert = await service.detectAbuse('affiliate-001', {
        tenantId,
        clickRate: 150,
      });

      expect(alert).not.toBeNull();

      const json = service.toJSON(alert!);

      expect(json.id).toBe(alert!.id);
      expect(json.abuseType).toBe(AbuseType.CLICK_FRAUD);
      expect(json.status).toBe('OPEN');
    });
  });
});
