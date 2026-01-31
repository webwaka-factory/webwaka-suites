/**
 * Unit Tests for Attribution Service
 * 
 * Tests for attribution configurations and tracking.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import Decimal from 'decimal.js';
import { AttributionService } from '../../src/services/AttributionService';
import {
  AttributionConfiguration,
  AttributionEvent,
  AttributionType,
} from '../../src/types';

describe('AttributionService', () => {
  let service: AttributionService;
  let tenantId: string;
  let organizationId: string;

  beforeEach(() => {
    service = new AttributionService();
    tenantId = 'tenant-001';
    organizationId = 'org-001';
  });

  describe('createConfiguration', () => {
    it('should create an attribution configuration', async () => {
      const config: AttributionConfiguration = {
        id: 'config-001',
        tenantId,
        organizationId,
        attributionType: AttributionType.LAST_CLICK,
        lookbackWindow: 30,
        maxAffiliateChainDepth: 3,
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const result = await service.createConfiguration(config);

      expect(result.id).toBe('config-001');
      expect(result.attributionType).toBe(AttributionType.LAST_CLICK);
      expect(result.lookbackWindow).toBe(30);
    });

    it('should support different attribution types', async () => {
      const types = [
        AttributionType.DIRECT,
        AttributionType.REFERRAL,
        AttributionType.MULTI_TOUCH,
        AttributionType.FIRST_CLICK,
        AttributionType.LAST_CLICK,
        AttributionType.LINEAR,
      ];

      for (const type of types) {
        const config: AttributionConfiguration = {
          id: `config-${type}`,
          tenantId,
          organizationId,
          attributionType: type,
          lookbackWindow: 30,
          maxAffiliateChainDepth: 3,
          isActive: true,
          createdAt: new Date(),
          updatedAt: new Date(),
        };

        const result = await service.createConfiguration(config);
        expect(result.attributionType).toBe(type);
      }
    });
  });

  describe('updateConfiguration', () => {
    it('should update an existing configuration', async () => {
      const config: AttributionConfiguration = {
        id: 'config-update-001',
        tenantId,
        organizationId,
        attributionType: AttributionType.LAST_CLICK,
        lookbackWindow: 30,
        maxAffiliateChainDepth: 3,
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      await service.createConfiguration(config);

      const updated = await service.updateConfiguration('config-update-001', {
        lookbackWindow: 60,
        attributionType: AttributionType.MULTI_TOUCH,
      });

      expect(updated.lookbackWindow).toBe(60);
      expect(updated.attributionType).toBe(AttributionType.MULTI_TOUCH);
    });

    it('should throw error for non-existent configuration', async () => {
      await expect(
        service.updateConfiguration('non-existent', { lookbackWindow: 60 })
      ).rejects.toThrow('Configuration non-existent not found');
    });
  });

  describe('getConfiguration', () => {
    it('should retrieve a configuration by ID', async () => {
      const config: AttributionConfiguration = {
        id: 'config-get-001',
        tenantId,
        organizationId,
        attributionType: AttributionType.LINEAR,
        lookbackWindow: 14,
        maxAffiliateChainDepth: 5,
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      await service.createConfiguration(config);

      const result = await service.getConfiguration('config-get-001');

      expect(result.id).toBe('config-get-001');
      expect(result.lookbackWindow).toBe(14);
    });

    it('should throw error for non-existent configuration', async () => {
      await expect(service.getConfiguration('non-existent')).rejects.toThrow(
        'Configuration non-existent not found'
      );
    });
  });

  describe('trackAttribution', () => {
    it('should track an attribution event', async () => {
      const event: AttributionEvent = {
        id: 'event-001',
        tenantId,
        saleId: 'sale-001',
        affiliateId: 'affiliate-001',
        affiliateChain: ['affiliate-001'],
        attributionType: AttributionType.DIRECT,
        attributionWeight: new Decimal(1),
        touchpoints: [
          {
            affiliateId: 'affiliate-001',
            timestamp: new Date(),
            channel: 'direct',
            weight: new Decimal(1),
          },
        ],
        createdAt: new Date(),
      };

      await service.trackAttribution(event);

      const history = await service.getAttributionHistory('affiliate-001');

      expect(history.length).toBe(1);
      expect(history[0].saleId).toBe('sale-001');
    });

    it('should track multi-touch attribution', async () => {
      const event: AttributionEvent = {
        id: 'event-multi-001',
        tenantId,
        saleId: 'sale-002',
        affiliateId: 'affiliate-001',
        affiliateChain: ['affiliate-001', 'affiliate-002', 'affiliate-003'],
        attributionType: AttributionType.MULTI_TOUCH,
        attributionWeight: new Decimal(0.33),
        touchpoints: [
          {
            affiliateId: 'affiliate-001',
            timestamp: new Date(Date.now() - 86400000 * 2),
            channel: 'email',
            weight: new Decimal(0.33),
          },
          {
            affiliateId: 'affiliate-002',
            timestamp: new Date(Date.now() - 86400000),
            channel: 'social',
            weight: new Decimal(0.33),
          },
          {
            affiliateId: 'affiliate-003',
            timestamp: new Date(),
            channel: 'direct',
            weight: new Decimal(0.34),
          },
        ],
        createdAt: new Date(),
      };

      await service.trackAttribution(event);

      const history = await service.getAttributionHistory('affiliate-001');

      expect(history.length).toBe(1);
      expect(history[0].touchpoints.length).toBe(3);
    });

    it('should track Nigeria-based affiliates (INV-007)', async () => {
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
            channel: 'whatsapp',  // Popular in Nigeria
            weight: new Decimal(1),
          },
        ],
        createdAt: new Date(),
      };

      await service.trackAttribution(event);

      const history = await service.getAttributionHistory('affiliate-ng-001');

      expect(history.length).toBe(1);
      expect(history[0].touchpoints[0].channel).toBe('whatsapp');
    });
  });

  describe('getAttributionHistory', () => {
    it('should return attribution history for an affiliate', async () => {
      const events: AttributionEvent[] = [
        {
          id: 'event-hist-001',
          tenantId,
          saleId: 'sale-001',
          affiliateId: 'affiliate-hist-001',
          affiliateChain: ['affiliate-hist-001'],
          attributionType: AttributionType.DIRECT,
          attributionWeight: new Decimal(1),
          touchpoints: [],
          createdAt: new Date(),
        },
        {
          id: 'event-hist-002',
          tenantId,
          saleId: 'sale-002',
          affiliateId: 'affiliate-hist-001',
          affiliateChain: ['affiliate-hist-001'],
          attributionType: AttributionType.DIRECT,
          attributionWeight: new Decimal(1),
          touchpoints: [],
          createdAt: new Date(),
        },
      ];

      for (const event of events) {
        await service.trackAttribution(event);
      }

      const history = await service.getAttributionHistory('affiliate-hist-001');

      expect(history.length).toBe(2);
    });

    it('should return empty array for affiliate with no history', async () => {
      const history = await service.getAttributionHistory('non-existent');

      expect(history).toEqual([]);
    });
  });
});
