/**
 * Flexible Pricing Service
 * 
 * Manages flexible pricing configurations for affiliates, partners, and clients.
 * Supports fixed, variable, dynamic, and custom pricing models.
 */

import Decimal from 'decimal.js';
import { v4 as uuidv4 } from 'uuid';
import {
  PricingConfiguration,
  PricingModelType,
  DynamicPricingAdjustment,
  IPricingService,
} from '../types';

export class PricingService implements IPricingService {
  private configurations: Map<string, PricingConfiguration> = new Map();
  private adjustments: Map<string, DynamicPricingAdjustment> = new Map();

  /**
   * Create a pricing configuration
   */
  async createConfiguration(
    config: PricingConfiguration,
  ): Promise<PricingConfiguration> {
    const configuration: PricingConfiguration = {
      ...config,
      id: config.id || uuidv4(),
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    this.configurations.set(configuration.id, configuration);
    return configuration;
  }

  /**
   * Update a pricing configuration
   */
  async updateConfiguration(
    id: string,
    config: Partial<PricingConfiguration>,
  ): Promise<PricingConfiguration> {
    const existing = this.configurations.get(id);
    if (!existing) {
      throw new Error(`Configuration ${id} not found`);
    }

    const updated: PricingConfiguration = {
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
   * Get a pricing configuration
   */
  async getConfiguration(id: string): Promise<PricingConfiguration> {
    const config = this.configurations.get(id);
    if (!config) {
      throw new Error(`Configuration ${id} not found`);
    }
    return config;
  }

  /**
   * Calculate price based on configuration
   */
  async calculatePrice(
    config: PricingConfiguration,
    context: Record<string, unknown>,
  ): Promise<Decimal> {
    let price = config.basePrice;

    // Check for overrides
    if (config.overrides) {
      const override = config.overrides.find((o) => {
        const now = new Date();
        return o.productId === context.productId &&
          now >= o.validFrom &&
          (!o.validTo || now <= o.validTo);
      });

      if (override) {
        return override.price;
      }
    }

    // Apply rules in priority order
    const sortedRules = [...config.rules].sort((a, b) => a.priority - b.priority);

    for (const rule of sortedRules) {
      if (this.ruleApplies(rule, context)) {
        if (rule.adjustmentType === 'ABSOLUTE') {
          price = price.plus(rule.priceAdjustment);
        } else {
          price = price.times(new Decimal(1).plus(rule.priceAdjustment.dividedBy(100)));
        }
      }
    }

    return price;
  }

  /**
   * List configurations for a tenant
   */
  async listConfigurations(tenantId: string, actorId?: string): Promise<PricingConfiguration[]> {
    let configs = Array.from(this.configurations.values()).filter(
      (c) => c.tenantId === tenantId,
    );

    if (actorId) {
      configs = configs.filter((c) => c.actorId === actorId);
    }

    return configs;
  }

  /**
   * Check if a rule applies
   */
  private ruleApplies(rule: { conditions: any[] }, context: Record<string, unknown>): boolean {
    return rule.conditions.every((cond) => {
      const value = context[cond.field];

      switch (cond.operator) {
        case 'eq':
          return value === cond.value;
        case 'ne':
          return value !== cond.value;
        case 'gt':
          return Number(value) > Number(cond.value);
        case 'gte':
          return Number(value) >= Number(cond.value);
        case 'lt':
          return Number(value) < Number(cond.value);
        case 'lte':
          return Number(value) <= Number(cond.value);
        case 'in':
          return Array.isArray(cond.value) && cond.value.includes(value);
        case 'contains':
          return String(value).includes(String(cond.value));
        default:
          return false;
      }
    });
  }

  /**
   * Calculate dynamic pricing with adjustments
   */
  async calculateDynamicPrice(
    config: PricingConfiguration,
    context: Record<string, unknown>,
  ): Promise<DynamicPricingAdjustment> {
    let price = config.basePrice;
    const adjustments = [];

    // Apply rules
    const sortedRules = [...config.rules].sort((a, b) => a.priority - b.priority);

    for (const rule of sortedRules) {
      if (this.ruleApplies(rule, context)) {
        adjustments.push({
          rule: rule.name,
          adjustment: rule.priceAdjustment,
          adjustmentType: rule.adjustmentType,
        });

        if (rule.adjustmentType === 'ABSOLUTE') {
          price = price.plus(rule.priceAdjustment);
        } else {
          price = price.times(new Decimal(1).plus(rule.priceAdjustment.dividedBy(100)));
        }
      }
    }

    const adjustment: DynamicPricingAdjustment = {
      id: uuidv4(),
      tenantId: config.tenantId,
      affiliateId: context.affiliateId as string,
      basePrice: config.basePrice,
      adjustments,
      finalPrice: price,
      calculatedAt: new Date(),
    };

    this.adjustments.set(adjustment.id, adjustment);
    return adjustment;
  }

  /**
   * Get pricing history for an actor
   */
  async getPricingHistory(tenantId: string, actorId: string): Promise<DynamicPricingAdjustment[]> {
    return Array.from(this.adjustments.values())
      .filter((a) => a.tenantId === tenantId && a.affiliateId === actorId)
      .sort((a, b) => b.calculatedAt.getTime() - a.calculatedAt.getTime());
  }

  /**
   * Validate configuration
   */
  validateConfiguration(config: PricingConfiguration): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!config.tenantId) {
      errors.push('Tenant ID is required');
    }

    if (!config.organizationId) {
      errors.push('Organization ID is required');
    }

    if (!config.actorId) {
      errors.push('Actor ID is required');
    }

    if (!config.modelType) {
      errors.push('Pricing model type is required');
    }

    if (config.basePrice.isNegative()) {
      errors.push('Base price cannot be negative');
    }

    if (!config.rules || config.rules.length === 0) {
      errors.push('At least one rule is required');
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  /**
   * Serialize configuration to JSON
   */
  toJSON(config: PricingConfiguration): Record<string, unknown> {
    return {
      id: config.id,
      tenantId: config.tenantId,
      organizationId: config.organizationId,
      actorId: config.actorId,
      actorType: config.actorType,
      modelType: config.modelType,
      basePrice: config.basePrice.toString(),
      rules: config.rules.map((r) => ({
        id: r.id,
        name: r.name,
        priceAdjustment: r.priceAdjustment.toString(),
        adjustmentType: r.adjustmentType,
        priority: r.priority,
      })),
      isActive: config.isActive,
      createdAt: config.createdAt.toISOString(),
      updatedAt: config.updatedAt.toISOString(),
    };
  }
}
