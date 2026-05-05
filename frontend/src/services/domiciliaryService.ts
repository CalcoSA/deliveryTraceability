import type { Domiciliary, DomiciliaryCreate, DomiciliaryUpdate, DomiciliaryFilters } from "../models/Domiciliary";
import type { ApiResponse } from "../models/ApiResponse";
import { apiClient } from "./apiClient";

export const domiciliaryService = {

  async getAll(filters?: DomiciliaryFilters): Promise<ApiResponse<Domiciliary[]>> {
    const params: DomiciliaryFilters = {};

    if (filters?.pointSale && filters.pointSale > 0) {
      params.pointSale = filters.pointSale;
    }

    if (filters?.statusDomiciliary !== undefined) {
      params.statusDomiciliary = filters.statusDomiciliary;
    }

    const response = await apiClient.get<ApiResponse<Domiciliary[]>>("/domiciliary", { params });
    return response.data;
  },

  async getById(idDomiciliary: number): Promise<ApiResponse<Domiciliary>> {
    const response = await apiClient.get<ApiResponse<Domiciliary>>(`/domiciliary/${idDomiciliary}`);
    return response.data;
  },

  async getByDocument(documentDomiciliary: string): Promise<ApiResponse<Domiciliary>> {
    const response = await apiClient.get<ApiResponse<Domiciliary>>(`/domiciliary/document/${documentDomiciliary}`);
    return response.data;
  },

  async create(data: DomiciliaryCreate): Promise<ApiResponse<Domiciliary>> {
    const response = await apiClient.post<ApiResponse<Domiciliary>>("/domiciliary", data);
    return response.data;
  },

  async update(idDomiciliary: number, data: DomiciliaryUpdate): Promise<ApiResponse<Domiciliary>> {
    const response = await apiClient.put<ApiResponse<Domiciliary>>(`/domiciliary/${idDomiciliary}`, data);
    return response.data;
  },
};