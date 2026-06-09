<?php
// includes/config.php

define('DB_HOST', '127.0.0.1');
define('DB_NAME', 'asag_db');
define('DB_USER', 'root');
define('DB_PASS', 'password');
define('DB_CHARSET', 'utf8mb4');

define('ASAG_API_URL', 'http://127.0.0.1:8000/grade');
define('APP_NAME', 'ASAG System');
define('BASE_URL', 'http://localhost:8080');

function db(): PDO {
    static $pdo = null;
    if ($pdo === null) {
        $dsn = "mysql:host=" . DB_HOST . ";dbname=" . DB_NAME . ";charset=" . DB_CHARSET;
        $options = [
            PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES   => false,
        ];
        $pdo = new PDO($dsn, DB_USER, DB_PASS, $options);
    }
    return $pdo;
}

session_start();

function auth_required(string $role = 'student'): void {
    if (empty($_SESSION['user_id'])) {
        header('Location: ' . BASE_URL . '/index.php');
        exit;
    }
    if ($role === 'admin' && $_SESSION['role'] !== 'admin') {
        header('Location: ' . BASE_URL . '/student/dashboard.php');
        exit;
    }
}

function grade_via_api(string $context, string $reference, string $student, string $type, array $options = []): array {
    $payload = [
        'question_context' => $context,
        'reference_answer' => $reference,
        'student_answer'   => $student,
        'question_type'    => $type,
    ];
    if (!empty($options)) {
        $payload['mcq_options'] = $options;
    }

    $ch = curl_init(ASAG_API_URL);
    curl_setopt_array($ch, [
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => json_encode($payload),
        CURLOPT_HTTPHEADER     => ['Content-Type: application/json'],
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT        => 30,
    ]);
    $response = curl_exec($ch);
    $code     = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($code !== 200 || !$response) {
        return ['error' => 'API unavailable', 'final_weighted_score' => 0];
    }
    return json_decode($response, true) ?? [];
}

function grade_label(float $pct): string {
    if ($pct >= 70) return 'A';
    if ($pct >= 60) return 'B';
    if ($pct >= 50) return 'C';
    if ($pct >= 40) return 'D';
    return 'F';
}
