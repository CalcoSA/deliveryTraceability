export interface DeliverySettlement {
  IdDeliverySettlement: number;
  IdDeliveryRecord: number;
  IdParameter: number;
  parameterNameSettlement: string;
  parameterValueSettlement: number | string;
  deliveryQuantitySettlement: number;
  totalValueSettlement: number | string;
  createdBySettlement: number;
  createdAtSettlement: string;
  updatedBySettlement: number | null;
  updatedAtSettlement: string | null;
}

export interface DeliveryRecord {
  IdDeliveryRecord: number;
  deliveryDate: string;
  IdPointSale: number;
  IdDomiciliary: number;
  deliveryQuantity: number | null;
  isRestDay: boolean;
  createdByDeliveryRecord: number;
  createdAtDeliveryRecord: string;
  updatedByDeliveryRecord: number | null;
  updatedAtDeliveryRecord: string | null;
  settlement: DeliverySettlement | null;
}

export interface DeliveryRecordBulkItemCreate {
  IdDomiciliary: number;
  deliveryQuantity: number | null;
  isRestDay: boolean;
}

export interface DeliveryRecordBulkCreate {
  deliveryDate: string;
  IdPointSale: number;
  records: DeliveryRecordBulkItemCreate[];
}