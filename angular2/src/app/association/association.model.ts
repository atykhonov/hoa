export class Association {

  constructor(
    public name: string,
    public individual_tax_number?: string,
    public edrpou?: string,
    public certificate?: string,
    public legal_address?: string,
    public physical_address?: string,
    public phone_number?: string,
    public id?: number,
  ) { }
}
