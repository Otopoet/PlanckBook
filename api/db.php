<?php
/**
 * Shared bootstrap for every PLANCK API endpoint: config, PDO, tiny helpers.
 * All endpoints are same-origin (the site and /api both live under /planck/),
 * so no CORS handling is needed.
 */
declare(strict_types=1);

function pk_config(): array {
    static $cfg = null;
    if ($cfg === null) {
        $path = __DIR__ . '/config.php';
        if (!is_file($path)) {
            http_response_code(500);
            exit('config.php missing — copy config.sample.php and fill it in.');
        }
        $cfg = require $path;
    }
    return $cfg;
}

function pk_db(): PDO {
    static $pdo = null;
    if ($pdo === null) {
        $c = pk_config();
        $dsn = "mysql:host={$c['db_host']};dbname={$c['db_name']};charset=utf8mb4";
        $pdo = new PDO($dsn, $c['db_user'], $c['db_pass'], [
            PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES   => false,
        ]);
    }
    return $pdo;
}

/** Decode a JSON request body (also accepts sendBeacon's text/plain payload). */
function pk_json_input(): array {
    $raw = file_get_contents('php://input') ?: '';
    $data = json_decode($raw, true);
    return is_array($data) ? $data : [];
}

/** Coarse, non-identifying device class from the User-Agent. */
function pk_ua_class(): string {
    $ua = strtolower($_SERVER['HTTP_USER_AGENT'] ?? '');
    if ($ua === '') return 'other';
    if (preg_match('/ipad|tablet|playbook|silk|(android(?!.*mobile))/', $ua)) return 'tablet';
    if (preg_match('/mobi|iphone|ipod|phone|android/', $ua))                 return 'mobile';
    return 'desktop';
}

/** Resolve a reported station code -> stations.id (or null, so we never drop an event). */
function pk_station_id(PDO $db, string $code): ?int {
    if ($code === '') return null;
    $st = $db->prepare('SELECT id FROM stations WHERE code = ? LIMIT 1');
    $st->execute([$code]);
    $id = $st->fetchColumn();
    return $id === false ? null : (int)$id;
}

function pk_json(int $status, array $body): void {
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($body);
    exit;
}

function pk_require_post(): void {
    if (($_SERVER['REQUEST_METHOD'] ?? 'GET') !== 'POST') {
        pk_json(405, ['error' => 'POST only']);
    }
}
