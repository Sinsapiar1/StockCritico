# 🚀 Guía de Despliegue - Stock Analyzer Pro

## Opciones de Despliegue

### 1. 🌐 Streamlit Cloud (Recomendado - GRATIS)

#### Paso 1: Preparar Repositorio GitHub
```bash
# 1. Crear repositorio en GitHub
# 2. Subir código
git init
git add .
git commit -m "Initial commit - Stock Analyzer Pro"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/stock-analyzer-pro.git
git push -u origin main
```

#### Paso 2: Desplegar en Streamlit Cloud
1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Conecta tu cuenta de GitHub
3. Selecciona tu repositorio `stock-analyzer-pro`
4. Archivo principal: `app.py`
5. ¡Listo! Tu app estará en: `https://tu-usuario-stock-analyzer-pro.streamlit.app`

### 2. 🐳 Docker (Para servidores propios)

#### Construir imagen
```bash
docker build -t stock-analyzer-pro .
```

#### Ejecutar contenedor
```bash
docker run -p 8501:8501 stock-analyzer-pro
```

#### Docker Compose
```yaml
version: '3.8'
services:
  stock-analyzer:
    build: .
    ports:
      - "8501:8501"
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
    restart: unless-stopped
```

### 3. ☁️ Heroku

#### Archivos necesarios
1. `Procfile`:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

2. `runtime.txt`:
```
python-3.11.4
```

#### Comandos de despliegue
```bash
heroku create tu-stock-analyzer
git push heroku main
```

### 4. 🔧 Servidor Local/VPS

#### Usando el script de inicio
```bash
./start.sh
```

#### Manual
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## Configuraciones Importantes

### Variables de Entorno
```bash
# Opcional: configurar puerto personalizado
export STREAMLIT_SERVER_PORT=8501

# Opcional: configurar dominio
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### Configuración de Firewall (VPS)
```bash
# Abrir puerto 8501
sudo ufw allow 8501
```

### Configuración Nginx (Opcional)
```nginx
server {
    listen 80;
    server_name tu-dominio.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Verificación de Despliegue

### Checklist Post-Despliegue
- [ ] La aplicación carga sin errores
- [ ] Se pueden subir archivos Excel
- [ ] Los gráficos se renderizan correctamente
- [ ] La exportación a Excel funciona
- [ ] Las métricas se calculan correctamente
- [ ] El diseño responsivo funciona en móviles

### URLs de Prueba
- **Local**: http://localhost:8501
- **Streamlit Cloud**: https://tu-usuario-stock-analyzer-pro.streamlit.app
- **Heroku**: https://tu-stock-analyzer.herokuapp.com

## Solución de Problemas

### Error: "Module not found"
```bash
pip install -r requirements.txt --upgrade
```

### Error: "Port already in use"
```bash
# Cambiar puerto
streamlit run app.py --server.port 8502
```

### Error: "Memory limit exceeded"
- Reducir tamaño de archivos de prueba
- Optimizar procesamiento de datos
- Considerar upgrade de plan en cloud

### Logs de Debugging
```bash
# Ver logs en Streamlit Cloud
streamlit run app.py --logger.level debug

# Ver logs en Docker
docker logs container-name
```

## Mejores Prácticas

### Seguridad
- No incluir datos sensibles en el repositorio
- Usar variables de entorno para configuraciones
- Implementar límites de tamaño de archivo
- Validar entrada de usuarios

### Performance
- Usar `@st.cache_data` para datos grandes
- Optimizar consultas de pandas
- Implementar paginación para tablas grandes
- Comprimir archivos de salida

### Monitoreo
- Configurar alertas de uptime
- Monitorear uso de memoria
- Trackear errores con Sentry (opcional)
- Analizar métricas de uso

## Soporte

### Recursos Útiles
- [Documentación Streamlit](https://docs.streamlit.io)
- [Streamlit Community](https://discuss.streamlit.io)
- [GitHub Issues](https://github.com/tu-usuario/stock-analyzer-pro/issues)

### Contacto
- 📧 Email: soporte@tu-empresa.com
- 💬 Discord: [Tu Server](https://discord.gg/tu-server)
- 📱 WhatsApp: +56 9 XXXX XXXX

---

**🎯 ¡Tu Stock Analyzer Pro está listo para producción!**