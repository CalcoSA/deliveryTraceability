export type DeliveryReportPeriod = "day" | "week" | "month";

export interface DeliverySettlementReport {
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
  totalRestDays: number;
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