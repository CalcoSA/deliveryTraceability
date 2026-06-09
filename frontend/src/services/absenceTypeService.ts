import type { AbsenceType } from "../models/DeliveryRecord";
import type { ApiResponse } from "../models/ApiResponse";
import { apiClient } from "./apiClient";

export const absenceTypeService = {
  async getAll(): Promise<ApiResponse<AbsenceType[]>> {
    const response = await apiClient.get<ApiResponse<AbsenceType[]>>("/absence-type/");
    return response.data;
  },
};