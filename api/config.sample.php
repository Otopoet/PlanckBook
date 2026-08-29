<?php
/**
 * PLANCK data layer — configuration.
 *
 * SETUP: copy this file to `config.php` and fill in the values from hPanel
 * (Databases -> MySQL Databases). Keep config.php OUT of version control and,
 * ideally, OUTSIDE the public web root. If it must live in /planck/api/, the
 * shipped .htaccess already denies direct web access to config.php.
 *
 * Never commit real credentials.
 */
return [
    // --- MySQL (from Hostinger hPanel) ---
    'db_host' => 'localhost',          // Hostinger usually 'localhost'
    'db_name' => 'uXXXXXX_planck',     // the database you created
    'db_user' => 'uXXXXXX_planck',     // the MySQL user
    'db_pass' => 'CHANGE_ME',

    // --- Secrets ---
    // Random 32+ char string. Signs the access-code cookie. Generate once, e.g.:
    //   php -r "echo bin2hex(random_bytes(24));"
    'app_secret' => 'CHANGE_ME_TO_A_LONG_RANDOM_STRING',

    // Key required to read the stats dashboard (stats.php?key=...). Keep private.
    'stats_key'  => 'CHANGE_ME_TOO',

    // --- Feature toggles ---
    'enable_tracking'     => true,   // events / analytics
    'enable_feedback'     => true,   // feedback endpoint + widget
    'enable_access_codes' => true,   // gate.php + .htaccess enforcement

    // Cookie name + lifetime (days) for an activated access code.
    'gate_cookie' => 'pk_pass',
    'gate_days'   => 365,
];
