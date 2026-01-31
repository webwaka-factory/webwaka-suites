/**
 * SC-2 MLAS Suite Type Definitions
 * 
 * Complete type definitions for the MLAS Suite including revenue sharing,
 * attribution, abuse prevention, and flexible pricing.
 */

import Decimal from 'decimal.js';

// ============================================================================
// Revenue Sharing Types
// ============================================================================

export enum RevenueModelType {
  FLAT_RATE = 'FLAT_RATE',
  PERCENTAGE = 'PERCENTAGE',
  TIERED = 'TIERED',
  PERFORMANCE_BASED = 'PERFORMANCE_BASED',
  HYBRID = 'HYBRID',
}

export interface RevenueSharingRule {
  id: string;
  tenantId: string;
  name: string;
  description?: string;
  modelType: RevenueModelType;
  baseRate: Decimal;
  conditions?: RevenueCondition[];
  tierLevels?: TierLevel[];
  bonusRates?: BonusRate[];
  capAmount?: Decimal;
  minAmount?: Decimal;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface RevenueCondition {
  field: string;
  operator: 'eq' | 'ne' | 'gt' | 'gte' | 'lt' | 'lte' | 'in' | 'contains';
  value: unknown;
}

export interface TierLevel {
  threshold: Decimal;
  rate: Decimal;
}

export interface BonusRate {
  threshold: Decimal;
  rate: Decimal;
  description?: string;
}

export interface RevenueSharingConfiguration {
  id: string;
  tenantId: string;
  organizationId: string;
  name: string;
  description?: string;
  rules: RevenueSharingRule[];
  defaultRule?: RevenueSharingRule;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

// ============================================================================
// Attribution Types
// ============================================================================

export enum AttributionType {
  DIRECT = 'DIRECT',
  REFERRAL = 'REFERRAL',
  MULTI_TOUCH = 'MULTI_TOUCH',
  FIRST_CLICK = 'FIRST_CLICK',
  LAST_CLICK = 'LAST_CLICK',
  LINEAR = 'LINEAR',
}

export interface AttributionConfiguration {
  id: string;
  tenantId: string;
  organizationId: string;
  attributionType: AttributionType;
  lookbackWindow: number; // days
  maxAffiliateChainDepth: number;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface AttributionEvent {
  id: string;
  tenantId: string;
  saleId: string;
  affiliateId: string;
  affiliateChain: string[];
  attributionType: AttributionType;
  attributionWeight: Decimal;
  touchpoints: Touchpoint[];
  createdAt: Date;
}

export interface Touchpoint {
  affiliateId: string;
  timestamp: Date;
  channel: string;
  weight: Decimal;
}

// ============================================================================
// Abuse Prevention Types
// ============================================================================

export enum AbuseType {
  CLICK_FRAUD = 'CLICK_FRAUD',
  COOKIE_STUFFING = 'COOKIE_STUFFING',
  SELF_DEALING = 'SELF_DEALING',
  INCENTIVIZED_TRAFFIC = 'INCENTIVIZED_TRAFFIC',
  BRAND_BIDDING = 'BRAND_BIDDING',
  DUPLICATE_ORDERS = 'DUPLICATE_ORDERS',
  UNUSUAL_PATTERN = 'UNUSUAL_PATTERN',
}

export enum AbuseRiskLevel {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL',
}

export interface AbuseDetectionRule {
  id: string;
  tenantId: string;
  name: string;
  description?: string;
  abuseType: AbuseType;
  conditions: AbuseCondition[];
  riskLevel: AbuseRiskLevel;
  action: AbuseAction;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface AbuseCondition {
  metric: string;
  operator: 'eq' | 'ne' | 'gt' | 'gte' | 'lt' | 'lte' | 'in' | 'contains';
  threshold: unknown;
  timeWindow?: number; // seconds
}

export enum AbuseAction {
  FLAG = 'FLAG',
  HOLD = 'HOLD',
  REJECT = 'REJECT',
  SUSPEND = 'SUSPEND',
  TERMINATE = 'TERMINATE',
}

export interface AbuseAlert {
  id: string;
  tenantId: string;
  affiliateId: string;
  saleId?: string;
  abuseType: AbuseType;
  riskLevel: AbuseRiskLevel;
  detectedRules: string[];
  evidence: Record<string, unknown>;
  action: AbuseAction;
  status: 'OPEN' | 'INVESTIGATING' | 'RESOLVED' | 'DISMISSED';
  createdAt: Date;
  updatedAt: Date;
  resolvedAt?: Date;
}

export interface AbusePattern {
  affiliateId: string;
  metric: string;
  value: Decimal;
  expectedRange: { min: Decimal; max: Decimal };
  deviation: Decimal;
  isAnomaly: boolean;
}

// ============================================================================
// Flexible Pricing Types
// ============================================================================

export enum PricingModelType {
  FIXED = 'FIXED',
  VARIABLE = 'VARIABLE',
  DYNAMIC = 'DYNAMIC',
  CUSTOM = 'CUSTOM',
}

export interface PricingConfiguration {
  id: string;
  tenantId: string;
  organizationId: string;
  actorId: string; // Affiliate or Partner
  actorType: 'AFFILIATE' | 'PARTNER' | 'CLIENT';
  modelType: PricingModelType;
  basePrice: Decimal;
  rules: PricingRule[];
  overrides?: PricingOverride[];
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface PricingRule {
  id: string;
  name: string;
  conditions: PricingCondition[];
  priceAdjustment: Decimal;
  adjustmentType: 'ABSOLUTE' | 'PERCENTAGE';
  priority: number;
}

export interface PricingCondition {
  field: string;
  operator: 'eq' | 'ne' | 'gt' | 'gte' | 'lt' | 'lte' | 'in' | 'contains';
  value: unknown;
}

export interface PricingOverride {
  id: string;
  productId: string;
  price: Decimal;
  validFrom: Date;
  validTo?: Date;
}

export interface DynamicPricingAdjustment {
  id: string;
  tenantId: string;
  affiliateId: string;
  basePrice: Decimal;
  adjustments: PriceAdjustment[];
  finalPrice: Decimal;
  calculatedAt: Date;
}

export interface PriceAdjustment {
  rule: string;
  adjustment: Decimal;
  adjustmentType: 'ABSOLUTE' | 'PERCENTAGE';
}

// ============================================================================
// Configuration UI Types
// ============================================================================

export interface ConfigurationPanel {
  id: string;
  title: string;
  description?: string;
  component: React.ComponentType<any>;
  icon?: string;
  order: number;
}

export interface ConfigurationStep {
  id: string;
  title: string;
  description?: string;
  fields: ConfigurationField[];
  validation?: (data: Record<string, unknown>) => ValidationResult;
}

export interface ConfigurationField {
  id: string;
  name: string;
  label: string;
  type: 'text' | 'number' | 'select' | 'multiselect' | 'checkbox' | 'textarea' | 'json';
  required: boolean;
  defaultValue?: unknown;
  options?: SelectOption[];
  validation?: (value: unknown) => ValidationResult;
  help?: string;
}

export interface SelectOption {
  value: string | number;
  label: string;
  description?: string;
}

export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings?: string[];
}

// ============================================================================
// Dashboard Types
// ============================================================================

export interface DashboardMetric {
  id: string;
  title: string;
  value: string | number;
  unit?: string;
  trend?: 'UP' | 'DOWN' | 'STABLE';
  trendPercent?: Decimal;
  lastUpdated: Date;
}

export interface DashboardChart {
  id: string;
  title: string;
  type: 'line' | 'bar' | 'pie' | 'area';
  data: ChartDataPoint[];
  xAxisLabel?: string;
  yAxisLabel?: string;
}

export interface ChartDataPoint {
  label: string;
  value: Decimal;
  metadata?: Record<string, unknown>;
}

export interface DashboardReport {
  id: string;
  title: string;
  description?: string;
  metrics: DashboardMetric[];
  charts: DashboardChart[];
  generatedAt: Date;
  periodStart: Date;
  periodEnd: Date;
}

// ============================================================================
// API Response Types
// ============================================================================

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: ApiError;
  timestamp: Date;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  limit: number;
  offset: number;
}

// ============================================================================
// Service Interfaces
// ============================================================================

export interface IRevenueSharingService {
  createConfiguration(config: RevenueSharingConfiguration): Promise<RevenueSharingConfiguration>;
  updateConfiguration(id: string, config: Partial<RevenueSharingConfiguration>): Promise<RevenueSharingConfiguration>;
  getConfiguration(id: string): Promise<RevenueSharingConfiguration>;
  listConfigurations(tenantId: string): Promise<RevenueSharingConfiguration[]>;
  deleteConfiguration(id: string): Promise<void>;
  calculateRevenue(rule: RevenueSharingRule, amount: Decimal, context?: Record<string, unknown>): Promise<Decimal>;
}

export interface IAttributionService {
  createConfiguration(config: AttributionConfiguration): Promise<AttributionConfiguration>;
  updateConfiguration(id: string, config: Partial<AttributionConfiguration>): Promise<AttributionConfiguration>;
  getConfiguration(id: string): Promise<AttributionConfiguration>;
  trackAttribution(event: AttributionEvent): Promise<void>;
  getAttributionHistory(affiliateId: string): Promise<AttributionEvent[]>;
}

export interface IAbuseDetectionService {
  createRule(rule: AbuseDetectionRule): Promise<AbuseDetectionRule>;
  updateRule(id: string, rule: Partial<AbuseDetectionRule>): Promise<AbuseDetectionRule>;
  deleteRule(id: string): Promise<void>;
  detectAbuse(affiliateId: string, context: Record<string, unknown>): Promise<AbuseAlert | null>;
  getAbuseAlerts(tenantId: string): Promise<AbuseAlert[]>;
  resolveAlert(alertId: string, resolution: string): Promise<void>;
}

export interface IPricingService {
  createConfiguration(config: PricingConfiguration): Promise<PricingConfiguration>;
  updateConfiguration(id: string, config: Partial<PricingConfiguration>): Promise<PricingConfiguration>;
  getConfiguration(id: string): Promise<PricingConfiguration>;
  calculatePrice(config: PricingConfiguration, context: Record<string, unknown>): Promise<Decimal>;
  listConfigurations(tenantId: string, actorId?: string): Promise<PricingConfiguration[]>;
}
