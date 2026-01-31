/**
 * Attribution Service
 * 
 * Manages multi-level attribution tracking and configuration.
 * Supports multiple attribution models: direct, referral, multi-touch, first-click, last-click, linear.
 */

import Decimal from 'decimal.js';
import { v4 as uuidv4 } from 'uuid';
import {
  AttributionConfiguration,
  AttributionEvent,
  AttributionType,
  Touchpoint,
  IAttributionService,
} from '../types';

export class AttributionService implements IAttributionService {
  private configurations: Map<string, AttributionConfiguration> = new Map();
  private events: Map<string, AttributionEvent> = new Map();

  /**
   * Create an attribution configuration
   */
  async createConfiguration(
    config: AttributionConfiguration,
  ): Promise<AttributionConfiguration> {
    const configuration: AttributionConfiguration = {
      ...config,
      id: config.id || uuidv4(),
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    this.configurations.set(configuration.id, configuration);
    return configuration;
  }

  /**
   * Update an attribution configuration
   */
  async updateConfiguration(
    id: string,
    config: Partial<AttributionConfiguration>,
  ): Promise<AttributionConfiguration> {
    const existing = this.configurations.get(id);
    if (!existing) {
      throw new Error(`Configuration ${id} not found`);
    }

    const updated: AttributionConfiguration = {
      ...existing,
      ...config,
      id: existing.id,
      createdAt: existing.createdAt,
      updatedAt: new Date(),
    };

    this.configurations.set(id, updated);
    return updated;
  }

  /**
   * Get an attribution configuration
   */
  async getConfiguration(id: string): Promise<AttributionConfiguration> {
    const config = this.configurations.get(id);
    if (!config) {
      throw new Error(`Configuration ${id} not found`);
    }
    return config;
  }

  /**
   * Track an attribution event
   */
  async trackAttribution(event: AttributionEvent): Promise<void> {
    const attributionEvent: AttributionEvent = {
      ...event,
      id: event.id || uuidv4(),
      createdAt: new Date(),
    };

    // Calculate weights based on attribution type
    attributionEvent.touchpoints = this.calculateWeights(
      event.touchpoints,
      event.attributionType,
    );

    // Calculate overall attribution weight
    attributionEvent.attributionWeight = this.calculateAttributionWeight(
      attributionEvent.touchpoints,
    );

    this.events.set(attributionEvent.id, attributionEvent);
  }

  /**
   * Get attribution history for an affiliate
   */
  async getAttributionHistory(affiliateId: string): Promise<AttributionEvent[]> {
    return Array.from(this.events.values())
      .filter((e) => e.affiliateId === affiliateId || e.affiliateChain.includes(affiliateId))
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  }

  /**
   * Calculate weights for touchpoints based on attribution type
   */
  private calculateWeights(
    touchpoints: Touchpoint[],
    attributionType: AttributionType,
  ): Touchpoint[] {
    if (!touchpoints || touchpoints.length === 0) {
      return [];
    }

    const weighted = [...touchpoints];

    switch (attributionType) {
      case AttributionType.DIRECT:
        // All credit to last touchpoint
        weighted.forEach((tp, idx) => {
          tp.weight = idx === weighted.length - 1 ? new Decimal(1) : new Decimal(0);
        });
        break;

      case AttributionType.FIRST_CLICK:
        // All credit to first touchpoint
        weighted.forEach((tp, idx) => {
          tp.weight = idx === 0 ? new Decimal(1) : new Decimal(0);
        });
        break;

      case AttributionType.LAST_CLICK:
        // All credit to last touchpoint
        weighted.forEach((tp, idx) => {
          tp.weight = idx === weighted.length - 1 ? new Decimal(1) : new Decimal(0);
        });
        break;

      case AttributionType.LINEAR:
        // Equal credit to all touchpoints
        const equal = new Decimal(1).dividedBy(weighted.length);
        weighted.forEach((tp) => {
          tp.weight = equal;
        });
        break;

      case AttributionType.MULTI_TOUCH:
        // Weighted by recency
        const total = weighted.length * (weighted.length + 1) / 2;
        weighted.forEach((tp, idx) => {
          tp.weight = new Decimal(idx + 1).dividedBy(total);
        });
        break;

      case AttributionType.REFERRAL:
        // Credit to referrer (first touchpoint) and converter (last touchpoint)
        weighted.forEach((tp, idx) => {
          if (idx === 0 || idx === weighted.length - 1) {
            tp.weight = new Decimal(0.5);
          } else {
            tp.weight = new Decimal(0);
          }
        });
        break;
    }

    return weighted;
  }

  /**
   * Calculate overall attribution weight
   */
  private calculateAttributionWeight(touchpoints: Touchpoint[]): Decimal {
    return touchpoints.reduce(
      (sum, tp) => sum.plus(tp.weight),
      new Decimal(0),
    );
  }

  /**
   * Get attribution events by sale
   */
  async getAttributionBySale(saleId: string): Promise<AttributionEvent[]> {
    return Array.from(this.events.values())
      .filter((e) => e.saleId === saleId)
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  }

  /**
   * Validate configuration
   */
  validateConfiguration(config: AttributionConfiguration): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!config.tenantId) {
      errors.push('Tenant ID is required');
    }

    if (!config.organizationId) {
      errors.push('Organization ID is required');
    }

    if (!config.attributionType) {
      errors.push('Attribution type is required');
    }

    if (config.lookbackWindow < 1) {
      errors.push('Lookback window must be at least 1 day');
    }

    if (config.maxAffiliateChainDepth < 1) {
      errors.push('Max affiliate chain depth must be at least 1');
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  /**
   * Serialize event to JSON
   */
  toJSON(event: AttributionEvent): Record<string, unknown> {
    return {
      id: event.id,
      tenantId: event.tenantId,
      saleId: event.saleId,
      affiliateId: event.affiliateId,
      affiliateChain: event.affiliateChain,
      attributionType: event.attributionType,
      attributionWeight: event.attributionWeight.toString(),
      touchpoints: event.touchpoints.map((tp) => ({
        affiliateId: tp.affiliateId,
        timestamp: tp.timestamp.toISOString(),
        channel: tp.channel,
        weight: tp.weight.toString(),
      })),
      createdAt: event.createdAt.toISOString(),
    };
  }
}
