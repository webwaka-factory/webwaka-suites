/**
 * Abuse Detection Service
 * 
 * Detects and prevents fraudulent activity including click fraud, cookie stuffing,
 * self-dealing, incentivized traffic, brand bidding, and duplicate orders.
 */

import Decimal from 'decimal.js';
import { v4 as uuidv4 } from 'uuid';
import {
  AbuseDetectionRule,
  AbuseAlert,
  AbuseType,
  AbuseRiskLevel,
  AbuseAction,
  AbusePattern,
  IAbuseDetectionService,
} from '../types';

export class AbuseDetectionService implements IAbuseDetectionService {
  private rules: Map<string, AbuseDetectionRule> = new Map();
  private alerts: Map<string, AbuseAlert> = new Map();
  private patterns: Map<string, AbusePattern[]> = new Map();

  /**
   * Create an abuse detection rule
   */
  async createRule(rule: AbuseDetectionRule): Promise<AbuseDetectionRule> {
    const newRule: AbuseDetectionRule = {
      ...rule,
      id: rule.id || uuidv4(),
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    this.rules.set(newRule.id, newRule);
    return newRule;
  }

  /**
   * Update an abuse detection rule
   */
  async updateRule(
    id: string,
    rule: Partial<AbuseDetectionRule>,
  ): Promise<AbuseDetectionRule> {
    const existing = this.rules.get(id);
    if (!existing) {
      throw new Error(`Rule ${id} not found`);
    }

    const updated: AbuseDetectionRule = {
      ...existing,
      ...rule,
      id: existing.id,
      createdAt: existing.createdAt,
      updatedAt: new Date(),
    };

    this.rules.set(id, updated);
    return updated;
  }

  /**
   * Delete an abuse detection rule
   */
  async deleteRule(id: string): Promise<void> {
    const rule = this.rules.get(id);
    if (!rule) {
      throw new Error(`Rule ${id} not found`);
    }
    this.rules.delete(id);
  }

  /**
   * Detect abuse for an affiliate
   */
  async detectAbuse(
    affiliateId: string,
    context: Record<string, unknown>,
  ): Promise<AbuseAlert | null> {
    const activeRules = Array.from(this.rules.values()).filter((r) => r.isActive);
    const detectedRules: string[] = [];
    let maxRiskLevel = AbuseRiskLevel.LOW;

    // Check each rule
    for (const rule of activeRules) {
      if (this.ruleMatches(rule, context)) {
        detectedRules.push(rule.id);

        // Update max risk level
        if (this.getRiskLevelValue(rule.riskLevel) > this.getRiskLevelValue(maxRiskLevel)) {
          maxRiskLevel = rule.riskLevel;
        }
      }
    }

    // If no rules matched, no abuse detected
    if (detectedRules.length === 0) {
      return null;
    }

    // Determine action based on risk level
    let action = AbuseAction.FLAG;
    if (maxRiskLevel === AbuseRiskLevel.HIGH) {
      action = AbuseAction.HOLD;
    } else if (maxRiskLevel === AbuseRiskLevel.CRITICAL) {
      action = AbuseAction.SUSPEND;
    }

    // Create alert
    const alert: AbuseAlert = {
      id: uuidv4(),
      tenantId: context.tenantId as string,
      affiliateId,
      saleId: context.saleId as string | undefined,
      abuseType: this.determineAbuseType(detectedRules),
      riskLevel: maxRiskLevel,
      detectedRules,
      evidence: context,
      action,
      status: 'OPEN',
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    this.alerts.set(alert.id, alert);
    return alert;
  }

  /**
   * Get abuse alerts for a tenant
   */
  async getAbuseAlerts(tenantId: string): Promise<AbuseAlert[]> {
    return Array.from(this.alerts.values())
      .filter((a) => a.tenantId === tenantId)
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  }

  /**
   * Resolve an abuse alert
   */
  async resolveAlert(alertId: string, resolution: string): Promise<void> {
    const alert = this.alerts.get(alertId);
    if (!alert) {
      throw new Error(`Alert ${alertId} not found`);
    }

    alert.status = 'RESOLVED';
    alert.updatedAt = new Date();
    alert.resolvedAt = new Date();
  }

  /**
   * Check if a rule matches the context
   */
  private ruleMatches(rule: AbuseDetectionRule, context: Record<string, unknown>): boolean {
    return rule.conditions.every((cond) => {
      const value = context[cond.metric];
      const threshold = cond.threshold;

      switch (cond.operator) {
        case 'eq':
          return value === threshold;
        case 'ne':
          return value !== threshold;
        case 'gt':
          return Number(value) > Number(threshold);
        case 'gte':
          return Number(value) >= Number(threshold);
        case 'lt':
          return Number(value) < Number(threshold);
        case 'lte':
          return Number(value) <= Number(threshold);
        case 'in':
          return Array.isArray(threshold) && threshold.includes(value);
        case 'contains':
          return String(value).includes(String(threshold));
        default:
          return false;
      }
    });
  }

  /**
   * Determine abuse type from detected rules
   */
  private determineAbuseType(ruleIds: string[]): AbuseType {
    // Get the first rule's abuse type
    const firstRule = Array.from(this.rules.values()).find((r) => ruleIds.includes(r.id));
    return firstRule?.abuseType || AbuseType.UNUSUAL_PATTERN;
  }

  /**
   * Get risk level numeric value for comparison
   */
  private getRiskLevelValue(level: AbuseRiskLevel): number {
    const values: Record<AbuseRiskLevel, number> = {
      [AbuseRiskLevel.LOW]: 1,
      [AbuseRiskLevel.MEDIUM]: 2,
      [AbuseRiskLevel.HIGH]: 3,
      [AbuseRiskLevel.CRITICAL]: 4,
    };
    return values[level];
  }

  /**
   * Detect anomalies in affiliate patterns
   */
  async detectAnomalies(affiliateId: string, metrics: Record<string, Decimal>): Promise<AbusePattern[]> {
    const patterns: AbusePattern[] = [];

    for (const [metric, value] of Object.entries(metrics)) {
      // Get historical data for this metric
      const history = this.patterns.get(`${affiliateId}:${metric}`) || [];

      if (history.length > 0) {
        // Calculate expected range (mean ± 2 standard deviations)
        const mean = history.reduce((sum, p) => sum.plus(p.value), new Decimal(0)).dividedBy(history.length);
        const variance = history.reduce(
          (sum, p) => sum.plus(p.value.minus(mean).pow(2)),
          new Decimal(0),
        ).dividedBy(history.length);
        const stdDev = variance.sqrt();

        const min = mean.minus(stdDev.times(2));
        const max = mean.plus(stdDev.times(2));

        const isAnomaly = value.lessThan(min) || value.greaterThan(max);
        const deviation = isAnomaly ? value.minus(mean).abs() : new Decimal(0);

        patterns.push({
          affiliateId,
          metric,
          value,
          expectedRange: { min, max },
          deviation,
          isAnomaly,
        });
      }
    }

    return patterns;
  }

  /**
   * Validate rule
   */
  validateRule(rule: AbuseDetectionRule): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!rule.tenantId) {
      errors.push('Tenant ID is required');
    }

    if (!rule.name || rule.name.trim().length === 0) {
      errors.push('Rule name is required');
    }

    if (!rule.abuseType) {
      errors.push('Abuse type is required');
    }

    if (!rule.conditions || rule.conditions.length === 0) {
      errors.push('At least one condition is required');
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  /**
   * Serialize alert to JSON
   */
  toJSON(alert: AbuseAlert): Record<string, unknown> {
    return {
      id: alert.id,
      tenantId: alert.tenantId,
      affiliateId: alert.affiliateId,
      saleId: alert.saleId,
      abuseType: alert.abuseType,
      riskLevel: alert.riskLevel,
      detectedRules: alert.detectedRules,
      action: alert.action,
      status: alert.status,
      createdAt: alert.createdAt.toISOString(),
      updatedAt: alert.updatedAt.toISOString(),
      resolvedAt: alert.resolvedAt?.toISOString(),
    };
  }
}
