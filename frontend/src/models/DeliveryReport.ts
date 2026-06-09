export type DeliveryReportPeriod = "day" | "week" | "month";

export interface DeliverySettlementReport {
  IdDeliveryRecord?: number;
  periodType: DeliveryReportPeriod;
  periodKey: string;
  periodLabel: string;
  IdPointSale: number;
  codePointSale: string;
  namePointSale: string;
  IdDomiciliary: number;
  documentDomiciliary: string;
  nameDomiciliary: string;
  parameterNameSettlement: string;
  parameterValueSettlement: number | string;
  totalDeliveryQuantity: number;
  totalAbsences: number;
  absenceTypes: string;
  totalValueSettlement: number | string;
  totalRecords: number;
  createdByUsers?: string | null;
}

export interface DeliverySettlementReportFilters {
  startDate: string;
  endDate: string;
  period: DeliveryReportPeriod;
  IdPointSale?: number;
  IdDomiciliary?: number;
}

export interface UpdateDeliveryQuantityRequest {
  deliveryQuantity: number;
}

export interface UpdateDeliveryQuantityResponse {
  IdDeliveryRecord: number;
  deliveryDate: string;
  IdPointSale: number;
  IdDomiciliary: number;
  deliveryQuantity: number;
  IdDeliverySettlement: number;
  IdParameter: number;
  parameterNameSettlement: string;
  parameterValueSettlement: number;
  deliveryQuantitySettlement: number;
  totalValueSettlement: number;
}