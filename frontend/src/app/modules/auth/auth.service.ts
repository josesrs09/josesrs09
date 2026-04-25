import { ApiBaseService } from '../../core/services/api-base.service';

export interface LoginRequest {
  username: string;
  password: string;
}

export class AuthService extends ApiBaseService {
  login(payload: LoginRequest) {
    return this.post('/auth/login', payload);
  }
}
