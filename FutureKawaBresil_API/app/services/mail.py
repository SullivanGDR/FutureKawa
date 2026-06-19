from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from sqlalchemy.future import select
from app.models.configuration_pays import ConfigurationPays
from app.config import get_settings

# Configuration de fastapi-mail
settings = get_settings()

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME="FutureKawa Supervision",
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

fastmail = FastMail(conf)

async def get_responsable_email(session, nom_pays: str = None) -> str:
    """Récupère l'email du responsable dans la table configuration locale pour un pays spécifique."""
    if nom_pays:
        result = await session.execute(select(ConfigurationPays).filter(ConfigurationPays.nom_pays == nom_pays))
    else:
        result = await session.execute(select(ConfigurationPays).filter(ConfigurationPays.nom_pays == settings.NOM_PAYS))
    config = result.scalars().first()
    if config and config.email_responsable:
        return config.email_responsable
    return "default-manager@futurekawa.com" 



async def send_climate_alert_email(
    session,
    module_id: str,
    nom_entrepot: str,
    nom_pays: str,
    temperature: float,
    humidite: float,
    config,
    reasons: list
):
    """Envoie un e-mail HTML premium et détaillé pour les dérives climatiques."""
    recipient = await get_responsable_email(session, nom_pays)
    from datetime import datetime
    current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    temp_status_badge = ""
    if temperature < config.seuil_temp_min or temperature > config.seuil_temp_max:
        temp_status_badge = '<span style="display: inline-block; padding: 2px 8px; font-size: 11px; font-weight: 600; border-radius: 9999px; background-color: #ffe4e6; color: #be123c;">HORS SEUIL</span>'
    else:
        temp_status_badge = '<span style="display: inline-block; padding: 2px 8px; font-size: 11px; font-weight: 600; border-radius: 9999px; background-color: #dcfce7; color: #15803d;">CONFORME</span>'

    hum_status_badge = ""
    if humidite < config.seuil_hum_min or humidite > config.seuil_hum_max:
        hum_status_badge = '<span style="display: inline-block; padding: 2px 8px; font-size: 11px; font-weight: 600; border-radius: 9999px; background-color: #ffe4e6; color: #be123c;">HORS SEUIL</span>'
    else:
        hum_status_badge = '<span style="display: inline-block; padding: 2px 8px; font-size: 11px; font-weight: 600; border-radius: 9999px; background-color: #dcfce7; color: #15803d;">CONFORME</span>'

    reasons_html = "".join([f"<li style='margin-bottom: 6px; color: #be123c; font-weight: 500;'>{r}</li>" for r in reasons])

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body style="font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px; -webkit-font-smoothing: antialiased;">
        <div style="max-width: 620px; margin: 20px auto; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);">
            <!-- En-tête de marque -->
            <div style="background-color: #0f172a; padding: 20px 30px; border-bottom: 1px solid #1e293b;">
                <span style="color: #ffffff; font-size: 18px; font-weight: 800; letter-spacing: 0.5px;">Future<span style="color: #38bdf8;">Kawa</span></span>
                <span style="float: right; font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; margin-top: 5px;">Supervision Region</span>
            </div>

            <!-- Bandeau d'état rouge critique -->
            <div style="background-color: #be123c; color: #ffffff; padding: 14px 30px; font-size: 13px; font-weight: bold; letter-spacing: 0.5px; text-transform: uppercase; display: flex; align-items: center;">
                <span style="font-size: 16px; margin-right: 8px;">🌡️</span> ALERTE CRITIQUE : DÉRIVE DES SEUILS CLIMATIQUES ({nom_pays})
            </div>

            <div style="padding: 30px;">
                <p style="font-size: 15px; color: #0f172a; margin-top: 0; margin-bottom: 12px; font-weight: 600;">Bonjour,</p>
                <p style="font-size: 14px; color: #475569; margin-bottom: 25px; line-height: 1.5; margin-top: 0;">
                    Une dérive climatique a été mesurée dans l'un de vos entrepôts de stockage. Les conditions requises pour la préservation des grains ne sont plus garanties :
                </p>

                <!-- Carte d'incident principale -->
                <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 20px; margin-bottom: 25px;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 6px 0; font-size: 13px; font-weight: bold; color: #64748b; width: 35%;">Site d'exploitation</td>
                            <td style="padding: 6px 0; font-size: 13px; font-weight: 600; color: #0f172a;">{nom_entrepot} ({nom_pays})</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; font-size: 13px; font-weight: bold; color: #64748b;">Module IoT / Sonde</td>
                            <td style="padding: 6px 0; font-size: 13px; font-family: monospace; font-weight: bold; color: #0f172a; background-color: #e2e8f0; padding: 2px 6px; border-radius: 4px; display: inline-block;">{module_id}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; font-size: 13px; font-weight: bold; color: #64748b;">Date de détection</td>
                            <td style="padding: 6px 0; font-size: 13px; font-family: monospace; color: #0f172a;">{current_time}</td>
                        </tr>
                    </table>
                </div>

                <!-- Tableau comparatif des mesures -->
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 25px;">
                    <thead>
                        <tr style="background-color: #f1f5f9; border-bottom: 2px solid #e2e8f0;">
                            <th style="padding: 10px; text-align: left; font-size: 12px; font-weight: bold; color: #475569;">Grandeur</th>
                            <th style="padding: 10px; text-align: left; font-size: 12px; font-weight: bold; color: #475569;">Mesure Reçue</th>
                            <th style="padding: 10px; text-align: left; font-size: 12px; font-weight: bold; color: #475569;">Cible Idéale (Seuils admis)</th>
                            <th style="padding: 10px; text-align: left; font-size: 12px; font-weight: bold; color: #475569;">État</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 12px 10px; font-size: 13px; font-weight: bold; color: #0f172a;">Température</td>
                            <td style="padding: 12px 10px; font-size: 13px; font-weight: bold; color: #be123c;">{temperature}°C</td>
                            <td style="padding: 12px 10px; font-size: 13px; color: #475569;">{config.temp_ideale}°C (±{config.tolerance_temp}°C)<br><span style="font-size: 11px; color: #94a3b8;">[{config.seuil_temp_min}°C - {config.seuil_temp_max}°C]</span></td>
                            <td style="padding: 12px 10px;">{temp_status_badge}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 12px 10px; font-size: 13px; font-weight: bold; color: #0f172a;">Humidité</td>
                            <td style="padding: 12px 10px; font-size: 13px; font-weight: bold; color: #be123c;">{humidite}%</td>
                            <td style="padding: 12px 10px; font-size: 13px; color: #475569;">{config.hum_ideale}% (±{config.tolerance_hum}%)<br><span style="font-size: 11px; color: #94a3b8;">[{config.seuil_hum_min}% - {config.seuil_hum_max}%]</span></td>
                            <td style="padding: 12px 10px;">{hum_status_badge}</td>
                        </tr>
                    </tbody>
                </table>

                <!-- Raisons / Symptômes -->
                <div style="margin-bottom: 25px;">
                    <p style="font-size: 13px; font-weight: bold; color: #be123c; text-transform: uppercase; margin-bottom: 8px;">Détails des anomalies :</p>
                    <ul style="margin: 0; padding-left: 20px; font-size: 13px; line-height: 1.5; color: #334155;">
                        {reasons_html}
                    </ul>
                </div>

                <!-- Recommandation d'action -->
                <div style="background-color: #fff1f2; border-left: 4px solid #be123c; border-radius: 0 6px 6px 0; padding: 15px 20px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 13px; line-height: 1.5; color: #9f1239; font-weight: 500;">
                        <strong>Action immédiate :</strong> Vérifiez le système de climatisation et de ventilation de l'entrepôt concerné. Les lots en transit dans cette cellule ont été automatiquement marqués comme "En alerte" dans la console.
                    </p>
                </div>

                <!-- Bouton d'action centralisé -->
                <div style="text-align: center; margin-top: 30px;">
                    <a href="http://localhost:5173" style="background-color: #0f172a; color: #ffffff; text-decoration: none; padding: 12px 24px; font-weight: bold; border-radius: 6px; display: inline-block; font-size: 13px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">Accéder à la Console de Supervision</a>
                </div>
            </div>

            <!-- Pied de page -->
            <div style="background-color: #f8fafc; padding: 20px 30px; border-top: 1px solid #e2e8f0; font-size: 11px; color: #64748b; line-height: 1.5; text-align: center;">
                Cet e-mail est généré automatiquement par la console régionale FutureKawa.<br>
                Merci de ne pas y répondre directement.
            </div>
        </div>
    </body>
    </html>
    """

    message = MessageSchema(
        subject=f"[FutureKawa ALERTE CLIMATIQUE] Hors Seuils pour {module_id} ({nom_entrepot})",
        recipients=[recipient],
        body=html_content,
        subtype=MessageType.html
    )

    try:
        await fastmail.send_message(message)
        print(f"[Mail Service] E-mail d'alerte climatique envoye a {recipient}")
    except Exception as e:
        print(f"[Mail Service Error] Impossible d'envoyer l'alerte climatique : {e}")



async def send_connection_alert_email(
    session,
    nom_pays: str,
    inactive_modules: list
):
    """Envoie un e-mail HTML premium récapitulant les pertes de connexion de capteurs."""
    recipient = await get_responsable_email(session, nom_pays)
    from datetime import datetime
    current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    rows_html = ""
    for mod in inactive_modules:
        derniere_com = mod["derniere_activite"]
        duree = mod["duree_inactivite"]
        rows_html += f"""
        <tr style="border-bottom: 1px solid #e2e8f0;">
            <td style="padding: 12px 10px; font-family: monospace; font-weight: bold; color: #0f172a; font-size: 13px;">{mod['id_module']}</td>
            <td style="padding: 12px 10px; font-size: 13px; color: #334155;">{mod['nom_entrepot']}</td>
            <td style="padding: 12px 10px; font-size: 13px; color: #64748b; font-family: monospace;">{derniere_com}</td>
            <td style="padding: 12px 10px; font-size: 13px; color: #be123c; font-weight: 500;">{duree}</td>
            <td style="padding: 12px 10px; text-align: center;">
                <span style="display: inline-block; padding: 2px 8px; font-size: 11px; font-weight: 600; border-radius: 9999px; background-color: #ffedd5; color: #ea580c;">HORS LIGNE</span>
            </td>
        </tr>
        """

    count = len(inactive_modules)
    subject_text = f"Pann{"es" if count > 1 else "e"} Système - Perte de Signal IoT ({count} module{"s" if count > 1 else ""})"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body style="font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px; -webkit-font-smoothing: antialiased;">
        <div style="max-width: 620px; margin: 20px auto; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);">
            <!-- En-tête -->
            <div style="background-color: #0f172a; padding: 20px 30px; border-bottom: 1px solid #1e293b;">
                <span style="color: #ffffff; font-size: 18px; font-weight: 800; letter-spacing: 0.5px;">Future<span style="color: #38bdf8;">Kawa</span></span>
                <span style="float: right; font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; margin-top: 5px;">Supervision Region</span>
            </div>

            <!-- Bandeau orange avertissement -->
            <div style="background-color: #ea580c; color: #ffffff; padding: 14px 30px; font-size: 13px; font-weight: bold; letter-spacing: 0.5px; text-transform: uppercase;">
                🔌 ALERTE CRITIQUE : PERTE DE CONNEXION CAPTEURS ({nom_pays})
            </div>

            <div style="padding: 30px;">
                <p style="font-size: 15px; color: #0f172a; margin-top: 0; margin-bottom: 12px; font-weight: 600;">Bonjour,</p>
                <p style="font-size: 14px; color: #475569; margin-bottom: 25px; line-height: 1.5; margin-top: 0;">
                    La passerelle MQTT a détecté un arrêt des communications pour <strong>{count} capteur{"s" if count > 1 else ""}</strong>. 
                    Leur statut a été automatiquement positionné sur <strong>inactif</strong>. 
                    Voici le rapport d'incident :
                </p>

                <!-- Tableau des capteurs hors-ligne -->
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 25px;">
                    <thead>
                        <tr style="background-color: #f1f5f9; border-bottom: 2px solid #e2e8f0;">
                            <th style="padding: 10px; text-align: left; font-size: 12px; font-weight: bold; color: #475569;">Capteur</th>
                            <th style="padding: 10px; text-align: left; font-size: 12px; font-weight: bold; color: #475569;">Entrepôt</th>
                            <th style="padding: 10px; text-align: left; font-size: 12px; font-weight: bold; color: #475569;">Dernier Signal</th>
                            <th style="padding: 10px; text-align: left; font-size: 12px; font-weight: bold; color: #475569;">Inactivité</th>
                            <th style="padding: 10px; text-align: center; font-size: 12px; font-weight: bold; color: #475569;">État</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>

                <div style="background-color: #fff7ed; border-left: 4px solid #ea580c; border-radius: 0 6px 6px 0; padding: 15px 20px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 13px; line-height: 1.5; color: #c2410c; font-weight: 500;">
                        <strong>Diagnostic requis :</strong> Vérifiez l'alimentation électrique des modules concernés ainsi que la couverture du réseau local.
                    </p>
                </div>

                <!-- Bouton d'action -->
                <div style="text-align: center; margin-top: 30px;">
                    <a href="http://localhost:5173" style="background-color: #0f172a; color: #ffffff; text-decoration: none; padding: 12px 24px; font-weight: bold; border-radius: 6px; display: inline-block; font-size: 13px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">Accéder à la Console de Supervision</a>
                </div>
            </div>

            <!-- Pied de page -->
            <div style="background-color: #f8fafc; padding: 20px 30px; border-top: 1px solid #e2e8f0; font-size: 11px; color: #64748b; line-height: 1.5; text-align: center;">
                Cet e-mail est généré automatiquement par la console régionale FutureKawa.<br>
                Merci de ne pas y répondre directement.
            </div>
        </div>
    </body>
    </html>
    """

    message = MessageSchema(
        subject=f"[FutureKawa SYSTEM] {subject_text}",
        recipients=[recipient],
        body=html_content,
        subtype=MessageType.html
    )

    try:
        await fastmail.send_message(message)
        print(f"[Mail Service] E-mail groupé de perte de connexion envoyé à {recipient}")
    except Exception as e:
        print(f"[Mail Service Error] Impossible d'envoyer l'e-mail groupé de perte de connexion : {e}")



async def send_lot_expiry_alert_email(
    session,
    nom_pays: str,
    expired_lots: list
):
    """Envoie un e-mail HTML premium récapitulant les lots qui dépassent la durée limite de stockage."""
    recipient = await get_responsable_email(session, nom_pays)
    from datetime import datetime
    current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    rows_html = ""
    for lot in expired_lots:
        rows_html += f"""
        <tr style="border-bottom: 1px solid #e2e8f0;">
            <td style="padding: 12px 10px; font-family: monospace; font-weight: bold; color: #0f172a; font-size: 13px;">{lot['id_lot']}</td>
            <td style="padding: 12px 10px; font-size: 13px; color: #334155;">{lot['nom_entrepot']}</td>
            <td style="padding: 12px 10px; font-size: 13px; color: #64748b; font-family: monospace;">{lot['date_stockage']}</td>
            <td style="padding: 12px 10px; font-size: 13px; color: #b45309; font-weight: bold;">{lot['age_jours']} jours</td>
            <td style="padding: 12px 10px; text-align: center;">
                <span style="display: inline-block; padding: 2px 8px; font-size: 11px; font-weight: 600; border-radius: 9999px; background-color: #fef3c7; color: #b45309;">PÉRIMÉ</span>
            </td>
        </tr>
        """

    count = len(expired_lots)
    subject_text = f"Rotation FIFO - Alerte Péremption ({count} lot{"s" if count > 1 else ""})"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body style="font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px; -webkit-font-smoothing: antialiased;">
        <div style="max-width: 620px; margin: 20px auto; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);">
            <!-- En-tête -->
            <div style="background-color: #0f172a; padding: 20px 30px; border-bottom: 1px solid #1e293b;">
                <span style="color: #ffffff; font-size: 18px; font-weight: 800; letter-spacing: 0.5px;">Future<span style="color: #38bdf8;">Kawa</span></span>
                <span style="float: right; font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; margin-top: 5px;">Supervision Region</span>
            </div>

            <!-- Bandeau jaune ambre -->
            <div style="background-color: #d97706; color: #ffffff; padding: 14px 30px; font-size: 13px; font-weight: bold; letter-spacing: 0.5px; text-transform: uppercase;">
                📅 ALERTE FIFO : ROTATION DES STOCKS ({nom_pays})
            </div>

            <div style="padding: 30px;">
                <p style="font-size: 15px; color: #0f172a; margin-top: 0; margin-bottom: 12px; font-weight: 600;">Bonjour,</p>
                <p style="font-size: 14px; color: #475569; margin-bottom: 25px; line-height: 1.5; margin-top: 0;">
                    Le suivi du stockage signale que <strong>{count} lot{"s" if count > 1 else ""}</strong> de café ont dépassé la durée maximale autorisée de stockage (365 jours). 
                    Leur statut a été basculé sur <strong>périmé</strong>. 
                    Veuillez procéder à leur traitement prioritaire :
                </p>

                <!-- Tableau des lots périmés -->
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 25px;">
                    <thead>
                        <tr style="background-color: #f1f5f9; border-bottom: 2px solid #e2e8f0;">
                            <th style="padding: 10px; text-align: left; font-size: 12px; font-weight: bold; color: #475569;">ID Lot</th>
                            <th style="padding: 10px; text-align: left; font-size: 12px; font-weight: bold; color: #475569;">Entrepôt</th>
                            <th style="padding: 10px; text-align: left; font-size: 12px; font-weight: bold; color: #475569;">Date d'entrée</th>
                            <th style="padding: 10px; text-align: left; font-size: 12px; font-weight: bold; color: #475569;">Durée de Stockage</th>
                            <th style="padding: 10px; text-align: center; font-size: 12px; font-weight: bold; color: #475569;">État</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>

                <div style="background-color: #fffbeb; border-left: 4px solid #d97706; border-radius: 0 6px 6px 0; padding: 15px 20px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 13px; line-height: 1.5; color: #b45309; font-weight: 500;">
                        <strong>Règle de rotation (FIFO) :</strong> Pour des raisons de qualité du grain de café, tout lot stocké depuis plus de 365 jours doit être traité ou déclassé.
                    </p>
                </div>

                <!-- Bouton d'action -->
                <div style="text-align: center; margin-top: 30px;">
                    <a href="http://localhost:5173" style="background-color: #0f172a; color: #ffffff; text-decoration: none; padding: 12px 24px; font-weight: bold; border-radius: 6px; display: inline-block; font-size: 13px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">Accéder à la Console de Supervision</a>
                </div>
            </div>

            <!-- Pied de page -->
            <div style="background-color: #f8fafc; padding: 20px 30px; border-top: 1px solid #e2e8f0; font-size: 11px; color: #64748b; line-height: 1.5; text-align: center;">
                Cet e-mail est généré automatiquement par la console régionale FutureKawa.<br>
                Merci de ne pas y répondre directement.
            </div>
        </div>
    </body>
    </html>
    """

    message = MessageSchema(
        subject=f"[FutureKawa FIFO] {subject_text}",
        recipients=[recipient],
        body=html_content,
        subtype=MessageType.html
    )

    try:
        await fastmail.send_message(message)
        print(f"[Mail Service] E-mail groupé de rotation FIFO envoyé à {recipient}")
    except Exception as e:
        print(f"[Mail Service Error] Impossible d'envoyer l'e-mail groupé de rotation FIFO : {e}")



async def send_alert_email(session, subject: str, body_content: str):
    """Fallback générique pour l'envoi d'e-mails simples."""
    recipient = await get_responsable_email(session)
    from datetime import datetime
    
    alert_color = "#18181b"
    alert_icon = "⚠️"
    
    subj_lower = subject.lower()
    if "panne" in subj_lower or "connexion" in subj_lower or "module" in subj_lower:
        alert_color = "#ea580c"
        alert_icon = "🔌"
    elif "peremption" in subj_lower or "fifo" in subj_lower or "lot" in subj_lower:
        alert_color = "#d97706"
        alert_icon = "📅"
    elif "climatique" in subj_lower or "seuil" in subj_lower or "hors" in subj_lower:
        alert_color = "#be123c"
        alert_icon = "🌡️"

    details_html = ""
    if " | " in body_content:
        details_list = body_content.split(" | ")
        details_html = "".join([f"<li style='margin-bottom: 5px;'>{item}</li>" for item in details_list])
        details_html = f"<ul style='margin: 0; padding-left: 20px;'>{details_html}</ul>"
    else:
        details_html = f"<p style='margin: 0; line-height: 1.5;'>{body_content}</p>"

    current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body style="font-family: 'Inter', sans-serif; background-color: #f8fafc; margin: 0; padding: 20px;">
        <div style="max-width: 600px; margin: 20px auto; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
            <div style="background-color: #0f172a; padding: 20px; border-bottom: 1px solid #1e293b;">
                <span style="color: #ffffff; font-weight: bold; font-size: 16px;">FutureKawa Supervision</span>
            </div>
            <div style="background-color: {alert_color}; color: #ffffff; padding: 12px 20px; font-size: 13px; font-weight: bold; text-transform: uppercase;">
                {alert_icon} {subject}
            </div>
            <div style="padding: 25px;">
                <p style="margin-top: 0; font-size: 14px; font-weight: bold; color: #0f172a;">Bonjour,</p>
                <p style="font-size: 13.5px; color: #475569; line-height: 1.5;">Une anomalie a été signalée par le système de supervision :</p>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 13px;">
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 8px; font-weight: bold; color: #64748b; width: 30%;">Date</td>
                        <td style="padding: 8px; color: #0f172a; font-family: monospace;">{current_time}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 8px; font-weight: bold; color: #64748b;">Incident</td>
                        <td style="padding: 8px; color: #0f172a; font-weight: bold;">{subject}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; font-weight: bold; color: #64748b;">Détails</td>
                        <td style="padding: 8px; color: #334155;">{details_html}</td>
                    </tr>
                </table>
            </div>
            <div style="background-color: #f8fafc; padding: 15px; text-align: center; border-top: 1px solid #e2e8f0; font-size: 11px; color: #64748b;">
                Ce courriel est un message automatique de supervision FutureKawa.
            </div>
        </div>
    </body>
    </html>
    """

    message = MessageSchema(
        subject=f"[FutureKawa ALERTE] {subject}",
        recipients=[recipient],
        body=html_content,
        subtype=MessageType.html
    )

    try:
        await fastmail.send_message(message)
        print(f"[Mail Service] E-mail envoye avec succes a {recipient}")
    except Exception as e:
        print(f"[Mail Service Error] Impossible d'envoyer l'email : {e}")
