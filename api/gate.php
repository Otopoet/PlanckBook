<?php
/**
 * Access-code gate. Replaces (or augments) the single shared password with a
 * unique code printed in each book / per print run.
 *
 * Flow: .htaccess redirects any reader without a valid `pk_pass` cookie here.
 * They enter their code; on success we set a signed cookie and send them on.
 * The cookie value is `<code>.<hmac>` so it can't be forged without app_secret.
 *
 * Note on strength: .htaccess checks only that the cookie is PRESENT and well-formed;
 * the HMAC makes it unforgeable, but a shared private companion like this is
 * "good-enough" privacy, not hard security. For hard guarantees use Cloudflare Access.
 */
declare(strict_types=1);
require __DIR__ . '/db.php';

$cfg = pk_config();
if (empty($cfg['enable_access_codes'])) { header('Location: ../index.html'); exit; }

/** Only allow redirects back into the /planck/ space (no open redirect). */
function pk_safe_next(string $next): string {
    $next = trim($next);
    if ($next === '' || $next[0] !== '/' || strpos($next, '//') === 0) return '../index.html';
    return $next;
}

$secret = (string)$cfg['app_secret'];
$cookie = (string)$cfg['gate_cookie'];
$next   = pk_safe_next((string)($_REQUEST['next'] ?? ''));
$error  = '';

if (($_SERVER['REQUEST_METHOD'] ?? 'GET') === 'POST') {
    $code = strtoupper(trim((string)($_POST['code'] ?? '')));
    try {
        $db = pk_db();
        $st = $db->prepare('SELECT code FROM access_codes WHERE code = ? AND revoked = 0 LIMIT 1');
        $st->execute([$code]);
        $row = $st->fetch();
        if ($row) {
            $db->prepare(
                'UPDATE access_codes
                 SET activated_at = COALESCE(activated_at, NOW()), last_seen_at = NOW()
                 WHERE code = ?')->execute([$code]);

            $token = $code . '.' . hash_hmac('sha256', $code, $secret);
            setcookie($cookie, $token, [
                'expires'  => time() + 86400 * (int)$cfg['gate_days'],
                'path'     => '/planck/',
                'secure'   => !empty($_SERVER['HTTPS']),
                'httponly' => true,
                'samesite' => 'Lax',
            ]);
            header('Location: ' . $next);
            exit;
        }
        $error = 'That code was not recognised. Check the code printed in your copy of PLANCK.';
    } catch (Throwable $e) {
        $error = 'Something went wrong validating the code. Please try again.';
    }
}
?><!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PLANCK — enter your access code</title>
<link rel="stylesheet" href="../assets/planck.css">
<style>
  .gate { max-width: 440px; margin: 14vh auto; padding: 0 22px; }
  .gate .eyebrow { font-family: var(--mono, monospace); color: var(--cyan); letter-spacing: .12em;
                   text-transform: uppercase; font-size: 12px; }
  .gate h1 { font-size: 26px; margin: 10px 0 6px; }
  .gate p.lead { color: var(--muted); margin: 0 0 22px; }
  .gate form { display: flex; gap: 10px; }
  .gate input { flex: 1; background: var(--panel); border: 1px solid var(--line-2);
                color: var(--text); border-radius: 10px; padding: 12px 14px; font-size: 16px;
                font-family: var(--mono, monospace); letter-spacing: .08em; }
  .gate input:focus { outline: none; border-color: var(--cyan); }
  .gate button { background: var(--cyan); color: #04201d; border: 0; border-radius: 10px;
                 padding: 12px 18px; font-weight: 600; font-size: 15px; cursor: pointer; }
  .gate .err { color: var(--red); margin-top: 14px; font-size: 14px; }
  .gate .foot { color: var(--faint); font-size: 12px; margin-top: 26px; }
</style>
</head>
<body>
<div class="gate">
  <div class="eyebrow">PLANCK · companion field guide</div>
  <h1>Enter your access code</h1>
  <p class="lead">The companion is private. Use the access code printed in your copy of the book.</p>
  <form method="post" action="gate.php?next=<?= htmlspecialchars(urlencode($next), ENT_QUOTES) ?>">
    <input name="code" autocomplete="off" autocapitalize="characters" spellcheck="false"
           placeholder="PLK-XXXX-XXX" aria-label="Access code" autofocus>
    <button type="submit">Enter</button>
  </form>
  <?php if ($error): ?><div class="err"><?= htmlspecialchars($error, ENT_QUOTES) ?></div><?php endif; ?>
  <div class="foot">One code unlocks the whole field guide on this device.</div>
</div>
</body>
</html>
