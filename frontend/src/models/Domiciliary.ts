export interface Domiciliary {
  IdDomiciliary: number;
  documentDomiciliary: string;
  nameDomiciliary: string;
  statusDomiciliary: boolean;
  pointSale: number;
}

export interface DomiciliaryCreate {
  documentDomiciliary: string;
  nameDomiciliary: string;
  statusDomiciliary: boolean;
  pointSale: number;
}

export type DomiciliaryUpdate = Partial<DomiciliaryCreate>;

export interface DomiciliaryFilters {
  pointSale?: number;
  statusDomiciliary?: boolean;
}