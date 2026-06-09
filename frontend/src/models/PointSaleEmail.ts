export interface PointSaleEmail {
  IdPointSaleEmail: number;
  emailPointSale: string;
  statusPointSaleEmail: boolean;
  createdAtPointSaleEmail: string;
  updatedAtPointSaleEmail: string | null;
}

export interface PointSaleEmailCreate {
  emailPointSale: string;
}

export interface PointSaleEmailUpdate {
  emailPointSale?: string;
  statusPointSaleEmail?: boolean;
}