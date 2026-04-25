<?php

namespace App\Controllers;

use App\Core\Request;
use App\Core\Response;
use App\Services\CustomerService;

class CustomerController
{
    private $service;

    public function __construct(CustomerService $service)
    {
        $this->service = $service;
    }

    public function list(): void
    {
        Response::success($this->service->all());
    }

    public function create(): void
    {
        $body = Request::json();

        if (empty($body['name']) || empty($body['tax_id'])) {
            Response::error('VALIDATION_ERROR', 'name y tax_id son obligatorios', 422, 'technical');
            return;
        }

        $customer = $this->service->create($body);
        Response::success($customer);
    }
}
