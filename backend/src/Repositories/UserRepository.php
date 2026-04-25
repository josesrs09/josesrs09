<?php

namespace App\Repositories;

class UserRepository
{
    private $users = [
        [
            'id' => 1,
            'email' => 'admin@empresa.com',
            'password' => 'admin123',
            'name' => 'Administrador',
            'roles' => ['SUPERADMIN'],
        ],
        [
            'id' => 2,
            'email' => 'contador@empresa.com',
            'password' => 'contador123',
            'name' => 'Contador',
            'roles' => ['CONTADOR'],
        ],
    ];

    public function findByEmail(string $email): ?array
    {
        foreach ($this->users as $user) {
            if ($user['email'] === $email) {
                return $user;
            }
        }
        return null;
    }
}
