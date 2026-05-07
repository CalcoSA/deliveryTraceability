import type { PointSale, PointSaleCreate, PointSaleUpdate } from "../models/PointSale";
import type { ApiResponse } from "../models/ApiResponse";
import { apiClient } from "./apiClient";

export const pointSaleService = {

  async getAll(): Promise<ApiResponse<PointSale[]>> {
    const response = await apiClient.get<ApiResponse<PointSale[]>>("/pointSale");
    return response.data;
  },

  async getById(idPointSale: number): Promise<ApiResponse<PointSale>> {
    const response = await apiClient.get<ApiResponse<PointSale>>(`/pointSale/${idPointSale}`);
    return response.data;
  },

  async create(data: PointSaleCreate): Promise<ApiResponse<PointSale>> {
    const response = await apiClient.post<ApiResponse<PointSale>>("/pointSale", data);
    return response.data;
  },

  async update(idPointSale: number, data: PointSaleUpdate): Promise<ApiResponse<PointSale>> {
    const response = await apiClient.put<ApiResponse<PointSale>>(`/pointSale/${idPointSale}`, data);
    return response.data;
  },
};