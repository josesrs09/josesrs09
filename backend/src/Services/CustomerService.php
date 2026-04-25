<?php

namespace App\Services;

class CustomerService
{
    private $file;

    public function __construct(string $storagePath)
    {
        $this->file = $storagePath . '/customers.json';
        if (!file_exists($this->file)) {
            file_put_contents($this->file, json_encode([]));
        }
    }

    public function all(): array
    {
        return $this->read();
    }

    public function create(array $payload): array
    {
        $items = $this->read();
        $id = count($items) + 1;
        $record = [
            'id' => $id,
            'name' => $payload['name'],
            'tax_id' => $payload['tax_id'],
            'credit_limit' => $payload['credit_limit'] ?? 0,
            'created_at' => gmdate('c'),
        ];
        $items[] = $record;
        $this->write($items);
        return $record;
    }

    private function read(): array
    {
        $content = file_get_contents($this->file);
        $decoded = json_decode($content, true);
        return is_array($decoded) ? $decoded : [];
    }

    private function write(array $data): void
    {
        file_put_contents($this->file, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    }
}
