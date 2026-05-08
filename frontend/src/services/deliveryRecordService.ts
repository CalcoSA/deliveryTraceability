import type { DeliveryRecord, DeliveryRecordBulkCreate, } from "../models/DeliveryRecord";
import type { ApiResponse } from "../models/ApiResponse";
import { apiClient } from "./apiClient";

export const deliveryRecordService = {
  async createBulk(data: DeliveryRecordBulkCreate): Promise<ApiResponse<DeliveryRecord[]>> {
    const response = await apiClient.post<ApiResponse<DeliveryRecord[]>>("/delivery-record/bulk/", data);
    return response.data;
  },
};