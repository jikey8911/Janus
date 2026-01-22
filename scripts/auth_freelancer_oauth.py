"""
Script de Autenticación OAuth para Freelancer.com

Este script guía al usuario a través del flujo OAuth para obtener:
1. Access Token
2. User ID

Documentación: https://developers.freelancer.com/docs/authentication
"""
import os
import requests
from dotenv import load_dotenv, set_key
import webbrowser
from urllib.parse import urlencode

load_dotenv()

# Credenciales de la aplicación
CLIENT_ID = os.getenv("FREELANCER_CLIENT_ID")
CLIENT_SECRET = os.getenv("FREELANCER_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8080/callback"  # Debe estar configurado en Freelancer App

# URLs de OAuth
AUTH_URL = "https://accounts.freelancer.com/oauth/authorize"
TOKEN_URL = "https://accounts.freelancer.com/oauth/token"
API_BASE = "https://www.freelancer.com/api"

def step1_get_authorization_code():
    """
    Paso 1: Obtener código de autorización
    """
    print("=" * 70)
    print("PASO 1: Obtener Código de Autorización")
    print("=" * 70)
    
    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ ERROR: FREELANCER_CLIENT_ID o CLIENT_SECRET no configurados en .env")
        return None
    
    # Construir URL de autorización
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "basic",  # Permisos básicos
        "advanced_scopes": "1 2 3 4 5 6"  # Permisos extendidos
    }
    
    auth_url = f"{AUTH_URL}?{urlencode(params)}"
    
    print(f"\n1. Se abrirá tu navegador en la página de autorización de Freelancer")
    print(f"2. Inicia sesión y autoriza la aplicación")
    print(f"3. Serás redirigido a: {REDIRECT_URI}")
    print(f"4. Copia el 'code' de la URL de redirección")
    print(f"\nURL de autorización:\n{auth_url}\n")
    
    # Abrir navegador
    try:
        webbrowser.open(auth_url)
        print("✅ Navegador abierto")
    except:
        print("⚠️ No se pudo abrir el navegador automáticamente")
        print(f"Abre manualmente: {auth_url}")
    
    # Solicitar código
    print("\n" + "-" * 70)
    code = input("Ingresa el código de autorización (code): ").strip()
    
    if not code:
        print("❌ No se ingresó código")
        return None
    
    return code

def step2_exchange_code_for_token(code):
    """
    Paso 2: Intercambiar código por access token
    """
    print("\n" + "=" * 70)
    print("PASO 2: Obtener Access Token")
    print("=" * 70)
    
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI
    }
    
    try:
        print("\nSolicitando access token...")
        response = requests.post(TOKEN_URL, data=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            refresh_token = data.get("refresh_token")
            
            print("✅ Access Token obtenido exitosamente")
            print(f"   Token: {access_token[:30]}...")
            
            if refresh_token:
                print(f"   Refresh Token: {refresh_token[:30]}...")
            
            return access_token, refresh_token
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def step3_get_user_id(access_token):
    """
    Paso 3: Obtener User ID usando el access token
    """
    print("\n" + "=" * 70)
    print("PASO 3: Obtener User ID")
    print("=" * 70)
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        print("\nConsultando información del usuario...")
        response = requests.get(
            f"{API_BASE}/users/0.1/self",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            user_id = data.get("result", {}).get("id")
            username = data.get("result", {}).get("username")
            
            print("✅ User ID obtenido exitosamente")
            print(f"   User ID: {user_id}")
            print(f"   Username: {username}")
            
            return user_id
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def step4_save_to_env(access_token, user_id):
    """
    Paso 4: Guardar credenciales en .env
    """
    print("\n" + "=" * 70)
    print("PASO 4: Guardar Credenciales")
    print("=" * 70)
    
    env_path = ".env"
    
    try:
        # Actualizar .env
        set_key(env_path, "FREELANCER_OAUTH_TOKEN", access_token)
        set_key(env_path, "FREELANCER_USER_ID", str(user_id))
        
        print(f"\n✅ Credenciales guardadas en {env_path}")
        print(f"   FREELANCER_OAUTH_TOKEN: {access_token[:30]}...")
        print(f"   FREELANCER_USER_ID: {user_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error guardando credenciales: {e}")
        return False

def main():
    print("\n🔐 AUTENTICACIÓN OAUTH - FREELANCER.COM\n")
    
    # Paso 1: Obtener código
    code = step1_get_authorization_code()
    if not code:
        return
    
    # Paso 2: Obtener token
    access_token, refresh_token = step2_exchange_code_for_token(code)
    if not access_token:
        return
    
    # Paso 3: Obtener User ID
    user_id = step3_get_user_id(access_token)
    if not user_id:
        return
    
    # Paso 4: Guardar en .env
    if step4_save_to_env(access_token, user_id):
        print("\n" + "=" * 70)
        print("✅ AUTENTICACIÓN COMPLETADA")
        print("=" * 70)
        print("\nPuedes usar FreelancerAdapter ahora con autenticación completa.")
        print("Ejecuta: python tests/verify_freelancer_complete.py")
    else:
        print("\n❌ Autenticación incompleta")

if __name__ == "__main__":
    main()
