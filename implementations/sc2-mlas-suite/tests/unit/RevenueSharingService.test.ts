/**
 * Unit Tests for Revenue Sharing Service
 * 
 * Tests for revenue sharing configurations and calculations.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import Decimal from 'decimal.js';
import { RevenueSharingService } from '../../src/services/RevenueSharingService';
import {
  RevenueSharingConfiguration,
  RevenueSharingRule,
  RevenueModelType,
} from '../../src/types';

describe('RevenueSharingService', () => {
  let service: RevenueSharingService;
  let tenantId: string;
  let organizationId: string;

  beforeEach(() => {
    service = new RevenueSharingService();
    tenantId = 'tenant-001';
    organizationId = 'org-001';
  });

  describe('createConfiguration', () => {
    it('should create a revenue sharing configuration', async () => {
      const rule: RevenueSharingRule = {
        id: 'rule-001',
        tenantId,
        name: 'Standard Commission',
        modelType: RevenueModelType.PERCENTAGE,
        baseRate: new Decimal(10),
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const config: RevenueSharingConfiguration = {
        id: 'config-001',
        tenantId,
        organizationId,
        name: 'Default Configuration',
        rules: [rule],
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const result = await service.createConfiguration(config);

      expect(result.id).toBe('config-001');
      expect(result.tenantId).toBe(tenantId);
      expect(result.rules.length).toBe(1);
    });

    it('should generate ID if not provided', async () => {
      const rule: RevenueSharingRule = {
        id: 'rule-001',
        tenantId,
        name: 'Auto ID Rule',
        modelType: RevenueModelType.FLAT_RATE,
        baseRate: new Decimal(50),
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const config: RevenueSharingConfiguration = {
        id: '',
        tenantId,
        organizationId,
        name: 'Auto ID Config',
        rules: [rule],
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const result = await service.createConfiguration(config);

      expect(result.id).toBeTruthy();
      expect(result.id.length).toBeGreaterThan(0);
    });
  });

  describe('updateConfiguration', () => {
    it('should update an existing configuration', async () => {
      const rule: RevenueSharingRule = {
        id: 'rule-001',
        tenantId,
        name: 'Original Rule',
        modelType: RevenueModelType.PERCENTAGE,
        baseRate: new Decimal(10),
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const config: RevenueSharingConfiguration = {
        id: 'config-update-001',
        tenantId,
        organizationId,
        name: 'Original Name',
        rules: [rule],
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      await service.createConfiguration(config);

      const updated = await service.updateConfiguration('config-update-001', {
        name: 'Updated Name',
        isActive: false,
      });

      expect(updated.name).toBe('Updated Name');
      expect(updated.isActive).toBe(false);
      expect(updated.id).toBe('config-update-001');
    });

    it('should throw error for non-existent configuration', async () => {
      await expect(
        service.updateConfiguration('non-existent', { name: 'New Name' })
      ).rejects.toThrow('Configuration non-existent not found');
    });
  });

  describe('getConfiguration', () => {
    it('should retrieve a configuration by ID', async () => {
      const rule: RevenueSharingRule = {
        id: 'rule-001',
        tenantId,
        name: 'Get Test Rule',
        modelType: RevenueModelType.PERCENTAGE,
        baseRate: new Decimal(15),
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const config: RevenueSharingConfiguration = {
        id: 'config-get-001',
        tenantId,
        organizationId,
        name: 'Get Test Config',
        rules: [rule],
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      await service.createConfiguration(config);

      const result = await service.getConfiguration('config-get-001');

      expect(result.id).toBe('config-get-001');
      expect(result.name).toBe('Get Test Config');
    });

    it('should throw error for non-existent configuration', async () => {
      await expect(service.getConfiguration('non-existent')).rejects.toThrow(
        'Configuration non-existent not found'
      );
    });
  });

  describe('listConfigurations', () => {
    it('should list configurations for a tenant', async () => {
      const rule: RevenueSharingRule = {
        id: 'rule-001',
        tenantId,
        name: 'List Test Rule',
        modelType: RevenueModelType.PERCENTAGE,
        baseRate: new Decimal(10),
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      await service.createConfiguration({
        id: 'config-list-001',
        tenantId,
        organizationId,
        name: 'Config 1',
        rules: [rule],
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      });

      await service.createConfiguration({
        id: 'config-list-002',
        tenantId,
        organizationId,
        name: 'Config 2',
        rules: [rule],
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      });

      const results = await service.listConfigurations(tenantId);

      expect(results.length).toBe(2);
    });

    it('should filter by tenant ID', async () => {
      const rule: RevenueSharingRule = {
        id: 'rule-001',
        tenantId: 'tenant-a',
        name: 'Tenant A Rule',
        modelType: RevenueModelType.PERCENTAGE,
        baseRate: new Decimal(10),
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      await service.createConfiguration({
        id: 'config-tenant-a',
        tenantId: 'tenant-a',
        organizationId,
        name: 'Tenant A Config',
        rules: [rule],
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      });

      await service.createConfiguration({
        id: 'config-tenant-b',
        tenantId: 'tenant-b',
        organizationId,
        name: 'Tenant B Config',
        rules: [{ ...rule, tenantId: 'tenant-b' }],
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      });

      const results = await service.listConfigurations('tenant-a');

      expect(results.length).toBe(1);
      expect(results[0].tenantId).toBe('tenant-a');
    });
  });

  describe('deleteConfiguration', () => {
    it('should delete a configuration', async () => {
      const rule: RevenueSharingRule = {
        id: 'rule-delete-001',
        tenantId,
        name: 'Delete Test Rule',
        modelType: RevenueModelType.PERCENTAGE,
        baseRate: new Decimal(10),
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      await service.createConfiguration({
        id: 'config-delete-001',
        tenantId,
        organizationId,
        name: 'Delete Test Config',
        rules: [rule],
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      });

      await service.deleteConfiguration('config-delete-001');

      await expect(service.getConfiguration('config-delete-001')).rejects.toThrow();
    });

    it('should throw error for non-existent configuration', async () => {
      await expect(service.deleteConfiguration('non-existent')).rejects.toThrow(
        'Configuration non-existent not found'
      );
    });
  });

  describe('calculateRevenue', () => {
    describe('FLAT_RATE model', () => {
      it('should return flat rate regardless of amount', async () => {
        const rule: RevenueSharingRule = {
          id: 'rule-flat-001',
          tenantId,
          name: 'Flat Rate Rule',
          modelType: RevenueModelType.FLAT_RATE,
          baseRate: new Decimal(100),
          isActive: true,
          createdAt: new Date(),
          updatedAt: new Date(),
        };

        const result = await service.calculateRevenue(rule, 1000);

        expect(result.toNumber()).toBe(100);
      });

      it('should return flat rate for small amounts', async () => {
        const rule: RevenueSharingRule = {
          id: 'rule-flat-002',
          tenantId,
          name: 'Flat Rate Rule',
          modelType: RevenueModelType.FLAT_RATE,
          baseRate: new Decimal(50),
          isActive: true,
          createdAt: new Date(),
          updatedAt: new Date(),
        };

        const result = await service.calculateRevenue(rule, 10);

        expect(result.toNumber()).toBe(50);
      });
    });

    describe('PERCENTAGE model', () => {
      it('should calculate percentage of amount', async () => {
        const rule: RevenueSharingRule = {
          id: 'rule-pct-001',
          tenantId,
          name: 'Percentage Rule',
          modelType: RevenueModelType.PERCENTAGE,
          baseRate: new Decimal(10),
          isActive: true,
          createdAt: new Date(),
          updatedAt: new Date(),
        };

        const result = await service.calculateRevenue(rule, 1000);

        expect(result.toNumber()).toBe(100);
      });

      it('should handle decimal percentages', async () => {
        const rule: RevenueSharingRule = {
          id: 'rule-pct-002',
          tenantId,
          name: 'Decimal Percentage Rule',
          modelType: RevenueModelType.PERCENTAGE,
          baseRate: new Decimal(7.5),
          isActive: true,
          createdAt: new Date(),
          updatedAt: new Date(),
        };

        const result = await service.calculateRevenue(rule, 1000);

        expect(result.toNumber()).toBe(75);
      });

      it('should handle Nigerian Naira amounts (INV-007)', async () => {
        const rule: RevenueSharingRule = {
          id: 'rule-ngn-001',
          tenantId,
          name: 'NGN Commission Rule',
          modelType: RevenueModelType.PERCENTAGE,
          baseRate: new Decimal(15),
          isActive: true,
          createdAt: new Date(),
          updatedAt: new Date(),
        };

        // 100,000 NGN sale
        const result = await service.calculateRevenue(rule, 100000);

        expect(result.toNumber()).toBe(15000);
      });
    });

    describe('TIERED model', () => {
      it('should apply tiered rates based on amount', async () => {
        const rule: RevenueSharingRule = {
          id: 'rule-tier-001',
          tenantId,
          name: 'Tiered Rule',
          modelType: RevenueModelType.TIERED,
          baseRate: new Decimal(5),
          tierLevels: [
            { threshold: new Decimal(1000), rate: new Decimal(10) },
            { threshold: new Decimal(5000), rate: new Decimal(15) },
            { threshold: new Decimal(10000), rate: new Decimal(20) },
          ],
          isActive: true,
          createdAt: new Date(),
          updatedAt: new Date(),
        };

        // Below first tier
        const result1 = await service.calculateRevenue(rule, 500);
        expect(result1.toNumber()).toBe(25); // 5% of 500

        // First tier
        const result2 = await service.calculateRevenue(rule, 2000);
        expect(result2.toNumber()).toBe(200); // 10% of 2000

        // Second tier
        const result3 = await service.calculateRevenue(rule, 7000);
        expect(result3.toNumber()).toBe(1050); // 15% of 7000

        // Third tier
        const result4 = await service.calculateRevenue(rule, 15000);
        expect(result4.toNumber()).toBe(3000); // 20% of 15000
      });
    });

    describe('Cap and minimum', () => {
      it('should apply cap amount', async () => {
        const rule: RevenueSharingRule = {
          id: 'rule-cap-001',
          tenantId,
          name: 'Capped Rule',
          modelType: RevenueModelType.PERCENTAGE,
          baseRate: new Decimal(20),
          capAmount: new Decimal(500),
          isActive: true,
          createdAt: new Date(),
          updatedAt: new Date(),
        };

        const result = await service.calculateRevenue(rule, 10000);

        expect(result.toNumber()).toBe(500); // Capped at 500
      });

      it('should apply minimum amount', async () => {
        const rule: RevenueSharingRule = {
          id: 'rule-min-001',
          tenantId,
          name: 'Minimum Rule',
          modelType: RevenueModelType.PERCENTAGE,
          baseRate: new Decimal(5),
          minAmount: new Decimal(100),
          isActive: true,
          createdAt: new Date(),
          updatedAt: new Date(),
        };

        const result = await service.calculateRevenue(rule, 100);

        expect(result.toNumber()).toBe(100); // Minimum of 100
      });
    });

    describe('Conditional rules', () => {
      it('should apply rule when conditions are met', async () => {
        const rule: RevenueSharingRule = {
          id: 'rule-cond-001',
          tenantId,
          name: 'Conditional Rule',
          modelType: RevenueModelType.PERCENTAGE,
          baseRate: new Decimal(15),
          conditions: [
            { field: 'category', operator: 'eq', value: 'electronics' },
          ],
          isActive: true,
          createdAt: new Date(),
          updatedAt: new Date(),
        };

        const result = await service.calculateRevenue(rule, 1000, {
          category: 'electronics',
        });

        expect(result.toNumber()).toBe(150);
      });

      it('should return zero when conditions are not met', async () => {
        const rule: RevenueSharingRule = {
          id: 'rule-cond-002',
          tenantId,
          name: 'Conditional Rule',
          modelType: RevenueModelType.PERCENTAGE,
          baseRate: new Decimal(15),
          conditions: [
            { field: 'category', operator: 'eq', value: 'electronics' },
          ],
          isActive: true,
          createdAt: new Date(),
          updatedAt: new Date(),
        };

        const result = await service.calculateRevenue(rule, 1000, {
          category: 'fashion',
        });

        expect(result.toNumber()).toBe(0);
      });
    });
  });

  describe('validateConfiguration', () => {
    it('should validate a valid configuration', () => {
      const config: RevenueSharingConfiguration = {
        id: 'config-valid-001',
        tenantId,
        organizationId,
        name: 'Valid Config',
        rules: [
          {
            id: 'rule-001',
            tenantId,
            name: 'Rule',
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

      const result = service.validateConfiguration(config);

      expect(result.valid).toBe(true);
      expect(result.errors.length).toBe(0);
    });

    it('should return errors for invalid configuration', () => {
      const config: RevenueSharingConfiguration = {
        id: 'config-invalid-001',
        tenantId: '',
        organizationId: '',
        name: '',
        rules: [],
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const result = service.validateConfiguration(config);

      expect(result.valid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
      expect(result.errors).toContain('Tenant ID is required');
      expect(result.errors).toContain('Organization ID is required');
      expect(result.errors).toContain('Configuration name is required');
      expect(result.errors).toContain('At least one rule is required');
    });
  });

  describe('toJSON', () => {
    it('should serialize configuration to JSON', () => {
      const config: RevenueSharingConfiguration = {
        id: 'config-json-001',
        tenantId,
        organizationId,
        name: 'JSON Test Config',
        rules: [
          {
            id: 'rule-001',
            tenantId,
            name: 'JSON Rule',
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

      const json = service.toJSON(config);

      expect(json.id).toBe('config-json-001');
      expect(json.name).toBe('JSON Test Config');
      expect(Array.isArray(json.rules)).toBe(true);
    });
  });
});
