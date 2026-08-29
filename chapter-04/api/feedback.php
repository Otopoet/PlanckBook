<?php
/**
 * Feedback ingest. Called by the small feedback widget in planck-companion.js.
 * Accepts a rating (+1 / -1) and/or a short message for a station.
 */
declare(strict_types=1);
require __DIR__ . '/db.php';

$cfg = pk_config();
if (empty($cfg['enable_feedback'])) { pk_json(404, ['error' => 'disabled']); }
pk_require_post();

try {
    $in      = pk_json_input();
    $code    = substr(trim((string)($in['code'] ?? '')), 0, 8);
    $visitor = (string)($in['visitor'] ?? '');
    $message = trim((string)($in['message'] ?? ''));
    $message = $message === '' ? null : mb_substr($message, 0, 2000);

    $rating = null;
    if (array_key_exists('rating', $in) && $in['rating'] !== null && $in['rating'] !== '') {
        $rating = (int)$in['rating'] >= 0 ? 1 : -1;
    }

    if ($rating === null && $message === null) {
        pk_json(400, ['error' => 'empty']);
    }
    if ($visitor !== '' &&
        !preg_match('/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i', $visitor)) {
        $visitor = '';
    }

    $db = pk_db();
    $stmt = $db->prepare(
        'INSERT INTO feedback (station_id, rating, message, visitor)
         VALUES (?, ?, ?, ?)');
    $stmt->execute([
        pk_station_id($db, $code), $rating, $message, $visitor !== '' ? $visitor : null,
    ]);

    pk_json(200, ['ok' => true]);
} catch (Throwable $e) {
    pk_json(500, ['error' => 'server']);
}
