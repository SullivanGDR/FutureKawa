import asyncio
from sqlalchemy import text
from app.database import engine, AsyncSessionLocal
from app.models import Base
from app.models.configuration_pays import ConfigurationPays
from app.models.entrepot import Entrepot
from app.models.lot import Lot
from app.models.module_iot import ModuleIot
from app.models.releve_mesure import ReleveMesure
from app.models.alerte import Alerte
from app.models.utilisateur import Utilisateur
from app.utils.security import hash_password
from datetime import datetime, timedelta

async def reset_db():
    print("[Database] Debut de la reinitialisation de la base de donnees...")
    
    # 1. Recréation des tables
    async with engine.begin() as conn:
        # Désactiver les contraintes de clés étrangères temporairement pour drop propre
        try:
            await conn.execute(text("DROP TABLE IF EXISTS releve_mesure CASCADE;"))
            await conn.execute(text("DROP TABLE IF EXISTS alerte CASCADE;"))
            await conn.execute(text("DROP TABLE IF EXISTS lot CASCADE;"))
            await conn.execute(text("DROP TABLE IF EXISTS module_iot CASCADE;"))
            await conn.execute(text("DROP TABLE IF EXISTS entrepot CASCADE;"))
            await conn.execute(text("DROP TABLE IF EXISTS configuration_pays CASCADE;"))
            await conn.execute(text("DROP TABLE IF EXISTS utilisateurs CASCADE;"))
            print("[Database] Anciennes tables supprimees.")
        except Exception as e:
            print(f"[Database Warning] Erreur lors de la suppression des tables : {e}")

        await conn.run_sync(Base.metadata.create_all)
        print("[Database] Nouvelles tables creees.")

    # 2. Seeding des données de test
    async with AsyncSessionLocal() as session:
        # A. Seuils / Configurations pays
        bresil_cfg = ConfigurationPays(
            nom_pays="Brésil",
            email_responsable="futurekawa.bresil@gmail.com",
            temp_ideale=29.0,
            hum_ideale=55.0,
            tolerance_temp=3.0,
            tolerance_hum=2.0
        )
        colombie_cfg = ConfigurationPays(
            nom_pays="Colombie",
            email_responsable="exploitation.colombie@futurekawa.com",
            temp_ideale=26.0,
            hum_ideale=80.0,
            tolerance_temp=3.0,
            tolerance_hum=2.0 
        )
        equateur_cfg = ConfigurationPays(
            nom_pays="Équateur",
            email_responsable="exploitation.equateur@futurekawa.com",
            temp_ideale=31.0,
            hum_ideale=60.0,
            tolerance_temp=3.0,
            tolerance_hum=2.0
        )
        session.add_all([bresil_cfg, colombie_cfg, equateur_cfg])

        # B. Sites / Entrepôts
        e1 = Entrepot(id_entrepot=1, nom_entrepot="Hub Central Santos")
        e2 = Entrepot(id_entrepot=2, nom_entrepot="Rio Terminal A")
        e3 = Entrepot(id_entrepot=3, nom_entrepot="Medellin Depot")
        e4 = Entrepot(id_entrepot=4, nom_entrepot="Quito Silos")
        session.add_all([e1, e2, e3, e4])

        # C. Modules IoT
        # active / inactive states
        m1 = ModuleIot(id_module="br-santos-01", statut_connexion="actif", id_entrepot=1)
        m2 = ModuleIot(id_module="br-rio-02", statut_connexion="actif", id_entrepot=2)
        m3 = ModuleIot(id_module="col-medellin-01", statut_connexion="actif", id_entrepot=3)
        m4 = ModuleIot(id_module="eq-quito-01", statut_connexion="inactif", id_entrepot=4)
        m5 = ModuleIot(id_module="br-santos-offline", statut_connexion="actif", id_entrepot=1) # Pas de message depuis 45 min
        session.add_all([m1, m2, m3, m4, m5])

        # D. Télémetrie historique
        releves = []
        now = datetime.now()

        # br-santos-01 : Relevés nominaux (dans les seuils)
        for i in range(12):
            releves.append(ReleveMesure(
                temperature=28.5 + (i % 2) * 0.4,
                humidite=54.6 + (i % 2) * 0.5,
                id_module="br-santos-01",
                date_heure=now - timedelta(minutes=5 * i)
            ))
            
        # br-rio-02 : Hors seuils (33.8°C, max Brésil est 32°C) -> En alerte
        for i in range(8):
            releves.append(ReleveMesure(
                temperature=33.8,
                humidite=56.2,
                id_module="br-rio-02",
                date_heure=now - timedelta(minutes=5 * i)
            ))
            
        # col-medellin-01 : Relevés nominaux
        for i in range(6):
            releves.append(ReleveMesure(
                temperature=25.8,
                humidite=79.5,
                id_module="col-medellin-01",
                date_heure=now - timedelta(minutes=5 * i)
            ))

        # br-santos-offline : Un seul message il y a 45 minutes (donc > 30 minutes offline)
        releves.append(ReleveMesure(
            temperature=29.2,
            humidite=54.8,
            id_module="br-santos-offline",
            date_heure=now - timedelta(minutes=45)
        ))
        
        session.add_all(releves)

        # E. Lots (FIFO validation)
        # Lot 1 : Brésil Santos - Périmé (> 365 jours)
        l1_stockage = datetime.now().date() - timedelta(days=400)
        l1 = Lot(id_lot="LOT-BR-001", date_stockage=l1_stockage, date_peremption=l1_stockage + timedelta(days=365), statut="périmé", id_entrepot=1)
        # Lot 2 : Brésil Santos - Conforme
        l2_stockage = datetime.now().date() - timedelta(days=120)
        l2 = Lot(id_lot="LOT-BR-002", date_stockage=l2_stockage, date_peremption=l2_stockage + timedelta(days=365), statut="conforme", id_entrepot=1)
        # Lot 3 : Brésil Rio - En alerte (à cause du module br-rio-02 qui surchauffe)
        l3_stockage = datetime.now().date() - timedelta(days=60)
        l3 = Lot(id_lot="LOT-BR-003", date_stockage=l3_stockage, date_peremption=l3_stockage + timedelta(days=365), statut="en alerte", id_entrepot=2)
        # Lot 4 : Colombie - Conforme
        l4_stockage = datetime.now().date() - timedelta(days=15)
        l4 = Lot(id_lot="LOT-COL-001", date_stockage=l4_stockage, date_peremption=l4_stockage + timedelta(days=365), statut="conforme", id_entrepot=3)
        session.add_all([l1, l2, l3, l4])

        # F. Alertes
        # Alerte péremption active
        a1 = Alerte(
            type_alerte="Péremption", 
            description="Le lot a dépassé 365 jours de stockage (400 jours).", 
            id_lot="LOT-BR-001", 
            id_module=None, 
            traitee=False
        )
        # Alerte température active
        a2 = Alerte(
            type_alerte="Conditionnement", 
            description="Température anormale: 33.8°C (Tolérance Brésil: 26.0-32.0°C)", 
            id_lot=None, 
            id_module="br-rio-02", 
            traitee=False
        )
        # Alerte connexion perdue active
        a3 = Alerte(
            type_alerte="Perte de connexion",
            description="Perte de signal MQTT pour le module br-santos-offline (dernière mesure reçue il y a 45 minutes).",
            id_lot=None,
            id_module="br-santos-offline",
            traitee=False
        )
        session.add_all([a1, a2, a3])

        # G. Utilisateurs
        admin_user = Utilisateur(
            email="admin@futurekawa.com",
            nom="System Admin",
            password_hash=hash_password("admin"),
            role="admin",
            nom_pays=None
        )
        bresil_user = Utilisateur(
            email="bresil@futurekawa.com",
            nom="Chef de Dépôt Brésil",
            password_hash=hash_password("kawa"),
            role="employe",
            nom_pays="Brésil"
        )
        colombie_user = Utilisateur(
            email="colombie@futurekawa.com",
            nom="Chef de Dépôt Colombie",
            password_hash=hash_password("kawa"),
            role="employe",
            nom_pays="Colombie"
        )
        equateur_user = Utilisateur(
            email="equateur@futurekawa.com",
            nom="Chef de Dépôt Équateur",
            password_hash=hash_password("kawa"),
            role="employe",
            nom_pays="Équateur"
        )
        session.add_all([admin_user, bresil_user, colombie_user, equateur_user])

        await session.commit()
        await session.execute(text("SELECT setval('entrepot_id_entrepot_seq', COALESCE((SELECT MAX(id_entrepot) FROM entrepot), 1))"))
        await session.commit()
        print("[Database] Donnees de test injectees avec succes !")

if __name__ == "__main__":
    asyncio.run(reset_db())
