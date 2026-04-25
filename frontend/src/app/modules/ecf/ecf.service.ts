import { ApiBaseService } from '../../core/services/api-base.service';

export interface EmitEcfRequest {
  type: '31' | '32' | '33' | '34' | '46' | '47';
  receiver_tax_id?: string;
  reference?: string;
}

export class EcfService extends ApiBaseService {
  validate(payload: EmitEcfRequest) {
    return this.post('/ecf/validate', payload);
  }

  emit(payload: EmitEcfRequest) {
    return this.post('/ecf/emit', payload);
  }

  send(id: number) {
    return this.post(`/ecf/${id}/send`, {});
  }

  status(id: number) {
    return this.get(`/ecf/${id}/status`);
  }
}
