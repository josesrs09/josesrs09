<?php

namespace App\Controllers;

use App\Core\Request;
use App\Core\Response;
use App\Services\AuthService;

class AuthController
{
    private $authService;

    public function __construct(AuthService $authService)
    {
        $this->authService = $authService;
    }

    public function login(): void
    {
        $body = Request::json();
        if (empty($body['username']) || empty($body['password'])) {
            Response::error('VALIDATION_ERROR', 'username y password son obligatorios', 422, 'technical');
            return;
        }

        $result = $this->authService->login($body['username'], $body['password']);
        if (!$result) {
            Response::error('AUTH_INVALID', 'Credenciales inválidas', 401, 'technical');
            return;
        }

        Response::success($result);
    }
}
