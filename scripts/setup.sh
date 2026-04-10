#!/bin/bash
set -euo pipefail

echo "=== Tracking Bot Setup ==="
echo ""

# 1. Generate bcrypt hash
echo "1. Generar hash de password"
echo "   Ejecutá esto en Python para generar tu hash:"
echo '   python3 -c "import bcrypt; print(bcrypt.hashpw(input(\"Password: \").encode(), bcrypt.gensalt()).decode())"'
echo ""

# 2. Turso setup
echo "2. Crear DB en Turso"
echo "   turso db create tracking-bot"
echo "   turso db show tracking-bot --url"
echo "   turso db tokens create tracking-bot"
echo ""

# 3. Init schema
echo "3. Inicializar schema"
echo "   turso db shell tracking-bot < schema.sql"
echo "   (o copiar el SQL del schema y ejecutarlo en turso db shell)"
echo ""

# 4. Set webhook
echo "4. Setear webhook de Telegram"
echo "   Reemplazá <TOKEN> y <API_URL>:"
echo '   curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook?url=<API_URL>/webhook"'
echo ""

# 5. UptimeRobot
echo "5. Crear monitor en UptimeRobot"
echo "   URL: <API_URL>/health"
echo "   Tipo: HTTP(s)"
echo "   Intervalo: 5 minutos"
echo ""

# 6. Render deploy
echo "6. Deploy en Render"
echo "   - API: New Web Service → Python → apuntar a /api"
echo "   - Web: New Static Site → Build: cd web && npm install && npm run build → Publish: web/dist"
echo "   - Agregar rewrite rule: /* → /index.html (para SPA routing)"
echo ""

echo "=== Variables de entorno requeridas ==="
echo "TELEGRAM_BOT_TOKEN="
echo "GROQ_API_KEY="
echo "TURSO_DATABASE_URL=libsql://xxx.turso.io"
echo "TURSO_AUTH_TOKEN="
echo "AUTH_EMAIL=tu@email.com"
echo "AUTH_PASSWORD_HASH=\$2b\$12\$..."
echo "JWT_SECRET=$(openssl rand -hex 32)"
echo "FRONTEND_URL=https://tracking-web.onrender.com"
echo "ALLOWED_CHAT_IDS=tu_chat_id"
echo ""
echo "Para obtener tu chat_id, mandá /start a @userinfobot en Telegram"
