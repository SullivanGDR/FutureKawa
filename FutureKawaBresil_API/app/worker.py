import asyncio
from datetime import datetime, timedelta
from sqlalchemy.future import select
from app.database import AsyncSessionLocal
from app.models.lot import Lot
from app.models.alerte import Alerte
from app.models.module_iot import ModuleIot
from app.models.releve_mesure import ReleveMesure
from app.models.entrepot import Entrepot
from app.config import get_settings
from app.services.mail import (
    send_connection_alert_email,
    send_lot_expiry_alert_email
)

async def check_expired_lots():
    while True:
        try:
            async with AsyncSessionLocal() as session:
                from app.models.configuration_pays import ConfigurationPays
                cfg_result = await session.execute(select(ConfigurationPays).filter(ConfigurationPays.nom_pays == get_settings().NOM_PAYS))
                config = cfg_result.scalars().first()
                nom_pays = config.nom_pays if config else get_settings().NOM_PAYS

                result = await session.execute(select(Lot).filter(Lot.statut != 'périmé'))
                lots = result.scalars().all()
                
                now = datetime.now().date()
                expired_lots = []
                
                for lot in lots:
                    diff = (now - lot.date_stockage).days
                    if diff > 365:
                        lot.statut = 'périmé'
                        
                        alert_exist = await session.execute(
                            select(Alerte).filter(Alerte.id_lot == lot.id_lot, Alerte.type_alerte == "Péremption", Alerte.traitee == False)
                        )
                        if not alert_exist.scalars().first():
                            desc = f"Le lot {lot.id_lot} a dépassé 365 jours de stockage ({diff} jours)."
                            from app.schemas.alerte import AlerteCreate
                            from app.crud import alerte as crud_alerte
                            
                            nouvelle_alerte = AlerteCreate(
                                type_alerte="Péremption",
                                description=desc,
                                id_lot=lot.id_lot
                            )
                            await crud_alerte.create_alerte(session, nouvelle_alerte)
                            
                            ent_result = await session.execute(
                                select(Entrepot).filter(Entrepot.id_entrepot == lot.id_entrepot)
                            )
                            entrepot = ent_result.scalars().first()
                            nom_entrepot = entrepot.nom_entrepot if entrepot else "Entrepôt Inconnu"
                            
                            expired_lots.append({
                                "id_lot": lot.id_lot,
                                "nom_entrepot": nom_entrepot,
                                "date_stockage": lot.date_stockage.strftime("%d/%m/%Y"),
                                "age_jours": diff
                            })
                
                if expired_lots:
                    await send_lot_expiry_alert_email(session, nom_pays, expired_lots)
                
                await session.commit()
                print("[Cron] Vérification des lots périmés effectuée.")
        except Exception as e:
            print(f"[Cron Error Lots] {e}")
        
        await asyncio.sleep(60 * 60)

async def check_module_connections():
    while True:
        try:
            async with AsyncSessionLocal() as session:
                from app.models.configuration_pays import ConfigurationPays
                cfg_result = await session.execute(select(ConfigurationPays).filter(ConfigurationPays.nom_pays == get_settings().NOM_PAYS))
                config = cfg_result.scalars().first()
                nom_pays = config.nom_pays if config else get_settings().NOM_PAYS

                result = await session.execute(select(ModuleIot))
                modules = result.scalars().all()
                
                now = datetime.now()
                inactive_modules = []
                
                for module in modules:
                    rel_result = await session.execute(
                        select(ReleveMesure)
                        .filter(ReleveMesure.id_module == module.id_module)
                        .order_by(ReleveMesure.date_heure.desc())
                        .limit(1)
                    )
                    dernier_releve = rel_result.scalars().first()
                    
                    is_offline = False
                    time_since = None
                    
                    if dernier_releve:
                        time_since = now - dernier_releve.date_heure.replace(tzinfo=None)
                        if time_since > timedelta(minutes=30):
                            is_offline = True
                    else:
                        is_offline = True
                        
                    if is_offline and module.statut_connexion == 'actif':
                        module.statut_connexion = 'inactif'
                        
                        alert_result = await session.execute(
                            select(Alerte).filter(Alerte.id_module == module.id_module, Alerte.type_alerte == "Perte de connexion", Alerte.traitee == False)
                        )
                        if not alert_result.scalars().first():
                            desc = f"Perte de signal MQTT pour le module {module.id_module}"
                            if dernier_releve:
                                desc += f" (dernière mesure reçue il y a {int(time_since.total_seconds() / 60)} minutes)."
                            else:
                                desc += " (aucune mesure reçue depuis le déploiement)."
                                
                            from app.schemas.alerte import AlerteCreate
                            from app.crud import alerte as crud_alerte
                            nouvelle_alerte = AlerteCreate(
                                type_alerte="Perte de connexion",
                                description=desc,
                                id_module=module.id_module
                            )
                            await crud_alerte.create_alerte(session, nouvelle_alerte)
                            
                            ent_result = await session.execute(
                                select(Entrepot).filter(Entrepot.id_entrepot == module.id_entrepot)
                            )
                            entrepot = ent_result.scalars().first()
                            nom_entrepot = entrepot.nom_entrepot if entrepot else "Entrepôt Inconnu"
                            
                            duree_inactivite = f"{int(time_since.total_seconds() / 60)} minutes" if time_since else "Aucune mesure reçue"
                            derniere_activite = dernier_releve.date_heure.strftime("%d/%m/%Y %H:%M:%S") if dernier_releve else "Jamais"
                            
                            inactive_modules.append({
                                "id_module": module.id_module,
                                "nom_entrepot": nom_entrepot,
                                "derniere_activite": derniere_activite,
                                "duree_inactivite": duree_inactivite
                            })
                
                if inactive_modules:
                    await send_connection_alert_email(session, nom_pays, inactive_modules)
                
                await session.commit()
                print("[Cron] Vérification des connexions IoT effectuée.")
        except Exception as e:
            print(f"[Cron Error IoT] {e}")
            
        await asyncio.sleep(30)

async def run_all_jobs():
    await asyncio.gather(
        check_expired_lots(),
        check_module_connections()
    )

def start_cron_jobs():
    return asyncio.create_task(run_all_jobs())
