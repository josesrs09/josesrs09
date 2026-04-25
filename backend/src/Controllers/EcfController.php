<?php

namespace App\Controllers;

use App\Core\Request;
use App\Core\Response;
use App\Services\EcfService;

class EcfController
{
    private $service;

    public function __construct(EcfService $service)
    {
        $this->service = $service;
    }

    public function validate(): void
    {
        $result = $this->service->validate(Request::json());
        if (!$result['valid']) {
            Response::json([
                'success' => false,
                'data' => ['valid' => false],
                'errors' => $result['errors'],
                'meta' => ['timestamp' => gmdate('c')],
            ], 422);
            return;
        }

        Response::success(['valid' => true]);
    }

    public function emit(): void
    {
        $payload = Request::json();
        $validation = $this->service->validate($payload);
        if (!$validation['valid']) {
            Response::json([
                'success' => false,
                'data' => ['valid' => false],
                'errors' => $validation['errors'],
                'meta' => ['timestamp' => gmdate('c')],
            ], 422);
            return;
        }

        $record = $this->service->emit($payload);
        Response::success($record);
    }

    public function send(array $params): void
    {
        $record = $this->service->send($params['id']);
        if (!$record) {
            Response::error('ECF_NOT_FOUND', 'Documento e-CF no encontrado', 404, 'business');
            return;
        }

        Response::success($record);
    }

    public function status(array $params): void
    {
        $record = $this->service->status($params['id']);
        if (!$record) {
            Response::error('ECF_NOT_FOUND', 'Documento e-CF no encontrado', 404, 'business');
            return;
        }

        Response::success($record);
    }
}
