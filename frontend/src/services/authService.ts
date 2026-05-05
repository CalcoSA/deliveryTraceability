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
};