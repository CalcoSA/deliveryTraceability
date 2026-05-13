import type { AuthResult, LoginRequest } from "../models/Auth";
import type { ApiResponse } from "../models/ApiResponse";
import { apiClient } from "./apiClient";

export const authService = {
  async login(data: LoginRequest): Promise<ApiResponse<AuthResult>> {
    const response = await apiClient.post<ApiResponse<AuthResult>>("/auth/login", data);
    return response.data;
  },

  async me(): Promise<ApiResponse<AuthResult>> {
    const response = await apiClient.get<ApiResponse<AuthResult>>("/auth/me");
    return response.data;
  },

  async intranetAccess(userLogin: string, ts: string, sig: string): Promise<ApiResponse<AuthResult>> {
    const response = await apiClient.get<ApiResponse<AuthResult>>("/auth/intranet-access", { params: { userLogin, ts, sig, }, });
    return response.data;
  },

  async requestPointSaleCode(emailPointSale: string): Promise<ApiResponse<Record<string, never>>> {
    const response = await apiClient.post<ApiResponse<Record<string, never>>>("/auth/point-sale/request-code", { emailPointSale });
    return response.data;
  },

  async verifyPointSaleCode(emailPointSale: string, code: string): Promise<ApiResponse<AuthResult>> {
    const response = await apiClient.post<ApiResponse<AuthResult>>("/auth/point-sale/verify-code", { emailPointSale, code });
    return response.data;
  },
};