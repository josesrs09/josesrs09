<?php

return [
    'app_name' => 'DGII Enterprise API',
    'jwt_secret' => getenv('JWT_SECRET') ?: 'change-me-in-production',
    'token_ttl_minutes' => 15,
];
