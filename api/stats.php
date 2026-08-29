<?php
/**
 * Author dashboard. Key-protected (config['stats_key']). Server-renders tables —
 * no client JS, nothing public. Visit:
 *   https://ivanroche.com/planck/api/stats.php?key=YOUR_STATS_KEY
 * Add &format=json for the raw numbers.
 */
declare(strict_types=1);
require __DIR__ . '/db.php';

$cfg = pk_config();
if (!hash_equals((string)$cfg['stats_key'], (string)($_GET['key'] ?? ''))) {
    http_response_code(403); exit('Forbidden');
}

$db = pk_db();
$q = fn(string $sql) => $db->query($sql)->fetchAll();

$totals   = $db->query(
    "SELECT COUNT(*) views, COUNT(DISTINCT visitor) visitors, SUM(via_qr) qr
     FROM events WHERE event_type='view'")->fetch();
$stations = $q("SELECT * FROM v_station_views");
$daily    = $q("SELECT * FROM v_daily_views LIMIT 30");
$codes    = !empty($cfg['enable_access_codes'])
    ? $q("SELECT label, COUNT(*) issued, SUM(activated_at IS NOT NULL) activated, SUM(views) views
          FROM access_codes GROUP BY label ORDER BY issued DESC")
    : [];
$feedback = !empty($cfg['enable_feedback'])
    ? $db->query(
        "SELECT f.created_at, s.code, s.title, f.rating, f.message, f.status
         FROM feedback f LEFT JOIN stations s ON s.id=f.station_id
         ORDER BY f.created_at DESC LIMIT 100")->fetchAll()
    : [];

if (($_GET['format'] ?? '') === 'json') {
    pk_json(200, compact('totals', 'stations', 'daily', 'codes', 'feedback'));
}

function h($v): string { return htmlspecialchars((string)$v, ENT_QUOTES); }
?><!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>PLANCK — engagement</title>
<link rel="stylesheet" href="../assets/planck.css">
<style>
  .dash { max-width: 920px; margin: 5vh auto; padding: 0 22px 80px; }
  .dash h1 { font-size: 24px; margin: 0 0 4px; }
  .dash h2 { font-size: 15px; color: var(--cyan); font-family: var(--mono, monospace);
             text-transform: uppercase; letter-spacing: .1em; margin: 34px 0 12px; }
  .kpis { display: flex; gap: 14px; flex-wrap: wrap; }
  .kpi { background: var(--panel); border: 1px solid var(--line); border-radius: 12px;
         padding: 16px 20px; min-width: 140px; }
  .kpi .n { font-size: 28px; font-weight: 700; }
  .kpi .l { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .08em; }
  table { width: 100%; border-collapse: collapse; font-size: 14px; }
  th, td { text-align: left; padding: 7px 10px; border-bottom: 1px solid var(--line); }
  th { color: var(--muted); font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: .06em; }
  td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
  .muted { color: var(--faint); }
</style>
</head><body>
<div class="dash">
  <h1>PLANCK · engagement</h1>
  <div class="muted">Privacy-light: no IPs, no personal data. A “visitor” is a random browser id.</div>

  <div class="kpis" style="margin-top:18px">
    <div class="kpi"><div class="n"><?= (int)$totals['views'] ?></div><div class="l">station views</div></div>
    <div class="kpi"><div class="n"><?= (int)$totals['visitors'] ?></div><div class="l">unique visitors</div></div>
    <div class="kpi"><div class="n"><?= (int)$totals['qr'] ?></div><div class="l">via QR</div></div>
  </div>

  <h2>Stations by views</h2>
  <table><thead><tr><th>Code</th><th>Ch</th><th>Title</th><th>Type</th>
    <th class="num">Views</th><th class="num">Unique</th><th class="num">QR</th><th>Last seen</th></tr></thead><tbody>
  <?php foreach ($stations as $s): ?>
    <tr><td><?= h($s['code']) ?></td><td><?= h($s['chapter']) ?></td><td><?= h($s['title']) ?></td>
        <td class="muted"><?= h($s['type']) ?></td>
        <td class="num"><?= (int)$s['views'] ?></td><td class="num"><?= (int)$s['unique_visitors'] ?></td>
        <td class="num"><?= (int)$s['qr_arrivals'] ?></td><td class="muted"><?= h($s['last_seen']) ?></td></tr>
  <?php endforeach; ?>
  </tbody></table>

  <?php if ($codes): ?>
  <h2>Access codes</h2>
  <table><thead><tr><th>Batch</th><th class="num">Issued</th><th class="num">Activated</th><th class="num">Views</th></tr></thead><tbody>
  <?php foreach ($codes as $c): ?>
    <tr><td><?= h($c['label'] ?: '—') ?></td><td class="num"><?= (int)$c['issued'] ?></td>
        <td class="num"><?= (int)$c['activated'] ?></td><td class="num"><?= (int)$c['views'] ?></td></tr>
  <?php endforeach; ?>
  </tbody></table>
  <?php endif; ?>

  <?php if ($feedback): ?>
  <h2>Recent feedback</h2>
  <table><thead><tr><th>When</th><th>Station</th><th>Rating</th><th>Message</th><th>Status</th></tr></thead><tbody>
  <?php foreach ($feedback as $f): ?>
    <tr><td class="muted"><?= h($f['created_at']) ?></td>
        <td><?= h($f['code']) ?> <span class="muted"><?= h($f['title']) ?></span></td>
        <td><?= $f['rating'] === null ? '—' : ((int)$f['rating'] > 0 ? '👍' : '👎') ?></td>
        <td><?= h($f['message']) ?></td><td class="muted"><?= h($f['status']) ?></td></tr>
  <?php endforeach; ?>
  </tbody></table>
  <?php endif; ?>
</div>
</body></html>
