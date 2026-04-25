# Backend PHP 7.3 - DGII Enterprise API

## Ejecutar local

```bash
php -S 0.0.0.0:8080 -t backend/public
```

## Endpoints incluidos

- `GET /api/v1/health`
- `POST /api/v1/auth/login`
- `GET /api/v1/customers`
- `POST /api/v1/customers`
- `POST /api/v1/ecf/validate`
- `POST /api/v1/ecf/emit`
- `POST /api/v1/ecf/{id}/send`
- `GET /api/v1/ecf/{id}/status`

## Credenciales demo

- `admin@empresa.com` / `admin123`
- `contador@empresa.com` / `contador123`
