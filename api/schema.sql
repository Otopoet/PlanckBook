-- PLANCK companion — data layer schema (MySQL / MariaDB, as shipped on Hostinger).
-- Run ONCE in phpMyAdmin (or `mysql < schema.sql`) after creating the database in hPanel.
-- Then run seed_stations.sql to populate the station catalogue.
--
-- Privacy: no IP address and no personal data are stored. A "visitor" is a random
-- UUID kept in the reader's browser localStorage — it distinguishes return visits
-- without identifying anyone. Safe to share publicly; GDPR-light by design.

SET NAMES utf8mb4;
SET time_zone = '+00:00';

-- ---------------------------------------------------------------------------
-- 1. Station catalogue — one row per addressable page (mirrors the manifest).
--    Seeded by tools/seed_stations.py -> seed_stations.sql so the `code` values
--    match exactly what build_site.py injects into each page.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS stations (
  id       SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  code     VARCHAR(8)   NOT NULL,                       -- e.g. '5.3' ('' for chapter overviews/extras)
  chapter  TINYINT UNSIGNED NULL,                       -- NULL for extras
  slug     VARCHAR(120) NOT NULL,                       -- 'chapter-05/hilbert_space.html'
  title    VARCHAR(160) NOT NULL,
  type     ENUM('lab','figure','index','extra') NOT NULL DEFAULT 'lab',
  PRIMARY KEY (id),
  UNIQUE KEY uq_slug (slug),
  KEY ix_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- 2. Events — the engagement log. One row per page open (and optional 'complete').
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS events (
  id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  station_id  SMALLINT UNSIGNED NULL,                   -- NULL if code didn't resolve (event still kept)
  event_type  ENUM('view','complete') NOT NULL DEFAULT 'view',
  visitor     CHAR(36) NOT NULL,                        -- random UUID from localStorage (not PII)
  via_qr      TINYINT(1) NOT NULL DEFAULT 0,            -- arrived via ?src=qr
  ua_class    ENUM('mobile','tablet','desktop','other') NOT NULL DEFAULT 'other',
  code_seen   VARCHAR(8) NULL,                          -- raw code the client reported (audit trail)
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY ix_station_time (station_id, created_at),
  KEY ix_time (created_at),
  KEY ix_visitor (visitor),
  CONSTRAINT fk_ev_station FOREIGN KEY (station_id) REFERENCES stations(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- 3. Access codes — one unique code per book / print run (optional gate).
--    Generate with tools/gen_access_codes.py. Enforced by gate.php + .htaccess.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS access_codes (
  id           INT UNSIGNED NOT NULL AUTO_INCREMENT,
  code         CHAR(12) NOT NULL,                       -- printed in the book, e.g. 'PLK-7QK4-X2'
  label        VARCHAR(80) NULL,                        -- batch label, e.g. 'print run 1'
  issued_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  activated_at TIMESTAMP NULL DEFAULT NULL,             -- first successful use
  last_seen_at TIMESTAMP NULL DEFAULT NULL,
  views        INT UNSIGNED NOT NULL DEFAULT 0,
  revoked      TINYINT(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  UNIQUE KEY uq_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- 4. Feedback — optional per-station rating / question.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS feedback (
  id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  station_id  SMALLINT UNSIGNED NULL,
  rating      TINYINT NULL,                             -- +1 helpful, -1 not, NULL if message-only
  message     VARCHAR(2000) NULL,
  visitor     CHAR(36) NULL,
  status      ENUM('new','read','archived') NOT NULL DEFAULT 'new',
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY ix_station (station_id),
  KEY ix_status (status),
  CONSTRAINT fk_fb_station FOREIGN KEY (station_id) REFERENCES stations(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- Convenience views for the dashboard / phpMyAdmin.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_station_views AS
  SELECT s.code, s.chapter, s.title, s.type,
         COUNT(e.id)                       AS views,
         COUNT(DISTINCT e.visitor)         AS unique_visitors,
         SUM(e.via_qr)                     AS qr_arrivals,
         MAX(e.created_at)                 AS last_seen
  FROM stations s
  LEFT JOIN events e ON e.station_id = s.id AND e.event_type = 'view'
  GROUP BY s.id
  ORDER BY views DESC;

CREATE OR REPLACE VIEW v_daily_views AS
  SELECT DATE(created_at) AS day, COUNT(*) AS views,
         COUNT(DISTINCT visitor) AS unique_visitors
  FROM events
  WHERE event_type = 'view'
  GROUP BY DATE(created_at)
  ORDER BY day DESC;
