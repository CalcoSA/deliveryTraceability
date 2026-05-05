export interface Parameter {
  IdParameter: number;
  nameParameter: string;
  valueParameter: string;
  createdByParameter: string;
  createdAtParameter: string;
  updatedByParameter: string | null;
  updatedAtParameter: string | null;
}

export interface ParameterCreate {
  nameParameter: string;
  valueParameter: string;
}

export type ParameterUpdate = Partial<ParameterCreate>;