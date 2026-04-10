# Deploy - Paso a paso

## 1. Crear Bot de Telegram

1. Abrí Telegram y buscá **@BotFather**
2. Enviá `/newbot`
3. Elegí nombre: `Tracking Personal` (o lo que quieras)
4. Elegí username: `tu_tracking_bot` (tiene que terminar en `bot`)
5. BotFather te da el **token** — guardalo
6. Enviá `/setdescription` y poné una descripción
7. Para obtener tu **chat_id**: buscá **@userinfobot** en Telegram, mandá `/start`, te devuelve tu ID numérico

## 2. Crear cuenta en Groq

1. Andá a https://console.groq.com/
2. Registrate (gratis)
3. Andá a **API Keys** → Create API Key
4. Guardá la key

## 3. Crear DB en Turso

1. Instalá Turso CLI:
   ```bash
   curl -sSfL https://get.tur.so/install.sh | bash
   ```
2. Logueate:
   ```bash
   turso auth login
   ```
3. Creá la DB:
   ```bash
   turso db create tracking-bot
   ```
4. Obtené la URL:
   ```bash
   turso db show tracking-bot --url
   ```
   Te da algo como: `libsql://tracking-bot-xxx.turso.io`
5. Creá un token:
   ```bash
   turso db tokens create tracking-bot
   ```
6. Iniciá el schema:
   ```bash
   turso db shell tracking-bot
   ```
   Y pegá:
   ```sql
   CREATE TABLE IF NOT EXISTS events (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       timestamp TEXT NOT NULL,
       category TEXT NOT NULL,
       data TEXT NOT NULL,
       raw_input TEXT,
       source TEXT DEFAULT 'telegram'
   );
   CREATE INDEX IF NOT EXISTS idx_events_category ON events(category);
   CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
   CREATE TABLE IF NOT EXISTS sessions (
       token_hash TEXT PRIMARY KEY,
       created_at TEXT NOT NULL,
       expires_at TEXT NOT NULL
   );
   ```

## 4. Generar password hash

```bash
python3 -c "import bcrypt; print(bcrypt.hashpw(input('Password: ').encode(), bcrypt.gensalt()).decode())"
```

Ingresá tu password, copiá el hash que empieza con `$2b$12$...`

## 5. Subir a GitHub

```bash
cd tracking-bot
git init
echo "node_modules/\ndist/\n__pycache__/\n*.pyc\n.env\n/tmp/\n*.db" > .gitignore
git add .
git commit -m "Initial commit: tracking personal bot + PWA"
git remote add origin https://github.com/TU_USUARIO/tracking-bot.git
git push -u origin main
```

## 6. Deploy API en Render

1. Andá a https://render.com/ y logueate con GitHub
2. **New → Web Service**
3. Conectá tu repo `tracking-bot`
4. Configurá:
   - **Name**: `tracking-api`
   - **Root Directory**: `api`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. En **Environment Variables** agregá:
   ```
   TELEGRAM_BOT_TOKEN=<token del paso 1>
   GROQ_API_KEY=<key del paso 2>
   TURSO_DATABASE_URL=<url del paso 3>
   TURSO_AUTH_TOKEN=<token del paso 3>
   AUTH_EMAIL=tu@email.com
   AUTH_PASSWORD_HASH=<hash del paso 4>
   JWT_SECRET=<generá uno: openssl rand -hex 32>
   FRONTEND_URL=https://tracking-web.onrender.com
   ALLOWED_CHAT_IDS=<tu chat_id del paso 1>
   ```
6. Click **Create Web Service**
7. Esperá que buildee (~2-3 min)
8. Copiá la URL que te da (ej: `https://tracking-api.onrender.com`)

## 7. Deploy Frontend en Render

1. **New → Static Site**
2. Conectá el mismo repo
3. Configurá:
   - **Name**: `tracking-web`
   - **Root Directory**: `web`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
4. En **Environment Variables**:
   ```
   VITE_API_URL=https://tracking-api.onrender.com
   ```
5. En **Redirects/Rewrites** agregá:
   - Source: `/*`
   - Destination: `/index.html`
   - Type: **Rewrite**
   (esto es para que el SPA routing funcione)
6. Click **Create Static Site**

## 8. Setear Webhook de Telegram

Una vez que la API esté deployada, ejecutá:

```bash
curl -X POST "https://api.telegram.org/bot<TU_TOKEN>/setWebhook?url=https://tracking-api.onrender.com/webhook"
```

Deberías recibir: `{"ok":true,"result":true,"description":"Webhook was set"}`

## 9. Configurar UptimeRobot

1. Andá a https://uptimerobot.com/ y creá cuenta (gratis)
2. **Add New Monitor**:
   - Type: HTTP(s)
   - URL: `https://tracking-api.onrender.com/health`
   - Interval: 5 minutes
3. Esto mantiene vivo el free tier de Render (se duerme a los 15 min de inactividad)

## 10. Probar todo

1. Abrí la PWA: `https://tracking-web.onrender.com`
2. Logueate con tu email y password
3. Mandá un mensaje al bot en Telegram: `almorcé milanesa, 700 cal`
4. Debería responder: `✓ 700 kcal`
5. Refrescá la PWA → debería aparecer en el dashboard
6. Probá audio: grabá un mensaje de voz → debe transcribir y parsear
7. Probá resumen: `resumen de los últimos 7 días` → texto + gráficos

## Importar datos del xlsx a producción

Una vez deployado, podés importar el xlsx editando el script para que apunte a Turso:

```bash
# En import_xlsx.py, cambiar:
# DB_PATH = "/tmp/tracking-dev.db"
# por usar libsql_client con las credenciales de Turso
```

O más simple: abrí `turso db shell tracking-bot` y ejecutá los INSERTs manualmente.

## Troubleshooting

- **Bot no responde**: verificá que el webhook esté seteado (`curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo`)
- **PWA no carga datos**: verificá CORS (la env `FRONTEND_URL` debe coincidir exactamente con la URL del static site)
- **Render se duerme**: verificá UptimeRobot está activo
- **Login falla**: verificá que el hash bcrypt sea correcto (generá uno nuevo si hace falta)
