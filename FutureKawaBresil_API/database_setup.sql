-- PostgreSQL Database Setup Script for FutureKawa
-- Drops old tables, recreates the schema, and inserts initial seed data.

-- =========================================================================
-- 1. CLEANUP (Suppression des anciennes tables si existantes)
-- =========================================================================
DROP TABLE IF EXISTS alerte CASCADE;
DROP TABLE IF EXISTS releve_mesure CASCADE;
DROP TABLE IF EXISTS lot CASCADE;
DROP TABLE IF EXISTS module_iot CASCADE;
DROP TABLE IF EXISTS entrepot CASCADE;
DROP TABLE IF EXISTS utilisateurs CASCADE;
DROP TABLE IF EXISTS configuration_pays CASCADE;

-- =========================================================================
-- 2. CREATE SCHEMA (Création des tables et contraintes de clés)
-- =========================================================================

-- Configuration Pays & Seuils
CREATE TABLE configuration_pays (
    nom_pays VARCHAR(100) PRIMARY KEY,
    email_responsable VARCHAR(255) NOT NULL,
    temp_ideale NUMERIC(5, 2) NOT NULL,
    hum_ideale NUMERIC(5, 2) NOT NULL,
    tolerance_temp NUMERIC(5, 2) NOT NULL,
    tolerance_hum NUMERIC(5, 2) NOT NULL
);

-- Utilisateurs (Gestion d'accès centralisée et par pays)
CREATE TABLE utilisateurs (
    id_utilisateur SERIAL PRIMARY KEY,
    email VARCHAR(150) UNIQUE NOT NULL,
    nom VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'employe',
    nom_pays VARCHAR(100) REFERENCES configuration_pays(nom_pays) ON DELETE SET NULL
);

-- Entrepôts de stockage
CREATE TABLE entrepot (
    id_entrepot SERIAL PRIMARY KEY,
    nom_entrepot VARCHAR(150) NOT NULL
);

-- Lots de café vert
CREATE TABLE lot (
    id_lot VARCHAR(50) PRIMARY KEY,
    date_stockage DATE NOT NULL,
    date_peremption DATE NOT NULL,
    statut VARCHAR(50) NOT NULL,
    id_entrepot INT REFERENCES entrepot(id_entrepot) ON DELETE CASCADE NOT NULL
);

-- Modules de capteurs IoT
CREATE TABLE module_iot (
    id_module VARCHAR(100) PRIMARY KEY,
    statut_connexion VARCHAR(50) NOT NULL,
    id_entrepot INT REFERENCES entrepot(id_entrepot) ON DELETE CASCADE NOT NULL
);

-- Relevés de mesures des capteurs
CREATE TABLE releve_mesure (
    id_releve SERIAL PRIMARY KEY,
    date_heure TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    temperature NUMERIC(5, 2) NOT NULL,
    humidite NUMERIC(5, 2) NOT NULL,
    id_module VARCHAR(100) REFERENCES module_iot(id_module) ON DELETE CASCADE NOT NULL
);

-- Signalement des alertes actives et clôturées
CREATE TABLE alerte (
    id_alerte SERIAL PRIMARY KEY,
    date_alerte TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    type_alerte VARCHAR(100) NOT NULL,
    description TEXT,
    id_lot VARCHAR(50) REFERENCES lot(id_lot) ON DELETE CASCADE,
    id_module VARCHAR(100) REFERENCES module_iot(id_module) ON DELETE CASCADE,
    traitee BOOLEAN DEFAULT FALSE NOT NULL
);

-- =========================================================================
-- 3. INSERT SEED DATA (Insertion des données initiales de test)
-- =========================================================================

-- A. Seuils environnementaux par pays
INSERT INTO configuration_pays (nom_pays, email_responsable, temp_ideale, hum_ideale, tolerance_temp, tolerance_hum) VALUES
('Brésil', 'futurekawa.bresil@gmail.com', 29.0, 55.0, 3.0, 2.0),
('Colombie', 'exploitation.colombie@futurekawa.com', 26.0, 80.0, 3.0, 2.0),
('Équateur', 'exploitation.equateur@futurekawa.com', 31.0, 60.0, 3.0, 2.0);

-- B. Utilisateurs (Mots de passe : admin/kawa avec le sel de sécurité appliqué)
INSERT INTO utilisateurs (email, nom, password_hash, role, nom_pays) VALUES
('admin@futurekawa.com', 'System Admin', 'cb631d6d745133aeb6d39be1f0e4c5e68a244c2114e15b3842c6f6def6b9b9f7', 'admin', NULL),
('bresil@futurekawa.com', 'Chef de Dépôt Brésil', 'e4e0b78e5cf35155634959b9d889c882280e3d6e6f09f30f9d7e79e0d83c4013', 'employe', 'Brésil'),
('colombie@futurekawa.com', 'Chef de Dépôt Colombie', 'e4e0b78e5cf35155634959b9d889c882280e3d6e6f09f30f9d7e79e0d83c4013', 'employe', 'Colombie'),
('equateur@futurekawa.com', 'Chef de Dépôt Équateur', 'e4e0b78e5cf35155634959b9d889c882280e3d6e6f09f30f9d7e79e0d83c4013', 'employe', 'Équateur');

-- C. Entrepôts
INSERT INTO entrepot (id_entrepot, nom_entrepot) VALUES
(1, 'Hub Central Santos'),
(2, 'Rio Terminal A'),
(3, 'Medellin Depot'),
(4, 'Quito Silos');

-- Recalibrer la séquence de clés primaires d'entrepôt après insertion forcée d'identifiants
SELECT setval('entrepot_id_entrepot_seq', (SELECT MAX(id_entrepot) FROM entrepot));

-- D. Modules IoT
INSERT INTO module_iot (id_module, statut_connexion, id_entrepot) VALUES
('br-santos-01', 'actif', 1),
('br-rio-02', 'actif', 2),
('col-medellin-01', 'actif', 3),
('eq-quito-01', 'inactif', 4),
('br-santos-offline', 'actif', 1);

-- E. Historique de Télémetrie (température/humidité)
-- br-santos-01 : Relevés nominaux dans les seuils autorisés
INSERT INTO releve_mesure (date_heure, temperature, humidite, id_module) VALUES
(NOW() - INTERVAL '55 minutes', 28.50, 54.60, 'br-santos-01'),
(NOW() - INTERVAL '50 minutes', 28.90, 55.10, 'br-santos-01'),
(NOW() - INTERVAL '45 minutes', 28.50, 54.60, 'br-santos-01'),
(NOW() - INTERVAL '40 minutes', 28.90, 55.10, 'br-santos-01'),
(NOW() - INTERVAL '35 minutes', 28.50, 54.60, 'br-santos-01'),
(NOW() - INTERVAL '30 minutes', 28.90, 55.10, 'br-santos-01'),
(NOW() - INTERVAL '25 minutes', 28.50, 54.60, 'br-santos-01'),
(NOW() - INTERVAL '20 minutes', 28.90, 55.10, 'br-santos-01'),
(NOW() - INTERVAL '15 minutes', 28.50, 54.60, 'br-santos-01'),
(NOW() - INTERVAL '10 minutes', 28.90, 55.10, 'br-santos-01'),
(NOW() - INTERVAL '5 minutes', 28.50, 54.60, 'br-santos-01'),
(NOW(), 28.90, 55.10, 'br-santos-01');

-- br-rio-02 : Hors seuils (surchauffe de 33.8°C pour max 32.0°C) -> En alerte
INSERT INTO releve_mesure (date_heure, temperature, humidite, id_module) VALUES
(NOW() - INTERVAL '35 minutes', 33.80, 56.20, 'br-rio-02'),
(NOW() - INTERVAL '30 minutes', 33.80, 56.20, 'br-rio-02'),
(NOW() - INTERVAL '25 minutes', 33.80, 56.20, 'br-rio-02'),
(NOW() - INTERVAL '20 minutes', 33.80, 56.20, 'br-rio-02'),
(NOW() - INTERVAL '15 minutes', 33.80, 56.20, 'br-rio-02'),
(NOW() - INTERVAL '10 minutes', 33.80, 56.20, 'br-rio-02'),
(NOW() - INTERVAL '5 minutes', 33.80, 56.20, 'br-rio-02'),
(NOW(), 33.80, 56.20, 'br-rio-02');

-- col-medellin-01 : Relevés normaux pour Colombie (seuil idéal 26.0°C / 80%)
INSERT INTO releve_mesure (date_heure, temperature, humidite, id_module) VALUES
(NOW() - INTERVAL '25 minutes', 25.80, 79.50, 'col-medellin-01'),
(NOW() - INTERVAL '20 minutes', 25.80, 79.50, 'col-medellin-01'),
(NOW() - INTERVAL '15 minutes', 25.80, 79.50, 'col-medellin-01'),
(NOW() - INTERVAL '10 minutes', 25.80, 79.50, 'col-medellin-01'),
(NOW() - INTERVAL '5 minutes', 25.80, 79.50, 'col-medellin-01'),
(NOW(), 25.80, 79.50, 'col-medellin-01');

-- br-santos-offline : Pas de mesure depuis 45 minutes (> 30 minutes inactivité)
INSERT INTO releve_mesure (date_heure, temperature, humidite, id_module) VALUES
(NOW() - INTERVAL '45 minutes', 29.20, 54.80, 'br-santos-offline');

-- F. Lots (Exemples de lots de café conformes, en alerte et périmés)
INSERT INTO lot (id_lot, date_stockage, date_peremption, statut, id_entrepot) VALUES
('LOT-BR-001', CURRENT_DATE - INTERVAL '400 days', CURRENT_DATE - INTERVAL '400 days' + INTERVAL '365 days', 'périmé', 1),
('LOT-BR-002', CURRENT_DATE - INTERVAL '120 days', CURRENT_DATE - INTERVAL '120 days' + INTERVAL '365 days', 'conforme', 1),
('LOT-BR-003', CURRENT_DATE - INTERVAL '60 days', CURRENT_DATE - INTERVAL '60 days' + INTERVAL '365 days', 'en alerte', 2),
('LOT-COL-001', CURRENT_DATE - INTERVAL '15 days', CURRENT_DATE - INTERVAL '15 days' + INTERVAL '365 days', 'conforme', 3);

-- G. Alertes actives sur le parc
INSERT INTO alerte (type_alerte, description, id_lot, id_module, traitee) VALUES
('Péremption', 'Le lot a dépassé 365 jours de stockage (400 jours).', 'LOT-BR-001', NULL, FALSE),
('Conditionnement', 'Température anormale: 33.8°C (Tolérance Brésil: 26.0-32.0°C)', NULL, 'br-rio-02', FALSE),
('Perte de connexion', 'Perte de signal MQTT pour le module br-santos-offline (dernière mesure reçue il y a 45 minutes).', NULL, 'br-santos-offline', FALSE);
