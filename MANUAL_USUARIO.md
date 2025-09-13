# 📖 MANUAL DE USUARIO - Stock Analyzer Pro

**Sistema Experto de Análisis de Inventario**  
**Desarrollado por: Adeodato Cornejo**

---

## 🎯 ¿QUÉ HACE ESTA APLICACIÓN?

**Stock Analyzer Pro** analiza tu inventario y te dice **cuántos días te durará cada producto** basándose en el consumo histórico vs stock actual.

### **En Palabras Simples:**
1. **Subes 2 archivos**: Curva ABC (consumo) + Stock (inventario)
2. **El sistema calcula**: Cuánto consumes por día de cada producto
3. **Te muestra**: Qué productos se van a agotar pronto
4. **Generas reportes**: Para tomar decisiones de compra

---

## 🚀 CÓMO USAR LA APLICACIÓN

### **Paso 1: Preparar Archivos**

#### **Archivo 1: Curva ABC (Del ERP)**
- Exporta desde tu ERP el reporte de "Curva ABC Realizado"
- Debe incluir: códigos, descripciones, consumo, fechas
- Formato: Excel (.xlsx o .xls)
- Puede tener cualquier rango de fechas (ej: 1-20 enero)

#### **Archivo 2: Stock Actual**
- Exporta tu inventario actual
- Debe incluir: códigos, descripciones, cantidades
- Formato: Excel (.xlsx o .xls)

### **Paso 2: Usar la Aplicación**

1. **Ve a**: https://stockcritico.streamlit.app
2. **Click**: "🚀 Comenzar Análisis"
3. **Sube**: Archivo Curva ABC
4. **Sube**: Archivo Stock
5. **Espera**: 1-2 minutos (procesamiento automático)
6. **¡Listo!**: Ve tus resultados

---

## 📊 INTERPRETACIÓN DE RESULTADOS

### **Dashboard Principal**

#### **🎯 Métricas Clave:**
- **Productos Analizados**: Total de productos procesados
- **Stock Crítico**: Productos que necesitas reponer YA
- **Cobertura Promedio**: Cuántos días te dura el stock en promedio
- **% en Riesgo**: Porcentaje de productos con problemas

#### **🧠 Insights Automáticos:**
- **Verde** ✅: Situación controlada (< 5% críticos)
- **Amarillo** ⚠️: Atención requerida (5-20% críticos)
- **Rojo** 🚨: Situación crítica (> 20% críticos)

### **Análisis por Curva ABC**

#### **🔴 Curva A (Productos Estratégicos)**
- **80% del consumo total**
- **Máxima prioridad** de reposición
- Si aparece en crítico: **URGENTE**

#### **🟡 Curva B (Productos Importantes)**
- **15% del consumo total**
- **Prioridad media** de reposición
- Seguimiento regular necesario

#### **🟢 Curva C (Productos de Bajo Consumo)**
- **5% del consumo total**
- **Menor prioridad** de reposición
- Suelen tener más productos críticos (normal)

### **Análisis por Servicios**

#### **Categorías Automáticas:**
- **🥐 Desayuno**: Huevos, pan, leche, yogurt, café
- **🍽️ Almuerzo/Cena**: Carnes, empanadas, arroz, papas
- **🍪 Colaciones**: Galletas, chocolates, bebidas
- **🍰 Postres**: Helados, flanes, dulces

---

## 🧮 CÓMO SE CALCULAN LAS MÉTRICAS

### **Fórmula Principal:**
```
Días de Cobertura = Stock Actual ÷ Consumo Promedio Diario
```

### **Ejemplo Práctico:**
**Producto: HUEVO PRIMERA BLANCO (359)**
- Consumo en período: 33,840 unidades
- Período: 8 días (01/09 - 08/09)
- Consumo diario: 33,840 ÷ 8 = 4,230 unidades/día
- Stock actual: 10,000 unidades
- **Días de cobertura: 10,000 ÷ 4,230 = 2.4 días**

### **Estados de Criticidad:**

#### **🔴 CRÍTICO**
- **Curva A**: ≤ 3 días
- **Curva B**: ≤ 5 días  
- **Curva C**: ≤ 7 días
- **Acción**: Reponer INMEDIATAMENTE

#### **🟡 BAJO**
- **Curva A**: 4-6 días
- **Curva B**: 6-10 días
- **Curva C**: 8-14 días
- **Acción**: Planificar reposición

#### **🟢 NORMAL**
- **Curva A**: 7-12 días
- **Curva B**: 11-20 días
- **Curva C**: 15-28 días
- **Acción**: Seguimiento regular

#### **🔵 NO CONSUMIDO**
- Sin consumo en el período analizado
- Stock sin rotación
- **Acción**: Revisar obsolescencia

---

## 📤 REPORTES Y EXPORTACIÓN

### **Reporte Excel Ejecutivo**
**Incluye 6 hojas:**
1. Resumen con KPIs principales
2. Lista de productos críticos
3. Análisis completo de inventario
4. Reporte de reposición con cantidades
5. Métricas por curva ABC
6. **Stock completo** (TODOS los productos)

### **Descargas Rápidas**
- **CSV Críticos**: Solo productos que necesitas reponer
- **CSV Completo**: Todos los datos para análisis adicional

---

## 🎯 CASOS DE USO PRÁCTICOS

### **Uso Diario - Jefe de Inventarios**
1. Sube archivos actualizados
2. Revisa dashboard principal
3. Ve productos críticos
4. Genera lista de reposición

### **Uso Semanal - Gerente de Operaciones**
1. Análisis completo de tendencias
2. Revisa análisis por curva ABC
3. Exporta reporte ejecutivo
4. Presenta resultados a dirección

### **Uso Mensual - Analista de Compras**
1. Análisis de productos sin consumo
2. Revisa patrones de obsolescencia
3. Optimiza políticas de inventario
4. Ajusta niveles de stock

---

## 🔍 INTERPRETACIÓN DE ALERTAS

### **🚨 Alertas Críticas**
- **Productos sin stock**: Agotados completamente
- **Curva A críticos**: Productos estratégicos en riesgo
- **Quiebre hoy**: Productos que se agotan en ≤1 día

### **⚠️ Alertas de Atención**
- **Stock bajo**: Requiere seguimiento
- **Cobertura baja**: Revisar políticas de reposición
- **Exceso de stock**: Posible sobrestock

### **✅ Indicadores Positivos**
- **Sin productos críticos**: Situación controlada
- **Cobertura adecuada**: Niveles óptimos
- **Balance por curva**: Distribución correcta

---

## 🎨 CARACTERÍSTICAS DE LA INTERFAZ

### **Diseño Responsivo**
- Funciona en computadora, tablet y móvil
- Gráficos interactivos
- Navegación intuitiva

### **Colores y Significados**
- **🔴 Rojo**: Crítico, urgente, requiere acción inmediata
- **🟡 Amarillo**: Atención, seguimiento necesario
- **🟢 Verde**: Normal, situación controlada
- **🔵 Azul**: Información, sin consumo

### **Navegación**
- **Tabs principales**: Dashboard, Curva ABC, Servicios, Avanzado, Exportar
- **Filtros**: Por estado, curva, rango de días
- **Ordenamiento**: Por criticidad, consumo, cobertura

---

## 🔧 SOLUCIÓN DE PROBLEMAS

### **Errores Comunes**

#### **"Error procesando Curva ABC"**
**Causas:**
- Archivo no es Excel (.xlsx/.xls)
- Archivo protegido con contraseña
- Formato no reconocido

**Solución:**
- Verificar formato de archivo
- Remover protección
- Exportar nuevamente desde ERP

#### **"No se encontraron productos en stock"**
**Causas:**
- Archivo de stock vacío
- Códigos de producto no coinciden
- Formato de columnas incorrecto

**Solución:**
- Verificar que archivo tenga datos
- Revisar códigos de productos
- Exportar con formato estándar

#### **"Aplicación lenta"**
**Causas:**
- Archivos muy grandes (>50MB)
- Conexión lenta
- Muchos usuarios simultáneos

**Solución:**
- Dividir archivos grandes
- Usar conexión estable
- Intentar en horario de menor uso

---

## 📈 MEJORES PRÁCTICAS

### **Preparación de Datos**
1. **Exportar semanalmente** para análisis regular
2. **Verificar códigos** entre archivos ABC y Stock
3. **Usar períodos consistentes** (ej: siempre 7 días)
4. **Mantener formato estándar** de exportación

### **Interpretación de Resultados**
1. **Priorizar Curva A** críticos siempre
2. **Revisar productos sin consumo** mensualmente
3. **Ajustar umbrales** según necesidades operativas
4. **Usar proyecciones** para planificación

### **Toma de Decisiones**
1. **Críticos**: Reponer inmediatamente
2. **Bajos**: Planificar en 2-3 días
3. **Sin consumo**: Analizar obsolescencia
4. **Exceso**: Revisar políticas de compra

---

## 🎯 RESULTADOS ESPERADOS

### **Beneficios Inmediatos**
- ⏱️ **Ahorro de tiempo**: 95% menos tiempo en análisis
- 🎯 **Precisión**: Cálculos automáticos sin errores
- 📊 **Visibilidad**: Dashboard en tiempo real
- 📋 **Reportes**: Listos para presentar

### **Beneficios a Mediano Plazo**
- 📉 **Reducción de quiebres**: Identificación temprana
- 💰 **Optimización de capital**: Mejor gestión de inventario
- 📈 **Mejora de KPIs**: Indicadores de gestión
- 🎯 **Decisiones basadas en datos**: Análisis objetivo

---

## 🆘 SOPORTE TÉCNICO

### **Recursos Disponibles**
- **Manual Técnico**: HANDOFF_TECNICO.md
- **Guía de Despliegue**: DEPLOYMENT.md
- **Código Fuente**: GitHub repository

### **Contacto**
- **Desarrollador**: Adeodato Cornejo
- **Aplicación**: https://stockcritico.streamlit.app
- **Repositorio**: https://github.com/Sinsapiar1/StockCritico

---

**🎯 Stock Analyzer Pro - Transformando datos de inventario en decisiones inteligentes**

**Desarrollado con excelencia por Adeodato Cornejo | 2025**