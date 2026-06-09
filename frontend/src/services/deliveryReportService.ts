import type { DeliverySettlementReport, DeliverySettlementReportFilters, UpdateDeliveryQuantityRequest, UpdateDeliveryQuantityResponse } from "../models/DeliveryReport";
import type { ApiResponse } from "../models/ApiResponse";
import { apiClient } from "./apiClient";

export const deliveryReportService = {
    
  async getSettlementReport(filters: DeliverySettlementReportFilters): Promise<ApiResponse<DeliverySettlementReport[]>> {
    const params: Record<string, string | number> = {
      startDate: filters.startDate,
      endDate: filters.endDate,
      period: filters.period,
    };

    if (filters.IdPointSale && filters.IdPointSale > 0) {
      params.IdPointSale = filters.IdPointSale;
    }

    if (filters.IdDomiciliary && filters.IdDomiciliary > 0) {
      params.IdDomiciliary = filters.IdDomiciliary;
    }

    const response = await apiClient.get<ApiResponse<DeliverySettlementReport[]>>("/delivery-report/settlement", { params });
    return response.data;
  },

  async updateDeliveryQuantityFromReport(IdDeliveryRecord: number, data: UpdateDeliveryQuantityRequest): Promise<ApiResponse<UpdateDeliveryQuantityResponse>> {
    const response = await apiClient.put<ApiResponse<UpdateDeliveryQuantityResponse>>(`/delivery-report/settlement/${IdDeliveryRecord}/quantity`, data);
    return response.data;
  },
};