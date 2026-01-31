/**
 * SC-2 MLAS Suite - Main Entry Point
 * 
 * Exports all services, models, and types for the MLAS Suite.
 */

// Export types
export * from './types';

// Export services
export { RevenueSharingService } from './services/RevenueSharingService';
export { AttributionService } from './services/AttributionService';
export { AbuseDetectionService } from './services/AbuseDetectionService';
export { PricingService } from './services/PricingService';

/**
 * MLAS Suite Module initialization
 */
export class MLASSuiteModule {
  private revenueSharingService: any;
  private attributionService: any;
  private abuseDetectionService: any;
  private pricingService: any;

  constructor() {
    this.revenueSharingService = new (require('./services/RevenueSharingService').RevenueSharingService)();
    this.attributionService = new (require('./services/AttributionService').AttributionService)();
    this.abuseDetectionService = new (require('./services/AbuseDetectionService').AbuseDetectionService)();
    this.pricingService = new (require('./services/PricingService').PricingService)();
  }

  getRevenueSharingService() {
    return this.revenueSharingService;
  }

  getAttributionService() {
    return this.attributionService;
  }

  getAbuseDetectionService() {
    return this.abuseDetectionService;
  }

  getPricingService() {
    return this.pricingService;
  }
}

export default MLASSuiteModule;
