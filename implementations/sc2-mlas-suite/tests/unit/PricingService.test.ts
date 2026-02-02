/**
 * Unit Tests for Pricing Service
 * 
 * Tests for flexible pricing configurations and calculations.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import Decimal from 'decimal.js';
import { PricingService } from '../../src/services/PricingService';
import {
  PricingConfiguration,
  PricingModelType,
  PricingRule,
} from '../../src/types';

describe('PricingService', () => {
  let service: PricingService;
  let tenantId: string;
  let organizationId: string;

  beforeEach(() => {
    service = new PricingService();
    tenantId = 'tenant-001';
    organizationId = 'org-001';
  });

  describe('createConfiguration', () => {
    it('should create a pricing configuration', async () => {
      const config: PricingConfiguration = {
        id: 'config-001',
        tenantId,
        organizationId,
        actorId: 'affiliate-001',
        actorType: 'AFFILIATE',
        modelType: PricingModelType.FIXED,
        basePrice: new Decimal(100),
        rules: [],
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const result = await service.createConfiguration(config);

      expect(result.id).toBe('config-001');
      expect(result.modelType).toBe(PricingModelType.FIXED);
      expect(result.basePrice.toNumber()).toBe(100);
    });

    it('should support different pricing model types', async () => {
      const types = [
        PricingModelType.FIXED,
        PricingModelType.VARIABLE,
        PricingModelType.DYNAMIC,
        PricingModelType.CUSTOM,
      ];

      for (const type of types) {
        const config: PricingConfiguration = {
          id: `config-${type}`,
          tenantId,
          organizationId,
          actorId: 'affiliate-001',
          actorType: 'AFFILIATE',
          modelType: type,
          basePrice: new Decimal(100),
          rules: [],
          isActive: true,
          createdAt: new Date(),
          updatedAt: new Date(),
        };

        const result = await service.createConfiguration(config);
        expect(result.modelType).toBe(type);
      }
    });

    it('should support different actor types', async () => {
      const actorTypes: Array<'AFFILIATE' | 'PARTNER' | 'CLIENT'> = [
        'AFFILIATE',
        'PARTNER',
        'CLIENT',
      ];

      for (const actorType of actorTypes) {
        const config: PricingConfiguration = {
          id: `config-${actorType}`,
          tenantId,
          organizationId,
          actorId: `${actorType.toLowerCase()}-001`,
          actorType,
          modelType: PricingModelType.FIXED,
          basePrice: new Decimal(100),
          rules: [],
          isActive: true,
          createdAt: new Date(),
          updatedAt: new Date(),
        };

        const result = await service.createConfiguration(config);
        expect(result.actorType).toBe(actorType);
      }
    });
  });

  describe('updateConfiguration', () => {
    it('should update an existing configuration', async () => {
      const config: PricingConfiguration = {
        id: 'config-update-001',
        tenantId,
        organizationId,
        actorId: 'affiliate-001',
        actorType: 'AFFILIATE',
        modelType: PricingModelType.FIXED,
        basePrice: new Decimal(100),
        rules: [],
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      await service.createConfiguration(config);

      const updated = await service.updateConfiguration('config-update-001', {
        basePrice: new Decimal(150),
        modelType: PricingModelType.VARIABLE,
      });

      expect(updated.basePrice.toNumber()).toBe(150);
      expect(updated.modelType).toBe(PricingModelType.VARIABLE);
    });

    it('should throw error for non-existent configuration', async () => {
      await expect(
        service.updateConfiguration('non-existent', { basePrice: new Decimal(100) })
      ).rejects.toThrow('Configuration non-existent not found');
    });
  });

  describe('getConfiguration', () => {
    it('should retrieve a configuration by ID', async () => {
      const config: PricingConfiguration = {
        id: 'config-get-001',
        tenantId,
        organizationId,
        actorId: 'affiliate-001',
        actorType: 'AFFILIATE',
        modelType: PricingModelType.DYNAMIC,
        basePrice: new Decimal(200),
        rules: [],
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      await service.createConfiguration(config);

      const result = await service.getConfiguration('config-get-001');

      expect(result.id).toBe('config-get-001');
      expect(result.basePrice.toNumber()).toBe(200);
    });

    it('should throw error for non-existent configuration', async () => {
      await expect(service.getConfiguration('non-existent')).rejects.toThrow(
        'Configuration non-existent not found'
      );
    });
  });

  describe('calculatePrice', () => {
    it('should return base price for FIXED model', async () => {
      const config: PricingConfiguration = {
        id: 'config-fixed-001',
        tenantId,
        organizationId,
        actorId: 'affiliate-001',
        actorType: 'AFFILIATE',
        modelType: PricingModelType.FIXED,
        basePrice: new Decimal(100),
        rules: [],
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const price = await service.calculatePrice(config, {});

      expect(price.toNumber()).toBe(100);
    });

    it('should apply percentage adjustments', async () => {
      const rule: PricingRule = {
        id: 'rule-pct-001',
        name: 'Volume Discount',
        conditions: [
          { field: 'quantity', operator: 'gte', value: 10 },
        ],
        priceAdjustment: new Decimal(-10),
        adjustmentType: 'PERCENTAGE',
        priority: 1,
      };

      const config: PricingConfiguration = {
        id: 'config-pct-001',
        tenantId,
        organizationId,
        actorId: 'affiliate-001',
        actorType: 'AFFILIATE',
        modelType: PricingModelType.VARIABLE,
        basePrice: new Decimal(100),
        rules: [rule],
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const price = await service.calculatePrice(config, { quantity: 15 });

      expect(price.toNumber()).toBe(90); // 100 - 10%
    });

    it('should apply absolute adjustments', async () => {
      const rule: PricingRule = {
        id: 'rule-abs-001',
        name: 'Flat Discount',
        conditions: [
          { field: 'isVIP', operator: 'eq', value: true },
        ],
        priceAdjustment: new Decimal(-25),
        adjustmentType: 'ABSOLUTE',
        priority: 1,
      };

      const config: PricingConfiguration = {
        id: 'config-abs-001',
        tenantId,
        organizationId,
        actorId: 'affiliate-001',
        actorType: 'AFFILIATE',
        modelType: PricingModelType.VARIABLE,
        basePrice: new Decimal(100),
        rules: [rule],
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const price = await service.calculatePrice(config, { isVIP: true });

      expect(price.toNumber()).toBe(75); // 100 - 25
    });

    it('should apply multiple rules by priority', async () => {
      const rules: PricingRule[] = [
        {
          id: 'rule-multi-001',
          name: 'Volume Discount',
          conditions: [
            { field: 'quantity', operator: 'gte', value: 10 },
          ],
          priceAdjustment: new Decimal(-10),
          adjustmentType: 'PERCENTAGE',
          priority: 1,
        },
        {
          id: 'rule-multi-002',
          name: 'VIP Discount',
          conditions: [
            { field: 'isVIP', operator: 'eq', value: true },
          ],
          priceAdjustment: new Decimal(-5),
          adjustmentType: 'ABSOLUTE',
          priority: 2,
        },
      ];

      const config: PricingConfiguration = {
        id: 'config-multi-001',
        tenantId,
        organizationId,
        actorId: 'affiliate-001',
        actorType: 'AFFILIATE',
        modelType: PricingModelType.VARIABLE,
        basePrice: new Decimal(100),
        rules,
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const price = await service.calculatePrice(config, {
        quantity: 15,
        isVIP: true,
      });

      // 100 - 10% = 90, then 90 - 5 = 85
      expect(price.toNumber()).toBe(85);
    });

    it('should handle Nigeria Naira pricing (INV-007)', async () => {
      const config: PricingConfiguration = {
        id: 'config-ngn-001',
        tenantId,
        organizationId,
        actorId: 'affiliate-ng-001',
        actorType: 'AFFILIATE',
        modelType: PricingModelType.FIXED,
        basePrice: new Decimal(50000), // 50,000 NGN
        rules: [],
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const price = await service.calculatePrice(config, {
        currency: 'NGN',
        region: 'Nigeria',
      });

      expect(price.toNumber()).toBe(50000);
    });

    it('should apply region-based pricing rules', async () => {
      const rule: PricingRule = {
        id: 'rule-region-001',
        name: 'Nigeria Discount',
        conditions: [
          { field: 'region', operator: 'eq', value: 'Nigeria' },
        ],
        priceAdjustment: new Decimal(-15),
        adjustmentType: 'PERCENTAGE',
        priority: 1,
      };

      const config: PricingConfiguration = {
        id: 'config-region-001',
        tenantId,
        organizationId,
        actorId: 'affiliate-001',
        actorType: 'AFFILIATE',
        modelType: PricingModelType.VARIABLE,
        basePrice: new Decimal(100000), // 100,000 NGN
        rules: [rule],
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const price = await service.calculatePrice(config, { region: 'Nigeria' });

      expect(price.toNumber()).toBe(85000); // 100,000 - 15%
    });
  });

  describe('listConfigurations', () => {
    it('should list configurations for a tenant', async () => {
      const configs: PricingConfiguration[] = [
        {
          id: 'config-list-001',
          tenantId,
          organizationId,
          actorId: 'affiliate-001',
          actorType: 'AFFILIATE',
          modelType: PricingModelType.FIXED,
          basePrice: new Decimal(100),
          rules: [],
          isActive: true,
          createdAt: new Date(),
          updatedAt: new Date(),
        },
        {
          id: 'config-list-002',
          tenantId,
          organizationId,
          actorId: 'affiliate-002',
          actorType: 'AFFILIATE',
          modelType: PricingModelType.VARIABLE,
          basePrice: new Decimal(150),
          rules: [],
          isActive: true,
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ];

      for (const config of configs) {
        await service.createConfiguration(config);
      }

      const results = await service.listConfigurations(tenantId);

      expect(results.length).toBe(2);
    });

    it('should filter by actor ID', async () => {
      const configs: PricingConfiguration[] = [
        {
          id: 'config-actor-001',
          tenantId,
          organizationId,
          actorId: 'affiliate-001',
          actorType: 'AFFILIATE',
          modelType: PricingModelType.FIXED,
          basePrice: new Decimal(100),
          rules: [],
          isActive: true,
          createdAt: new Date(),
          updatedAt: new Date(),
        },
        {
          id: 'config-actor-002',
          tenantId,
          organizationId,
          actorId: 'affiliate-002',
          actorType: 'AFFILIATE',
          modelType: PricingModelType.FIXED,
          basePrice: new Decimal(100),
          rules: [],
          isActive: true,
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ];

      for (const config of configs) {
        await service.createConfiguration(config);
      }

      const results = await service.listConfigurations(tenantId, 'affiliate-001');

      expect(results.length).toBe(1);
      expect(results[0].actorId).toBe('affiliate-001');
    });
  });
});
