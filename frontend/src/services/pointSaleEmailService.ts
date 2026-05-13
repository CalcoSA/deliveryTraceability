import type { PointSaleEmail, PointSaleEmailCreate, PointSaleEmailUpdate, } from "../models/PointSaleEmail";
import type { ApiResponse } from "../models/ApiResponse";
import { apiClient } from "./apiClient";

export const pointSaleEmailService = {

  async getAll(): Promise<ApiResponse<PointSaleEmail[]>> {
    const response = await apiClient.get<ApiResponse<PointSaleEmail[]>>("/point-sale-email/");
    return response.data;
  },

  async create(data: PointSaleEmailCreate): Promise<ApiResponse<PointSaleEmail>> {
    const response = await apiClient.post<ApiResponse<PointSaleEmail>>("/point-sale-email/", data);
    return response.data;
  },

  async update(IdPointSaleEmail: number, data: PointSaleEmailUpdate): Promise<ApiResponse<PointSaleEmail>> {
    const response = await apiClient.put<ApiResponse<PointSaleEmail>>(`/point-sale-email/${IdPointSaleEmail}`, data);
    return response.data;
  },

  async delete(IdPointSaleEmail: number): Promise<ApiResponse<Record<string, never>>> {
    const response = await apiClient.delete<ApiResponse<Record<string, never>>>(`/point-sale-email/${IdPointSaleEmail}`);
    return response.data;
  },
};