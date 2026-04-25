import { ApiBaseService } from '../../core/services/api-base.service';

export interface CreateCustomerRequest {
  name: string;
  tax_id: string;
  credit_limit?: number;
}

export class CustomersService extends ApiBaseService {
  list() {
    return this.get('/customers');
  }

  create(payload: CreateCustomerRequest) {
    return this.post('/customers', payload);
  }
}
