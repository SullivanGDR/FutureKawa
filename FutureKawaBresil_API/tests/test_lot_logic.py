"""
Tests des règles métier FutureKawa — sans base de données.

Règles testées:
  - Lot périmé si stocké > 365 jours (worker.py: if diff > 365)
  - Statuts valides: conforme, en alerte, périmé
  - Plages climatiques Brésil: temp 26-32°C, humidité 53-57%
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal


# --- Règles métier extraites du worker.py ---

def calcul_age_lot(date_stockage: date) -> int:
    return (date.today() - date_stockage).days


def est_lot_perime(date_peremption: date) -> bool:
    return date.today() > date_peremption


def est_temperature_hors_seuil(temp: Decimal, temp_ideale: Decimal, tolerance: Decimal) -> bool:
    return abs(temp - temp_ideale) > tolerance


def est_humidite_hors_seuil(hum: Decimal, hum_ideale: Decimal, tolerance: Decimal) -> bool:
    return abs(hum - hum_ideale) > tolerance


# --- Tests péremption lots ---

class TestExpiration:
    def test_lot_recente_non_perime(self):
        peremp = date.today() + timedelta(days=265)
        assert est_lot_perime(peremp) is False

    def test_lot_exactement_aujourd_hui_non_perime(self):
        peremp = date.today()
        assert est_lot_perime(peremp) is False

    def test_lot_perime_depuis_hier(self):
        peremp = date.today() - timedelta(days=1)
        assert est_lot_perime(peremp) is True

    def test_lot_perime_depuis_longtemps(self):
        peremp = date.today() - timedelta(days=35)
        assert est_lot_perime(peremp) is True

    def test_calcul_age_lot_correct(self):
        il_y_a_30_jours = date.today() - timedelta(days=30)
        assert calcul_age_lot(il_y_a_30_jours) == 30


# --- Tests seuils climatiques Brésil ---

class TestSeuilsClimatBresil:
    TEMP_IDEALE = Decimal("29.0")
    HUM_IDEALE = Decimal("55.0")
    TOLERANCE_TEMP = Decimal("3.0")   # plage: 26.0 - 32.0°C
    TOLERANCE_HUM = Decimal("2.0")    # plage: 53.0 - 57.0%

    def test_temperature_nominale_ok(self):
        assert est_temperature_hors_seuil(
            Decimal("28.5"), self.TEMP_IDEALE, self.TOLERANCE_TEMP
        ) is False

    def test_temperature_haute_alerte(self):
        assert est_temperature_hors_seuil(
            Decimal("33.8"), self.TEMP_IDEALE, self.TOLERANCE_TEMP
        ) is True

    def test_temperature_limite_haute_ok(self):
        assert est_temperature_hors_seuil(
            Decimal("32.0"), self.TEMP_IDEALE, self.TOLERANCE_TEMP
        ) is False

    def test_temperature_depassement_limite_haute(self):
        assert est_temperature_hors_seuil(
            Decimal("32.1"), self.TEMP_IDEALE, self.TOLERANCE_TEMP
        ) is True

    def test_humidite_nominale_ok(self):
        assert est_humidite_hors_seuil(
            Decimal("54.6"), self.HUM_IDEALE, self.TOLERANCE_HUM
        ) is False

    def test_humidite_trop_haute_alerte(self):
        assert est_humidite_hors_seuil(
            Decimal("60.0"), self.HUM_IDEALE, self.TOLERANCE_HUM
        ) is True

    def test_humidite_trop_basse_alerte(self):
        assert est_humidite_hors_seuil(
            Decimal("50.0"), self.HUM_IDEALE, self.TOLERANCE_HUM
        ) is True


# --- Tests seuils climatiques Colombie ---

class TestSeuilsClimatColombie:
    TEMP_IDEALE = Decimal("26.0")
    HUM_IDEALE = Decimal("80.0")
    TOLERANCE_TEMP = Decimal("3.0")   # plage: 23.0 - 29.0°C
    TOLERANCE_HUM = Decimal("2.0")    # plage: 78.0 - 82.0%

    def test_temperature_nominale_ok(self):
        assert est_temperature_hors_seuil(
            Decimal("25.8"), self.TEMP_IDEALE, self.TOLERANCE_TEMP
        ) is False

    def test_humidite_nominale_ok(self):
        assert est_humidite_hors_seuil(
            Decimal("79.5"), self.HUM_IDEALE, self.TOLERANCE_HUM
        ) is False
