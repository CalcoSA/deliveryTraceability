import type { Parameter, ParameterCreate, ParameterUpdate, } from "../models/Parameter";
import type { ApiResponse } from "../models/ApiResponse";
import { apiClient } from "./apiClient";

export const parameterService = {

  async getAll(): Promise<ApiResponse<Parameter[]>> {
    const response = await apiClient.get<ApiResponse<Parameter[]>>("/parameter/");
    return response.data;
  },

  async create(data: ParameterCreate): Promise<ApiResponse<Parameter>> {
    const response = await apiClient.post<ApiResponse<Parameter>>("/parameter/", data);
    return response.data;
  },

  async update(idParameter: number, data: ParameterUpdate): Promise<ApiResponse<Parameter>> {
    const response = await apiClient.put<ApiResponse<Parameter>>(`/parameter/${idParameter}`, data);
    return response.data;
  },
};