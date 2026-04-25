<?php

namespace App\Core;

class Router
{
    private $routes = [];

    public function add(string $method, string $pattern, callable $handler): void
    {
        $this->routes[] = [strtoupper($method), $pattern, $handler];
    }

    public function dispatch(string $method, string $path): void
    {
        foreach ($this->routes as $route) {
            [$routeMethod, $pattern, $handler] = $route;
            if ($routeMethod !== strtoupper($method)) {
                continue;
            }

            $regex = '#^' . preg_replace('#\{([a-zA-Z_][a-zA-Z0-9_]*)\}#', '(?P<$1>[^/]+)', $pattern) . '$#';
            if (preg_match($regex, $path, $matches)) {
                $params = [];
                foreach ($matches as $key => $value) {
                    if (!is_int($key)) {
                        $params[$key] = $value;
                    }
                }
                call_user_func($handler, $params);
                return;
            }
        }

        Response::error('NOT_FOUND', 'Endpoint no encontrado', 404);
    }
}
