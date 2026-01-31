/**
 * Revenue Sharing Service
 * 
 * Manages revenue sharing configurations and calculations.
 * Supports multiple revenue models: flat rate, percentage, tiered, performance-based, hybrid.
 */

import Decimal from 'decimal.js';
import { v4 as uuidv4 } from 'uuid';
import {
  RevenueSharingConfiguration,
  RevenueSharingRule,
  RevenueModelType,
  IRevenueSharingService,
} from '../types';

export class RevenueSharingService implements IRevenueSharingService {
  private configurations: Map<string, RevenueSharingConfiguration> = new Map();
  private rules: Map<string, RevenueSharingRule> = new Map();

  /**
   * Create a revenue sharing configuration
   */
  async createConfiguration(
    config: RevenueSharingConfiguration,
  ): Promise<RevenueSharingConfiguration> {
    const configuration: RevenueSharingConfiguration = {
      ...config,
      id: config.id || uuidv4(),
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    this.configurations.set(configuration.id, configuration);

    // Store rules
    for (const rule of configuration.rules) {
      this.rules.set(rule.id, rule);
    }

    return configuration;
  }

  /**
   * Update a revenue sharing configuration
   */
  async updateConfiguration(
    id: string,
    config: Partial<RevenueSharingConfiguration>,
  ): Promise<RevenueSharingConfiguration> {
    const existing = this.configurations.get(id);
    if (!existing) {
      throw new Error(`Configuration ${id} not found`);
    }

    const updated: RevenueSharingConfiguration = {
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
   * Get a revenue sharing configuration
   */
  async getConfiguration(id: string): Promise<RevenueSharingConfiguration> {
    const config = this.configurations.get(id);
    if (!config) {
      throw new Error(`Configuration ${id} not found`);
    }
    return config;
  }

  /**
   * List configurations for a tenant
   */
  async listConfigurations(tenantId: string): Promise<RevenueSharingConfiguration[]> {
    return Array.from(this.configurations.values()).filter(
      (c) => c.tenantId === tenantId,
    );
  }

  /**
   * Delete a configuration
   */
  async deleteConfiguration(id: string): Promise<void> {
    const config = this.configurations.get(id);
    if (!config) {
      throw new Error(`Configuration ${id} not found`);
    }

    // Remove rules
    for (const rule of config.rules) {
      this.rules.delete(rule.id);
    }

    this.configurations.delete(id);
  }

  /**
   * Calculate revenue based on a rule
   */
  async calculateRevenue(
    rule: RevenueSharingRule,
    amount: Decimal | number,
    context?: Record<string, unknown>,
  ): Promise<Decimal> {
    const baseAmount = new Decimal(amount);

    // Check if rule applies
    if (context && rule.conditions && rule.conditions.length > 0) {
      const applies = rule.conditions.every((cond) => this.conditionMet(cond, context));
      if (!applies) {
        return new Decimal(0);
      }
    }

    let revenue = new Decimal(0);

    // Calculate based on model type
    switch (rule.modelType) {
      case RevenueModelType.FLAT_RATE:
        revenue = rule.baseRate;
        break;

      case RevenueModelType.PERCENTAGE:
        revenue = baseAmount.times(rule.baseRate).dividedBy(100);
        break;

      case RevenueModelType.TIERED:
        revenue = this.calculateTieredRevenue(baseAmount, rule);
        break;

      case RevenueModelType.PERFORMANCE_BASED:
        revenue = this.calculatePerformanceRevenue(baseAmount, rule, context);
        break;

      case RevenueModelType.HYBRID:
        revenue = this.calculateHybridRevenue(baseAmount, rule, context);
        break;
    }

    // Apply cap if set
    if (rule.capAmount && revenue.greaterThan(rule.capAmount)) {
      revenue = rule.capAmount;
    }

    // Apply minimum if set
    if (rule.minAmount && revenue.lessThan(rule.minAmount)) {
      revenue = rule.minAmount;
    }

    return revenue;
  }

  /**
   * Calculate tiered revenue
   */
  private calculateTieredRevenue(amount: Decimal, rule: RevenueSharingRule): Decimal {
    if (!rule.tierLevels || rule.tierLevels.length === 0) {
      return amount.times(rule.baseRate).dividedBy(100);
    }

    // Find applicable tier
    let applicableRate = rule.baseRate;
    for (const tier of rule.tierLevels) {
      if (amount.greaterThanOrEqualTo(tier.threshold)) {
        applicableRate = tier.rate;
      }
    }

    return amount.times(applicableRate).dividedBy(100);
  }

  /**
   * Calculate performance-based revenue
   */
  private calculatePerformanceRevenue(
    amount: Decimal,
    rule: RevenueSharingRule,
    context?: Record<string, unknown>,
  ): Decimal {
    let rate = rule.baseRate;

    // Adjust rate based on performance metrics
    if (context?.performanceScore) {
      const score = new Decimal(context.performanceScore as number);
      rate = rule.baseRate.times(score).dividedBy(100);
    }

    // Apply bonus rates if applicable
    if (rule.bonusRates) {
      for (const bonus of rule.bonusRates) {
        if (amount.greaterThanOrEqualTo(bonus.threshold)) {
          rate = bonus.rate;
        }
      }
    }

    return amount.times(rate).dividedBy(100);
  }

  /**
   * Calculate hybrid revenue
   */
  private calculateHybridRevenue(
    amount: Decimal,
    rule: RevenueSharingRule,
    context?: Record<string, unknown>,
  ): Decimal {
    // Start with base rate
    let revenue = amount.times(rule.baseRate).dividedBy(100);

    // Add tiered adjustments
    if (rule.tierLevels) {
      for (const tier of rule.tierLevels) {
        if (amount.greaterThanOrEqualTo(tier.threshold)) {
          revenue = amount.times(tier.rate).dividedBy(100);
        }
      }
    }

    // Add performance adjustments
    if (context?.performanceScore) {
      const score = new Decimal(context.performanceScore as number);
      const adjustment = revenue.times(score).dividedBy(100);
      revenue = revenue.plus(adjustment);
    }

    return revenue;
  }

  /**
   * Check if a condition is met
   */
  private conditionMet(condition: { field: string; operator: string; value: unknown }, data: Record<string, unknown>): boolean {
    const value = data[condition.field];

    switch (condition.operator) {
      case 'eq':
        return value === condition.value;
      case 'ne':
        return value !== condition.value;
      case 'gt':
        return Number(value) > Number(condition.value);
      case 'gte':
        return Number(value) >= Number(condition.value);
      case 'lt':
        return Number(value) < Number(condition.value);
      case 'lte':
        return Number(value) <= Number(condition.value);
      case 'in':
        return Array.isArray(condition.value) && condition.value.includes(value);
      case 'contains':
        return String(value).includes(String(condition.value));
      default:
        return false;
    }
  }

  /**
   * Validate configuration
   */
  validateConfiguration(config: RevenueSharingConfiguration): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!config.tenantId) {
      errors.push('Tenant ID is required');
    }

    if (!config.organizationId) {
      errors.push('Organization ID is required');
    }

    if (!config.name || config.name.trim().length === 0) {
      errors.push('Configuration name is required');
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
  toJSON(config: RevenueSharingConfiguration): Record<string, unknown> {
    return {
      id: config.id,
      tenantId: config.tenantId,
      organizationId: config.organizationId,
      name: config.name,
      description: config.description,
      rules: config.rules.map((r) => ({
        id: r.id,
        name: r.name,
        modelType: r.modelType,
        baseRate: r.baseRate.toString(),
      })),
      isActive: config.isActive,
      createdAt: config.createdAt.toISOString(),
      updatedAt: config.updatedAt.toISOString(),
    };
  }
}
