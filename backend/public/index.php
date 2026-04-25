<?php

spl_autoload_register(function ($class) {
    $prefix = 'App\\';
    $baseDir = __DIR__ . '/../src/';

    $len = strlen($prefix);
    if (strncmp($prefix, $class, $len) !== 0) {
        return;
    }

    $relativeClass = substr($class, $len);
    $file = $baseDir . str_replace('\\', '/', $relativeClass) . '.php';

    if (file_exists($file)) {
        require $file;
    }
});

use App\Controllers\AuthController;
use App\Controllers\CustomerController;
use App\Controllers\EcfController;
use App\Core\Request;
use App\Core\Response;
use App\Core\Router;
use App\Repositories\UserRepository;
use App\Services\AuthService;
use App\Services\CustomerService;
use App\Services\EcfService;

$config = require __DIR__ . '/../src/Config/config.php';
$storagePath = realpath(__DIR__ . '/../storage');

$authController = new AuthController(new AuthService(new UserRepository(), $config));
$customerController = new CustomerController(new CustomerService($storagePath));
$ecfController = new EcfController(new EcfService($storagePath));

$router = new Router();

$router->add('GET', '/api/v1/health', function () {
    Response::success(['service' => 'DGII Enterprise API', 'status' => 'ok']);
});

$router->add('POST', '/api/v1/auth/login', function () use ($authController) {
    $authController->login();
});

$router->add('GET', '/api/v1/customers', function () use ($customerController) {
    $customerController->list();
});

$router->add('POST', '/api/v1/customers', function () use ($customerController) {
    $customerController->create();
});

$router->add('POST', '/api/v1/ecf/validate', function () use ($ecfController) {
    $ecfController->validate();
});

$router->add('POST', '/api/v1/ecf/emit', function () use ($ecfController) {
    $ecfController->emit();
});

$router->add('POST', '/api/v1/ecf/{id}/send', function ($params) use ($ecfController) {
    $ecfController->send($params);
});

$router->add('GET', '/api/v1/ecf/{id}/status', function ($params) use ($ecfController) {
    $ecfController->status($params);
});

$router->dispatch(Request::method(), Request::path());
