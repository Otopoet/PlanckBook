<?php
/**
 * Analytics ingest. Called by assets/planck-companion.js via navigator.sendBeacon()
 * when a station opens. Writes one `events` row and returns 204 (no body).
 * Designed to fail quietly — a tracking error must never affect the reader.
 */
declare(strict_types=1);
require __DIR__ . '/db.php';

$cfg = pk_config();
if (empty($cfg['enable_tracking'])) { http_response_code(204); exit; }
pk_require_post();

try {
    $in       = pk_json_input();
    $code     = substr(trim((string)($in['code'] ?? '')), 0, 8);
    $visitor  = (string)($in['visitor'] ?? '');
    $type     = ($in['type'] ?? 'view') === 'complete' ? 'complete' : 'view';
    $via_qr   = !empty($in['via_qr']) ? 1 : 0;

    // visitor must look like a UUID; otherwise drop silently.
    if (!preg_match('/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i', $visitor)) {
        http_response_code(204); exit;
    }

    $db = pk_db();

    // If an access code is active, refresh its last_seen/views (cheap engagement signal).
    if (!empty($cfg['enable_access_codes']) && !empty($_COOKIE[$cfg['gate_cookie']])) {
        $token = $_COOKIE[$cfg['gate_cookie']];
        if (strpos($token, '.') !== false) {
            [$ac] = explode('.', $token, 2);
            $upd = $db->prepare(
                'UPDATE access_codes SET last_seen_at = NOW(), views = views + 1
                 WHERE code = ? AND revoked = 0');
            $upd->execute([$ac]);
        }
    }

    $stmt = $db->prepare(
        'INSERT INTO events (station_id, event_type, visitor, via_qr, ua_class, code_seen)
         VALUES (?, ?, ?, ?, ?, ?)');
    $stmt->execute([
        pk_station_id($db, $code), $type, $visitor, $via_qr, pk_ua_class(),
        $code !== '' ? $code : null,
    ]);

    http_response_code(204);
} catch (Throwable $e) {
    // swallow — never surface an error to the page
    http_response_code(204);
}
