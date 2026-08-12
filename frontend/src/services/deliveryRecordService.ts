import type { DeliveryRecord, DeliveryRecordBulkCreate, DeliveryRecordFilters } from "../models/DeliveryRecord";
import type { ApiResponse } from "../models/ApiResponse";
import { apiClient } from "./apiClient";

export const deliveryRecordService = {

  async getAll(filters: DeliveryRecordFilters): Promise<ApiResponse<DeliveryRecord[]>> {
    const params: Record<string, string | number> = {};

    if (filters.deliveryDate) {
      params.deliveryDate = filters.deliveryDate;
    }

    if (filters.IdPointSale && filters.IdPointSale > 0) {
      params.IdPointSale = filters.IdPointSale;
    }

    if (filters.IdDomiciliary && filters.IdDomiciliary > 0) {
      params.IdDomiciliary = filters.IdDomiciliary;
    }

    const response = await apiClient.get<ApiResponse<DeliveryRecord[]>>("/delivery-record/", { params });
    return response.data;
  },

  async createBulk(data: DeliveryRecordBulkCreate): Promise<ApiResponse<DeliveryRecord[]>> {
    const response = await apiClient.post<ApiResponse<DeliveryRecord[]>>("/delivery-record/bulk", data);
    return response.data;
  },
};