<?php

namespace App\Services;

class EcfService
{
    private $file;

    public function __construct(string $storagePath)
    {
        $this->file = $storagePath . '/ecf_documents.json';
        if (!file_exists($this->file)) {
            file_put_contents($this->file, json_encode([]));
        }
    }

    public function validate(array $payload): array
    {
        $errors = [];

        if (empty($payload['type'])) {
            $errors[] = ['type' => 'technical', 'code' => 'TYPE_REQUIRED', 'message' => 'Tipo e-CF es obligatorio', 'field' => 'type'];
        }

        if (!empty($payload['type']) && !in_array($payload['type'], ['31', '32', '33', '34', '46', '47'], true)) {
            $errors[] = ['type' => 'fiscal', 'code' => 'TYPE_INVALID', 'message' => 'Tipo e-CF no soportado', 'field' => 'type'];
        }

        if (in_array($payload['type'] ?? '', ['31', '46'], true) && empty($payload['receiver_tax_id'])) {
            $errors[] = ['type' => 'fiscal', 'code' => 'RNC_REQUIRED', 'message' => 'RNC receptor/proveedor requerido', 'field' => 'receiver_tax_id'];
        }

        return ['valid' => count($errors) === 0, 'errors' => $errors];
    }

    public function emit(array $payload): array
    {
        $items = $this->read();
        $id = count($items) + 1;
        $record = [
            'id' => $id,
            'type' => $payload['type'],
            'reference' => $payload['reference'] ?? null,
            'receiver_tax_id' => $payload['receiver_tax_id'] ?? null,
            'status' => 'READY_TO_SEND',
            'created_at' => gmdate('c'),
        ];
        $items[] = $record;
        $this->write($items);
        return $record;
    }

    public function send(string $id): ?array
    {
        $items = $this->read();
        foreach ($items as &$item) {
            if ((string) $item['id'] === (string) $id) {
                $item['status'] = 'SENT';
                $item['track_id'] = 'DGII-' . str_pad((string) $item['id'], 6, '0', STR_PAD_LEFT);
                $item['sent_at'] = gmdate('c');
                $this->write($items);
                return $item;
            }
        }
        return null;
    }

    public function status(string $id): ?array
    {
        $items = $this->read();
        foreach ($items as $item) {
            if ((string) $item['id'] === (string) $id) {
                return $item;
            }
        }
        return null;
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
