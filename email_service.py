# email_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import secrets
import string

load_dotenv()

# Configuration SMTP
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)
APP_URL = os.getenv("APP_URL", "http://localhost:3000")

def generate_temp_password(length=12):
    """Générer un mot de passe temporaire aléatoire"""
    characters = string.ascii_letters + string.digits + "!@#$%"
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

def send_email(to_email: str, subject: str, body: str):
    """Envoyer un email via SMTP"""
    if not SMTP_USER or not SMTP_PASSWORD:
        print("⚠️ Configuration SMTP manquante - Email non envoyé")
        print(f"📧 Email simulé pour {to_email}:")
        print(f"Subject: {subject}")
        print(f"Body:\n{body}")
        return False
    
    try:
        # Créer le message
        msg = MIMEMultipart()
        msg['From'] = SMTP_FROM
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Ajouter le corps du message
        msg.attach(MIMEText(body, 'plain'))
        
        # Connexion au serveur SMTP
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        
        # Envoi
        text = msg.as_string()
        server.sendmail(SMTP_FROM, to_email, text)
        server.quit()
        
        print(f"✅ Email envoyé à {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur envoi email: {e}")
        return False

def send_welcome_email(username: str, email: str, temp_password: str, role: str, company_name: str = None):
    """Envoyer un email de bienvenue avec mot de passe temporaire"""
    
    role_fr = {
        "superadmin": "Super Administrateur",
        "admin": "Administrateur",
        "user": "Utilisateur"
    }.get(role, role)
    
    subject = "Bienvenue - Votre compte a été créé"
    
    body = f"""Bonjour {username},

Votre compte a été créé sur la plateforme de Gestion d'Échafaudages.

📋 Informations de connexion :
{'─' * 50}
Nom d'utilisateur : {username}
Mot de passe temporaire : {temp_password}
Rôle : {role_fr}
{f'Entreprise : {company_name}' if company_name else ''}

🔗 Lien de connexion : {APP_URL}/login

⚠️ IMPORTANT :
À votre première connexion, vous devrez obligatoirement changer votre mot de passe.

Pour des raisons de sécurité :
- Gardez ce mot de passe temporaire confidentiel
- Changez-le dès votre première connexion
- Choisissez un mot de passe fort (min. 8 caractères, majuscules, minuscules, chiffres)

Si vous n'êtes pas à l'origine de cette demande, veuillez contacter l'administrateur.

Cordialement,
L'équipe de Gestion d'Échafaudages
"""
    
    return send_email(email, subject, body)

def send_password_reset_email(username: str, email: str, temp_password: str):
    """Envoyer un email de réinitialisation de mot de passe"""
    
    subject = "Réinitialisation de votre mot de passe"
    
    body = f"""Bonjour {username},

Votre mot de passe a été réinitialisé.

📋 Nouveau mot de passe temporaire :
{'─' * 50}
Mot de passe : {temp_password}

🔗 Lien de connexion : {APP_URL}/login

⚠️ IMPORTANT :
À votre prochaine connexion, vous devrez obligatoirement changer ce mot de passe.

Si vous n'êtes pas à l'origine de cette demande, contactez immédiatement l'administrateur.

Cordialement,
L'équipe de Gestion d'Échafaudages
"""
    
    return send_email(email, subject, body)
