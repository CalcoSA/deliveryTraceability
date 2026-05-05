export interface PointSale {
  IdPointSale: number;
  codePointSale: string;
  namePointSale: string;
  statusPointSale: boolean;
}

export interface PointSaleCreate {
  codePointSale: string;
  namePointSale: string;
  statusPointSale: boolean;
}

export type PointSaleUpdate = Partial<PointSaleCreate>;