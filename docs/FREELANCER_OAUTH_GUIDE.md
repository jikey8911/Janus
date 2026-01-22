# Guía de Autenticación OAuth - Freelancer.com

## Problema Actual
El `FREELANCER_OAUTH_TOKEN` está configurado como `pending_auth_flow`, lo que impide:
- Obtener el User ID automáticamente
- Enviar propuestas
- Acceder a funcionalidades completas de la API

## Solución: Flujo OAuth Completo

### Opción 1: Script Automático (Recomendado)

#### Paso 1: Iniciar servidor de callback
```bash
# Terminal 1
python scripts/oauth_callback_server.py
```

Esto iniciará un servidor en `http://localhost:8080` para recibir el callback.

#### Paso 2: Ejecutar script de autenticación
```bash
# Terminal 2
python scripts/auth_freelancer_oauth.py
```

El script:
1. Abrirá tu navegador en Freelancer OAuth
2. Te pedirá autorizar la aplicación
3. Recibirá el código automáticamente
4. Intercambiará el código por access token
5. Obtendrá tu User ID
6. Guardará todo en `.env`

### Opción 2: Manual

#### 1. Configurar Redirect URI en Freelancer App
- Ve a: https://www.freelancer.com/users/settings/api
- Añade Redirect URI: `http://localhost:8080/callback`

#### 2. Obtener Authorization Code
Abre en tu navegador:
```
https://accounts.freelancer.com/oauth/authorize?response_type=code&client_id=08fc033b-ed8d-4596-bce6-0c8f81e7dd55&redirect_uri=http://localhost:8080/callback&scope=basic&advanced_scopes=1 2 3 4 5 6
```

#### 3. Copiar código de la URL
Después de autorizar, serás redirigido a:
```
http://localhost:8080/callback?code=XXXXXX
```
Copia el valor de `code`.

#### 4. Intercambiar código por token
```bash
curl -X POST https://accounts.freelancer.com/oauth/token \
  -d "grant_type=authorization_code" \
  -d "code=CODIGO_AQUI" \
  -d "client_id=08fc033b-ed8d-4596-bce6-0c8f81e7dd55" \
  -d "client_secret=152f9ade061fbaeeb389ea687a495627b724b908768e2da5b0bf86b5c47c73b957f55b4bb70d0c78cbdc3b031666fc2ad1a7fd9eb09367d5723b590d6d671ee3" \
  -d "redirect_uri=http://localhost:8080/callback"
```

#### 5. Obtener User ID
```bash
curl -H "Authorization: Bearer ACCESS_TOKEN_AQUI" \
  https://www.freelancer.com/api/users/0.1/self
```

#### 6. Actualizar .env
```env
FREELANCER_OAUTH_TOKEN=tu_access_token_aqui
FREELANCER_USER_ID=tu_user_id_aqui
```

## Verificación

Después de completar la autenticación:

```bash
python tests/verify_freelancer_complete.py
```

Deberías ver:
```
✅ User ID detectado: 12345678
✅ Encontrados 10 trabajos
```

## Troubleshooting

### Error: "Invalid redirect_uri"
- Verifica que `http://localhost:8080/callback` esté configurado en tu app de Freelancer
- URL exacta, sin trailing slash

### Error: "Invalid client credentials"
- Verifica CLIENT_ID y CLIENT_SECRET en .env
- Asegúrate de que no haya espacios extra

### Error: "Token expired"
- Los tokens OAuth expiran
- Ejecuta el flujo nuevamente para obtener un nuevo token

## Permisos (Scopes)

Los scopes solicitados son:
- `basic`: Información básica del usuario
- `advanced_scopes 1-6`: Permisos para:
  - 1: Leer proyectos
  - 2: Enviar propuestas
  - 3: Leer mensajes
  - 4: Enviar mensajes
  - 5: Gestionar proyectos
  - 6: Gestionar pagos

## Referencias

- [Freelancer OAuth Docs](https://developers.freelancer.com/docs/authentication)
- [API Reference](https://developers.freelancer.com/docs/projects/projects)
