# 📊 Sistema de Análisis de Stock Crítico

Sistema profesional para análisis de inventario basado en Curva ABC y cálculo de stock crítico. Procesa automáticamente archivos complejos exportados desde ERP y genera reportes ejecutivos.

## ✨ Características Principales

- 🔍 **Procesamiento Inteligente**: Maneja archivos ERP con celdas combinadas automáticamente
- 📈 **Análisis de Stock Crítico**: Identifica productos que requieren atención inmediata
- 🎯 **Clasificación ABC**: Prioriza productos según importancia estratégica
- 📊 **Dashboards Interactivos**: Visualizaciones profesionales en tiempo real
- 📋 **Reportes Ejecutivos**: Exportación a Excel con formato corporativo
- ⚡ **Alertas Automáticas**: Sistema de notificaciones por umbrales configurables

## 🚀 Demo en Vivo

[Ver Demo](https://tu-app.streamlit.app) _(disponible después del despliegue)_

## 📋 Requisitos del Sistema

- Python 3.9 o superior
- Archivos Excel (.xlsx/.xls) del ERP
- Navegador web moderno

## 🔧 Instalación Local

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/stock-analyzer.git
cd stock-analyzer
```

### 2. Crear Entorno Virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar la Aplicación
```bash
streamlit run app.py
```

La aplicación estará disponible en `http://localhost:8501`

## 📁 Estructura del Proyecto

```
stock-analyzer/
├── .streamlit/
│   └── config.toml          # Configuración de Streamlit
├── src/
│   ├── data_processor.py    # Procesamiento de archivos ERP
│   ├── analyzer.py          # Análisis y métricas
│   └── utils.py            # Utilidades y exportación
├── data/                   # Archivos de ejemplo (opcional)
├── assets/                 # Recursos estáticos
├── app.py                 # Aplicación principal
├── requirements.txt       # Dependencias Python
└── README.md             # Este archivo
```

## 📊 Formato de Archivos

### Archivo Curva ABC (ERP Export)
El sistema procesa automáticamente archivos con:
- Celdas combinadas
- Múltiples servicios (Desayuno, Almuerzo, Cena, etc.)
- Información de fechas y períodos
- Clasificación por curvas A, B, C

### Archivo de Stock
Inventario actual con:
- Códigos de productos
- Descripciones
- Stock disponible
- Precios (opcional)
- Familias de productos

## 🎯 Funcionalidades

### Dashboard Principal
- Métricas clave de inventario
- Distribución por estados de stock
- Análisis por curva ABC
- Alertas automáticas

### Análisis de Stock Crítico
- Identificación de productos sin stock
- Cálculo de días de cobertura
- Proyección de fechas de quiebre
- Priorización por curva ABC

### Reportes de Reposición
- Cantidades sugeridas de compra
- Priorización por criticidad
- Análisis por familia de productos
- Exportación a Excel profesional

### Exportación
- Reportes ejecutivos en Excel
- Dashboards con formato corporativo
- Archivos CSV para análisis adicional
- Gráficos embebidos

## 🔧 Configuración

### Umbrales de Alerta (Personalizables)
- **Curva A**: 3 días (productos críticos)
- **Curva B**: 5 días (productos importantes)  
- **Curva C**: 7 días (productos normales)

### Cálculo de Cobertura
```
Días de Cobertura = Stock Actual / Consumo Promedio Diario
Consumo Promedio Diario = Consumo Total del Período / Días del Período
```

## 📈 Métricas Calculadas

- **Stock Crítico**: Productos por debajo del umbral según curva ABC
- **Días de Cobertura**: Tiempo estimado hasta agotamiento
- **Valor de Inventario**: Valorización total del stock
- **Tasa de Rotación**: Velocidad de movimiento por producto
- **Proyección de Quiebre**: Fechas estimadas de agotamiento

## 🚀 Despliegue en Streamlit Cloud

1. **Subir a GitHub**: Sube tu código a un repositorio público
2. **Conectar Streamlit Cloud**: Vincula tu repositorio
3. **Configurar Variables**: Define configuraciones si es necesario
4. **Desplegar**: La aplicación estará lista en minutos

[Ver guía completa de despliegue](#despliegue)

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🆘 Soporte

### Problemas Comunes

**Error al procesar archivos ERP:**
- Verifica que el archivo tenga formato .xlsx o .xls
- Asegúrate de que contenga las hojas necesarias
- Revisa que no esté protegido con contraseña

**Aplicación no carga:**
- Verifica que todas las dependencias estén instaladas
- Comprueba la versión de Python (3.9+)
- Revisa los logs en la consola

**Gráficos no se muestran:**
- Actualiza el navegador
- Verifica conexión a internet
- Limpia caché del navegador

### Contacto

- 📧 Email: tu-email@empresa.com
- 💼 LinkedIn: [Tu Perfil](https://linkedin.com/in/tu-perfil)
- 🐛 Issues: [GitHub Issues](https://github.com/tu-usuario/stock-analyzer/issues)

## 🙏 Agradecimientos

- [Streamlit](https://streamlit.io/) por la plataforma de desarrollo
- [Plotly](https://plotly.com/) por las visualizaciones interactivas
- [Pandas](https://pandas.pydata.org/) por el procesamiento de datos
- Comunidad open source por las herramientas utilizadas

---

**⭐ Si este proyecto te fue útil, no olvides darle una estrella en GitHub!**# StockCritico
