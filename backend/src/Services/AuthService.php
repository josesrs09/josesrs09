<?php

namespace App\Services;

use App\Repositories\UserRepository;

class AuthService
{
    private $users;
    private $config;

    public function __construct(UserRepository $users, array $config)
    {
        $this->users = $users;
        $this->config = $config;
    }

    public function login(string $email, string $password): ?array
    {
        $user = $this->users->findByEmail($email);
        if (!$user || $user['password'] !== $password) {
            return null;
        }

        return [
            'access_token' => $this->makeToken($user),
            'refresh_token' => base64_encode('refresh|' . $user['id'] . '|' . time()),
            'expires_in' => $this->config['token_ttl_minutes'] * 60,
            'user' => [
                'id' => $user['id'],
                'email' => $user['email'],
                'name' => $user['name'],
                'roles' => $user['roles'],
            ],
        ];
    }

    private function makeToken(array $user): string
    {
        $payload = [
            'sub' => $user['id'],
            'email' => $user['email'],
            'roles' => $user['roles'],
            'exp' => time() + ($this->config['token_ttl_minutes'] * 60),
        ];

        return rtrim(strtr(base64_encode(json_encode($payload)), '+/', '-_'), '=');
    }
}
