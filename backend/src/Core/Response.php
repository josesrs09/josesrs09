<?php

namespace App\Core;

class Response
{
    public static function json($data, int $status = 200): void
    {
        http_response_code($status);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode($data, JSON_UNESCAPED_UNICODE);
    }

    public static function success($data = [], array $meta = []): void
    {
        self::json([
            'success' => true,
            'data' => $data,
            'errors' => [],
            'meta' => array_merge(['timestamp' => gmdate('c')], $meta),
        ]);
    }

    public static function error(string $code, string $message, int $status = 400, string $type = 'technical', ?string $field = null): void
    {
        self::json([
            'success' => false,
            'data' => new \stdClass(),
            'errors' => [[
                'type' => $type,
                'code' => $code,
                'message' => $message,
                'field' => $field,
            ]],
            'meta' => ['timestamp' => gmdate('c')],
        ], $status);
    }
}
