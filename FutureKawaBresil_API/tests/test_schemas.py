import pytest
from decimal import Decimal
from datetime import date, datetime
from pydantic import ValidationError

from app.schemas.lot import LotCreate, LotResponse
from app.schemas.alerte import AlerteCreate, AlerteResponse
from app.schemas.module_iot import ModuleIotCreate
from app.schemas.releve_mesure import ReleveMesureCreate
from app.schemas.configuration_pays import ConfigurationPaysCreate
from app.schemas.auth import LoginRequest, UserResponse


class TestLotSchema:
    def test_lot_create_valid(self):
        lot = LotCreate(id_lot="LOT-TEST-001", date_stockage=date(2024, 1, 1), date_peremption=date(2024, 12, 31), id_entrepot=1)
        assert lot.id_lot == "LOT-TEST-001"
        assert lot.id_entrepot == 1

    def test_lot_statut_default_conforme(self):
        lot = LotCreate(id_lot="L001", date_stockage=date.today(), date_peremption=date.today(), id_entrepot=1)
        assert lot.statut == "conforme"

    def test_lot_statut_custom(self):
        lot = LotCreate(id_lot="L002", date_stockage=date.today(), date_peremption=date.today(), statut="périmé", id_entrepot=2)
        assert lot.statut == "périmé"

    def test_lot_missing_id_raises(self):
        with pytest.raises(ValidationError):
            LotCreate(date_stockage=date.today(), date_peremption=date.today(), id_entrepot=1)

    def test_lot_missing_entrepot_raises(self):
        with pytest.raises(ValidationError):
            LotCreate(id_lot="L001", date_stockage=date.today(), date_peremption=date.today())


class TestAlerteSchema:
    def test_alerte_create_defaults(self):
        alerte = AlerteCreate(type_alerte="Péremption")
        assert alerte.traitee is False
        assert alerte.id_lot is None
        assert alerte.id_module is None
        assert alerte.description is None

    def test_alerte_with_lot(self):
        alerte = AlerteCreate(type_alerte="Conditionnement", id_lot="LOT-BR-001")
        assert alerte.id_lot == "LOT-BR-001"

    def test_alerte_with_module(self):
        alerte = AlerteCreate(type_alerte="Perte de connexion", id_module="br-rio-02")
        assert alerte.id_module == "br-rio-02"

    def test_alerte_missing_type_raises(self):
        with pytest.raises(ValidationError):
            AlerteCreate()

    def test_alerte_traitee_true(self):
        alerte = AlerteCreate(type_alerte="Test", traitee=True)
        assert alerte.traitee is True


class TestModuleIotSchema:
    def test_module_create_valid(self):
        module = ModuleIotCreate(id_module="br-test-01", statut_connexion="actif", id_entrepot=1)
        assert module.id_module == "br-test-01"
        assert module.statut_connexion == "actif"

    def test_module_inactif(self):
        module = ModuleIotCreate(id_module="eq-quito-01", statut_connexion="inactif", id_entrepot=4)
        assert module.statut_connexion == "inactif"

    def test_module_missing_id_raises(self):
        with pytest.raises(ValidationError):
            ModuleIotCreate(statut_connexion="actif", id_entrepot=1)

    def test_module_missing_entrepot_raises(self):
        with pytest.raises(ValidationError):
            ModuleIotCreate(id_module="m1", statut_connexion="actif")


class TestReleveMesureSchema:
    def test_releve_valid(self):
        releve = ReleveMesureCreate(
            temperature=Decimal("28.5"),
            humidite=Decimal("55.0"),
            id_module="br-santos-01"
        )
        assert releve.temperature == Decimal("28.5")
        assert releve.humidite == Decimal("55.0")

    def test_releve_temperature_from_float(self):
        releve = ReleveMesureCreate(temperature=28.5, humidite=55.0, id_module="m1")
        assert releve.temperature == Decimal("28.5")

    def test_releve_missing_module_raises(self):
        with pytest.raises(ValidationError):
            ReleveMesureCreate(temperature=28.5, humidite=55.0)


class TestConfigurationPaysSchema:
    def test_config_pays_valid(self):
        cfg = ConfigurationPaysCreate(
            nom_pays="Brésil",
            email_responsable="test@futurekawa.com",
            temp_ideale=Decimal("29.0"),
            hum_ideale=Decimal("55.0"),
            tolerance_temp=Decimal("3.0"),
            tolerance_hum=Decimal("2.0")
        )
        assert cfg.nom_pays == "Brésil"
        assert cfg.temp_ideale == Decimal("29.0")

    def test_config_pays_missing_email_raises(self):
        with pytest.raises(ValidationError):
            ConfigurationPaysCreate(
                nom_pays="Brésil",
                temp_ideale=Decimal("29.0"),
                hum_ideale=Decimal("55.0"),
                tolerance_temp=Decimal("3.0"),
                tolerance_hum=Decimal("2.0")
            )


class TestAuthSchema:
    def test_login_request_valid(self):
        req = LoginRequest(email="admin@futurekawa.com", password="admin")
        assert req.email == "admin@futurekawa.com"
        assert req.password == "admin"

    def test_login_request_invalid_email_raises(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="not-an-email", password="admin")

    def test_login_request_missing_password_raises(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="admin@futurekawa.com")

    def test_user_response_optional_pays(self):
        user = UserResponse(id_utilisateur=1, email="admin@futurekawa.com", nom="Admin", role="admin")
        assert user.nom_pays is None

    def test_user_response_with_pays(self):
        user = UserResponse(
            id_utilisateur=2, email="bresil@futurekawa.com",
            nom="Chef Brésil", role="employe", nom_pays="Brésil"
        )
        assert user.nom_pays == "Brésil"
