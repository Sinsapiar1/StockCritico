import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os
import time

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_processor import ERPDataProcessor
from analyzer import StockAnalyzer
from utils import ExcelExporter, AlertManager, format_number, format_currency

# Configuración de la página
st.set_page_config(
    page_title="Stock Analyzer Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado para diseño moderno y responsivo
st.markdown("""
<style>
    /* Reset y base */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Header principal */
    .hero-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 3rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        opacity: 0.9;
        font-weight: 300;
    }
    
    /* Cards de pasos */
    .step-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        border-left: 5px solid #667eea;
        margin-bottom: 2rem;
        transition: transform 0.3s ease;
    }
    
    .step-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }
    
    .step-number {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .step-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .step-description {
        color: #7f8c8d;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    /* Área de upload mejorada */
    .upload-zone {
        border: 3px dashed #667eea;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        background: #f8f9ff;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .upload-zone:hover {
        border-color: #764ba2;
        background: #f0f2ff;
    }
    
    /* Progress bar personalizada */
    .progress-container {
        background: #e9ecef;
        border-radius: 10px;
        padding: 5px;
        margin: 1rem 0;
    }
    
    .progress-bar {
        background: linear-gradient(90deg, #667eea, #764ba2);
        height: 20px;
        border-radius: 8px;
        transition: width 0.5s ease;
    }
    
    /* Métricas mejoradas */
    .metric-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 3px 15px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 4px solid #667eea;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        color: #7f8c8d;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Alertas mejoradas */
    .alert-critical {
        background: linear-gradient(135deg, #ff6b6b, #ff5252);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #ffa726, #ff9800);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .alert-success {
        background: linear-gradient(135deg, #66bb6a, #4caf50);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    /* Botones mejorados */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Tabs mejoradas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        border: none;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
    }
    
    /* Responsividad */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2rem;
        }
        
        .hero-subtitle {
            font-size: 1rem;
        }
        
        .step-card {
            padding: 1.5rem;
        }
        
        .metric-value {
            font-size: 2rem;
        }
    }
    
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Loading animation */
    .loading-spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        animation: spin 1s linear infinite;
        margin: 2rem auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Inicializar session state
    if 'step' not in st.session_state:
        st.session_state.step = 0
    if 'curva_abc_file' not in st.session_state:
        st.session_state.curva_abc_file = None
    if 'stock_file' not in st.session_state:
        st.session_state.stock_file = None
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False

    # Header principal
    show_hero_header()
    
    # Control de flujo principal
    if st.session_state.step == 0:
        show_welcome_screen()
    elif st.session_state.step == 1:
        show_upload_curva_abc()
    elif st.session_state.step == 2:
        show_upload_stock()
    elif st.session_state.step == 3:
        show_processing()
    elif st.session_state.step == 4:
        show_results()

def show_hero_header():
    """Header principal con diseño atractivo"""
    st.markdown("""
    <div class="hero-header">
        <div class="hero-title">🎯 Stock Analyzer Pro</div>
        <div class="hero-subtitle">Sistema Inteligente de Análisis de Inventario Crítico</div>
        <div style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.8;">
            Desarrollado por <strong>Adeodato Cornejo</strong> | Análisis Experto de Stock vs Consumo
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_welcome_screen():
    """Pantalla de bienvenida moderna"""
    
    # Progress bar
    show_progress_bar(0, 4)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="step-card">
            <div style="text-align: center;">
                <h2 style="color: #2c3e50; margin-bottom: 2rem;">Bienvenido al Análisis Profesional</h2>
                <p style="font-size: 1.2rem; color: #7f8c8d; line-height: 1.8; margin-bottom: 2rem;">
                    Transforma tus datos de inventario en insights accionables con solo dos clics. 
                    Nuestro sistema analiza automáticamente tu Curva ABC y Stock actual para 
                    identificar productos críticos y generar reportes ejecutivos.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Características principales
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">⚡</div>
                <h4 style="color: #2c3e50;">Procesamiento Automático</h4>
                <p style="color: #7f8c8d;">Maneja archivos complejos del ERP sin intervención manual</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_b:
            st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
                <h4 style="color: #2c3e50;">Dashboards Ejecutivos</h4>
                <p style="color: #7f8c8d;">Visualizaciones profesionales y reportes listos para presentar</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_c:
            st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🎯</div>
                <h4 style="color: #2c3e50;">Stock Crítico</h4>
                <p style="color: #7f8c8d;">Identifica productos que requieren atención inmediata</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Botón de inicio
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 Comenzar Análisis", key="start_analysis"):
            st.session_state.step = 1
            st.rerun()

def show_upload_curva_abc():
    """Paso 1: Upload de archivo Curva ABC"""
    
    show_progress_bar(1, 4)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="step-card">
            <div class="step-number">1</div>
            <div class="step-title">Subir Archivo Curva ABC</div>
            <div class="step-description">
                Selecciona el archivo exportado desde tu ERP que contiene los datos de consumo 
                y clasificación ABC de productos.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="upload-zone">', unsafe_allow_html=True)
        
        curva_abc_file = st.file_uploader(
            "📊 Arrastra aquí tu archivo Curva ABC",
            type=['xlsx', 'xls'],
            help="Formato: Excel (.xlsx, .xls) - Exportado desde el ERP",
            label_visibility="visible"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if curva_abc_file:
            st.session_state.curva_abc_file = curva_abc_file
            
            # Mostrar información del archivo
            st.markdown("""
            <div class="alert-success">
                ✅ Archivo cargado correctamente: {} ({:.2f} MB)
            </div>
            """.format(curva_abc_file.name, curva_abc_file.size / 1024 / 1024), unsafe_allow_html=True)
            
            # Botón para continuar
            if st.button("➡️ Continuar al Siguiente Paso", key="next_to_stock"):
                st.session_state.step = 2
                st.rerun()
        
        # Botón para volver
        if st.button("⬅️ Volver al Inicio", key="back_to_start"):
            st.session_state.step = 0
            st.rerun()

def show_upload_stock():
    """Paso 2: Upload de archivo Stock"""
    
    show_progress_bar(2, 4)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="step-card">
            <div class="step-number">2</div>
            <div class="step-title">Subir Archivo de Stock</div>
            <div class="step-description">
                Selecciona el archivo que contiene tu inventario actual con códigos de productos 
                y cantidades disponibles.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar archivo ABC ya cargado
        if st.session_state.curva_abc_file:
            st.markdown("""
            <div style="background: #e8f5e8; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                ✅ <strong>Curva ABC:</strong> {} ya cargado
            </div>
            """.format(st.session_state.curva_abc_file.name), unsafe_allow_html=True)
        
        st.markdown('<div class="upload-zone">', unsafe_allow_html=True)
        
        stock_file = st.file_uploader(
            "📦 Arrastra aquí tu archivo de Stock",
            type=['xlsx', 'xls'],
            help="Formato: Excel (.xlsx, .xls) - Inventario actual",
            label_visibility="visible"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if stock_file:
            st.session_state.stock_file = stock_file
            
            # Mostrar información del archivo
            st.markdown("""
            <div class="alert-success">
                ✅ Archivo cargado correctamente: {} ({:.2f} MB)
            </div>
            """.format(stock_file.name, stock_file.size / 1024 / 1024), unsafe_allow_html=True)
            
            # Botón para procesar
            if st.button("🔮 Procesar Análisis Completo", key="process_analysis"):
                st.session_state.step = 3
                st.rerun()
        
        # Botón para volver
        if st.button("⬅️ Volver al Paso Anterior", key="back_to_curva"):
            st.session_state.step = 1
            st.rerun()

def show_processing():
    """Paso 3: Procesamiento automático"""
    
    show_progress_bar(3, 4)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="step-card">
            <div class="step-number">3</div>
            <div class="step-title">Procesando Análisis Inteligente</div>
            <div class="step-description">
                Nuestro sistema está analizando tus archivos y generando insights profesionales. 
                Este proceso toma aproximadamente 30-60 segundos.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Animación de carga
        st.markdown('<div class="loading-spinner"></div>', unsafe_allow_html=True)
        
        # Progress text
        progress_text = st.empty()
        progress_bar = st.progress(0)
        
        # Simular procesamiento con pasos
        steps = [
            "🔍 Analizando estructura de archivos...",
            "📊 Procesando datos de Curva ABC...", 
            "📦 Consolidando información de Stock...",
            "🎯 Calculando stock crítico...",
            "📈 Generando métricas y KPIs...",
            "🎨 Creando visualizaciones...",
            "✅ Finalizando análisis..."
        ]
        
        for i, step in enumerate(steps):
            progress_text.text(step)
            progress_bar.progress((i + 1) / len(steps))
            time.sleep(0.8)  # Simular tiempo de procesamiento
        
        # Procesamiento real
        try:
            processor = ERPDataProcessor()
            
            # Procesar archivos
            curva_abc_data = processor.process_curva_abc(st.session_state.curva_abc_file)
            stock_data = processor.process_stock(st.session_state.stock_file)
            analysis_data = processor.calculate_coverage_analysis(8)  # Default 8 días
            
            # Guardar en session state
            st.session_state.analysis_data = analysis_data
            st.session_state.processor = processor
            st.session_state.analysis_complete = True
            
            progress_text.text("🎉 ¡Análisis completado exitosamente!")
            progress_bar.progress(1.0)
            
            time.sleep(1)
            st.session_state.step = 4
            st.rerun()
            
        except Exception as e:
            error_msg = str(e)
            st.markdown(f"""
            <div class="alert-critical">
                ❌ Error en el procesamiento: {error_msg}
            </div>
            """, unsafe_allow_html=True)
            
            # Mostrar sugerencias según el tipo de error
            if "stock" in error_msg.lower():
                st.markdown("""
                <div class="alert-warning">
                    💡 <strong>Sugerencias para el archivo de Stock:</strong><br>
                    • Verifica que el archivo contenga códigos de productos numéricos<br>
                    • Asegúrate de que tenga columnas con descripciones y cantidades<br>
                    • El archivo debe estar en formato Excel (.xlsx o .xls)<br>
                    • Revisa que no tenga protección por contraseña
                </div>
                """, unsafe_allow_html=True)
            elif "abc" in error_msg.lower():
                st.markdown("""
                <div class="alert-warning">
                    💡 <strong>Sugerencias para el archivo Curva ABC:</strong><br>
                    • Debe contener códigos de productos y consumos<br>
                    • Verifica que tenga datos de clasificación ABC<br>
                    • Asegúrate de que sea la exportación correcta del ERP
                </div>
                """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Reintentar", key="retry_processing"):
                    st.session_state.step = 3
                    st.rerun()
            
            with col2:
                if st.button("⬅️ Volver a Subir Archivos", key="back_to_upload"):
                    st.session_state.step = 1
                    st.rerun()

def show_results():
    """Paso 4: Mostrar resultados del análisis"""
    
    show_progress_bar(4, 4)
    
    if not st.session_state.analysis_complete:
        st.error("No hay análisis completado")
        return
    
    data = st.session_state.analysis_data
    analyzer = StockAnalyzer(data)
    
    # Header de resultados
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: #2c3e50; font-size: 2.5rem; margin-bottom: 0.5rem;">📊 Análisis Completado</h1>
        <p style="color: #7f8c8d; font-size: 1.2rem;">Dashboard ejecutivo generado automáticamente</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Alertas críticas
    alerts = AlertManager.check_critical_alerts(data)
    if alerts:
        for alert in alerts:
            if alert['type'] == 'error':
                st.markdown(f"""
                <div class="alert-critical">
                    🚨 <strong>{alert['title']}:</strong> {alert['message']}
                </div>
                """, unsafe_allow_html=True)
            elif alert['type'] == 'warning':
                st.markdown(f"""
                <div class="alert-warning">
                    ⚠️ <strong>{alert['title']}:</strong> {alert['message']}
                </div>
                """, unsafe_allow_html=True)
    
    # KPIs principales
    show_main_kpis(analyzer)
    
    # Tabs con análisis detallado
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard Principal", 
        "🎯 Análisis por Curva ABC", 
        "🍽️ Análisis por Servicios",
        "📈 Análisis Avanzado",
        "📤 Exportar Reportes"
    ])
    
    with tab1:
        show_dashboard_tab(analyzer)
    
    with tab2:
        show_curva_abc_tab(analyzer)
    
    with tab3:
        show_services_analysis_tab(analyzer)
    
    with tab4:
        show_advanced_analysis_tab(analyzer)
    
    with tab5:
        show_export_tab(analyzer, data)
    
    # Botón para nuevo análisis
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("🔄 Realizar Nuevo Análisis", key="new_analysis"):
            # Reset session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Footer profesional
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 10px; margin-top: 3rem;">
        <div style="color: #6c757d; font-size: 0.9rem;">
            <strong>🎯 Stock Analyzer Pro</strong> - Sistema Experto de Análisis de Inventario<br>
            Desarrollado por <strong style="color: #667eea;">Adeodato Cornejo</strong><br>
            <small>Análisis inteligente de stock vs consumo | Metodología experta en gestión de inventarios</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_progress_bar(current_step, total_steps):
    """Muestra barra de progreso del flujo"""
    progress_percentage = (current_step / total_steps) * 100
    
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-bar" style="width: {progress_percentage}%;"></div>
    </div>
    <div style="text-align: center; color: #7f8c8d; margin-bottom: 2rem;">
        Paso {current_step} de {total_steps}
    </div>
    """, unsafe_allow_html=True)

def show_main_kpis(analyzer):
    """Dashboard principal profesional con insights inteligentes"""
    
    metrics = analyzer.get_summary_metrics()
    data = analyzer.data
    
    # Header con contexto claro
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="color: #2c3e50; margin-bottom: 0.5rem;">📊 Análisis de Cobertura de Stock</h2>
        <p style="color: #7f8c8d; font-size: 1.1rem;">
            Evaluación de días de cobertura basada en consumo histórico vs stock actual
        </p>
        <div style="background: #e3f2fd; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
            <strong>🧮 Metodología de Cálculo:</strong><br>
            <code>Consumo Diario = Consumo Total del Período ÷ 8 días (01/09 - 08/09/2025)</code><br>
            <code>Días de Cobertura = Stock Actual ÷ Consumo Promedio Diario</code>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # KPIs principales con explicaciones
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📦</div>
            <div class="metric-value">{metrics['total_productos']}</div>
            <div class="metric-label">Productos Analizados</div>
            <div style="color: #7f8c8d; font-size: 0.8rem; margin-top: 0.5rem;">
                Con stock y consumo válidos
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        critical_pct = (metrics['productos_criticos'] / metrics['total_productos'] * 100) if metrics['total_productos'] > 0 else 0
        urgency_icon = "🚨" if critical_pct > 15 else "⚠️" if critical_pct > 5 else "✅"
        
        st.markdown(f"""
        <div class="metric-container" style="border-top-color: #ff6b6b;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{urgency_icon}</div>
            <div class="metric-value" style="color: #ff6b6b;">{metrics['productos_criticos']}</div>
            <div class="metric-label">Stock Crítico</div>
            <div style="color: #ff6b6b; font-size: 0.8rem; margin-top: 0.5rem;">
                Requieren reposición inmediata
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_coverage = data['dias_cobertura'].mean()
        coverage_icon = "📈" if avg_coverage > 15 else "📊" if avg_coverage > 7 else "📉"
        
        st.markdown(f"""
        <div class="metric-container" style="border-top-color: #4ECDC4;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{coverage_icon}</div>
            <div class="metric-value" style="color: #4ECDC4;">{avg_coverage:.1f}</div>
            <div class="metric-label">Días Cobertura Promedio</div>
            <div style="color: #7f8c8d; font-size: 0.8rem; margin-top: 0.5rem;">
                Stock actual ÷ consumo diario
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Valor total en riesgo (productos críticos)
        critical_products = data[data['estado_stock'] == 'CRÍTICO']
        risk_value = (critical_products['stock'] * critical_products.get('precio', 0)).sum()
        
        st.markdown(f"""
        <div class="metric-container" style="border-top-color: #FF8800;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">💰</div>
            <div class="metric-value" style="color: #FF8800; font-size: 1.8rem;">{critical_pct:.1f}%</div>
            <div class="metric-label">Productos en Riesgo</div>
            <div style="color: #7f8c8d; font-size: 0.8rem; margin-top: 0.5rem;">
                Del total de inventario
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Insights inteligentes
    st.markdown("<br>", unsafe_allow_html=True)
    show_intelligent_insights(data, metrics)

def show_intelligent_insights(data, metrics):
    """Muestra insights inteligentes basados en los datos"""
    
    # Análisis automático
    critical_pct = (metrics['productos_criticos'] / metrics['total_productos'] * 100) if metrics['total_productos'] > 0 else 0
    avg_coverage = data['dias_cobertura'].mean()
    
    # Productos más críticos por curva
    curva_a_critical = len(data[(data['curva'] == 'A') & (data['estado_stock'] == 'CRÍTICO')])
    curva_b_critical = len(data[(data['curva'] == 'B') & (data['estado_stock'] == 'CRÍTICO')])
    
    st.markdown("### 🧠 Insights Inteligentes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Alerta principal
        if critical_pct > 20:
            alert_type = "error"
            alert_icon = "🚨"
            alert_msg = f"SITUACIÓN CRÍTICA: {critical_pct:.1f}% de productos requieren reposición inmediata"
        elif critical_pct > 10:
            alert_type = "warning" 
            alert_icon = "⚠️"
            alert_msg = f"ATENCIÓN REQUERIDA: {critical_pct:.1f}% de productos en estado crítico"
        else:
            alert_type = "success"
            alert_icon = "✅"
            alert_msg = f"SITUACIÓN CONTROLADA: Solo {critical_pct:.1f}% de productos críticos"
        
        st.markdown(f"""
        <div class="alert-{alert_type}">
            {alert_icon} <strong>{alert_msg}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        # Recomendación por curva A
        if curva_a_critical > 0:
            st.markdown(f"""
            <div class="alert-warning">
                🎯 <strong>PRIORIDAD ALTA:</strong> {curva_a_critical} productos Curva A en estado crítico
                <br><small>Estos productos son estratégicos y requieren atención inmediata</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Análisis de cobertura
        if avg_coverage < 5:
            coverage_status = "🔴 Cobertura muy baja"
            coverage_msg = "La mayoría de productos se agotarán en menos de 5 días"
        elif avg_coverage < 10:
            coverage_status = "🟡 Cobertura moderada"  
            coverage_msg = "Revisar políticas de reposición y frecuencia de pedidos"
        else:
            coverage_status = "🟢 Cobertura adecuada"
            coverage_msg = "Los niveles de stock están dentro de rangos aceptables"
        
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #667eea;">
            <strong>{coverage_status}</strong><br>
            <small style="color: #6c757d;">{coverage_msg}</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Top 3 productos más críticos
        top_critical = data[data['estado_stock'] == 'CRÍTICO'].nsmallest(3, 'dias_cobertura')
        if len(top_critical) > 0:
            st.markdown("**🔥 Más Urgentes:**")
            for _, product in top_critical.iterrows():
                st.markdown(f"• **{product['codigo']}** - {product['descripcion'][:25]}... ({product['dias_cobertura']:.1f} días)")

def show_dashboard_tab(analyzer):
    """Tab del dashboard principal"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_status = analyzer.create_status_distribution_chart()
        st.plotly_chart(fig_status, use_container_width=True, key="dashboard_status_distribution")
    
    with col2:
        fig_curva = analyzer.create_coverage_by_curva_chart()
        st.plotly_chart(fig_curva, use_container_width=True, key="dashboard_coverage_by_curva")
    
    # Gráfico de productos críticos
    fig_critical = analyzer.create_critical_products_chart()
    st.plotly_chart(fig_critical, use_container_width=True, key="dashboard_critical_products")

def show_curva_abc_tab(analyzer):
    """Tab dedicado al análisis por Curva ABC"""
    
    data = analyzer.data
    
    st.markdown("### 🎯 Análisis por Curva ABC - Consumo Estratégico")
    
    st.markdown("""
    <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;">
        <h4 style="color: #2c3e50; margin-bottom: 1rem;">💡 ¿Qué es la Curva ABC?</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem;">
            <div style="text-align: center; padding: 1rem; background: white; border-radius: 8px; border-left: 4px solid #FF6B6B;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔴</div>
                <strong>Curva A</strong><br>
                <small>80% del consumo<br>Productos MÁS consumidos<br>Máxima prioridad</small>
            </div>
            <div style="text-align: center; padding: 1rem; background: white; border-radius: 8px; border-left: 4px solid #4ECDC4;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🟡</div>
                <strong>Curva B</strong><br>
                <small>15% del consumo<br>Consumo moderado<br>Prioridad media</small>
            </div>
            <div style="text-align: center; padding: 1rem; background: white; border-radius: 8px; border-left: 4px solid #45B7D1;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🟢</div>
                <strong>Curva C</strong><br>
                <small>5% del consumo<br>Productos MENOS consumidos<br>Menor prioridad</small>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: #fff3cd; padding: 1rem; border-radius: 8px; border-left: 4px solid #ffc107; margin-bottom: 2rem;">
        <strong>🧠 Insight Clave:</strong> La Curva C suele tener MÁS productos críticos porque al consumirse poco, 
        es fácil que se acumulen o que el stock no se rote adecuadamente, generando mayor criticidad.
    </div>
    """, unsafe_allow_html=True)
    
    # Análisis por cada curva
    available_curvas = sorted(data['curva'].unique())
    
    # Mostrar distribución general
    col1, col2, col3 = st.columns(3)
    
    for i, curva in enumerate(['A', 'B', 'C']):
        curva_data = data[data['curva'] == curva] if curva in available_curvas else pd.DataFrame()
        total_products = len(curva_data)
        critical_count = len(curva_data[curva_data['estado_stock'] == 'CRÍTICO']) if len(curva_data) > 0 else 0
        
        with [col1, col2, col3][i]:
            color = ['#FF6B6B', '#4ECDC4', '#45B7D1'][i]
            icon = ['🔴', '🟡', '🟢'][i]
            
            st.markdown(f"""
            <div style="background: white; padding: 1.5rem; border-radius: 10px; text-align: center; border-left: 4px solid {color};">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{icon}</div>
                <h3 style="color: {color}; margin-bottom: 0.5rem;">Curva {curva}</h3>
                <div style="font-size: 1.8rem; font-weight: bold; color: #2c3e50;">{total_products}</div>
                <div style="color: #7f8c8d; margin-bottom: 0.5rem;">Productos totales</div>
                {f'<div style="color: #FF4444; font-weight: bold;">{critical_count} críticos</div>' if critical_count > 0 else '<div style="color: #44AA44;">Sin productos críticos</div>'}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Explicación si solo hay una curva
    if len(available_curvas) == 1:
        st.markdown(f"""
        <div style="background: #e3f2fd; padding: 1rem; border-radius: 8px; border-left: 4px solid #2196f3; margin-bottom: 1rem;">
            <strong>ℹ️ Información:</strong> En tu análisis actual solo aparece <strong>Curva {available_curvas[0]}</strong>. 
            Esto significa que todos los productos analizados están clasificados en esta categoría según su nivel de consumo.
        </div>
        """, unsafe_allow_html=True)
    
    # Selector de curva para análisis detallado
    selected_curva = st.selectbox(
        "🔍 Selecciona una curva para análisis detallado:",
        options=available_curvas,
        index=0,
        help="Selecciona la curva que quieres analizar en detalle"
    )
    
    # Mostrar análisis detallado de la curva seleccionada
    show_detailed_curva_analysis(analyzer, data, selected_curva)

def show_services_analysis_tab(analyzer):
    """Tab de análisis EXPERTO por servicios - Enfoque Stock y Criticidad"""
    
    data = analyzer.data
    
    st.markdown("### 🍽️ Análisis Experto por Servicios - Stock vs Criticidad")
    
    # Información resumida para el usuario (sin debug técnico)
    if 'servicio' in data.columns:
        unique_services = data['servicio'].nunique()
        total_products = len(data)
        
    # Calcular estadísticas para mostrar
    productos_con_consumo = len(data[data['consumo_diario'] > 0])
    productos_sin_consumo = len(data[data['consumo_diario'] == 0])
    
    st.markdown(f"""
    <div style="background: #e8f5e8; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #28a745; margin-bottom: 2rem;">
        <h4 style="color: #2c3e50; margin-bottom: 1rem;">📊 Resumen Completo del Análisis</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div>
                <strong>📦 Stock Total:</strong> {total_products} productos<br>
                <strong>📅 Período:</strong> 8 días (01/09 - 08/09/2025)<br>
                <strong>🍽️ Servicios:</strong> {unique_services} detectados
            </div>
            <div>
                <strong>✅ Con Consumo:</strong> {productos_con_consumo} productos<br>
                <strong>📋 Sin Consumo:</strong> {productos_sin_consumo} productos<br>
                <small style="color: #6c757d;">Productos en inventario pero no consumidos en el período</small>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar si hay información de servicios
    if 'servicio' not in data.columns:
        st.markdown("""
        <div style="background: #fff3cd; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #ffc107; margin: 2rem 0;">
            <h4>🔧 Información del Procesamiento</h4>
            <p><strong>Estado:</strong> Los servicios no se detectaron en el procesamiento actual.</p>
            <p><strong>Causa probable:</strong> El procesador necesita ser ajustado para detectar correctamente los múltiples servicios en tu archivo.</p>
            <p><strong>Solución:</strong> El sistema está procesando todos los datos como un solo servicio consolidado.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Análisis consolidado cuando no hay servicios separados
        show_consolidated_expert_analysis(analyzer, data)
        
        # ANÁLISIS INTUITIVO POR SERVICIOS (Simulado basado en datos)
        st.markdown("---")
        show_intuitive_service_breakdown(analyzer, data)
        return
    
    # Análisis por servicios (cuando están disponibles)
    all_services = data['servicio'].unique()
    
    # Filtrar servicios reales (eliminar "X servicios")
    real_services = [s for s in all_services if not str(s).endswith('servicios') and str(s) != 'nan']
    
    if len(real_services) <= 1:
        st.markdown("""
        <div style="background: #e3f2fd; padding: 1rem; border-radius: 8px; border-left: 4px solid #2196f3;">
            <strong>ℹ️ Análisis Consolidado:</strong> Mostrando análisis consolidado de todos los servicios.
        </div>
        """, unsafe_allow_html=True)
        show_consolidated_expert_analysis(analyzer, data)
        show_intuitive_service_breakdown(analyzer, data)
        return
    
    services = real_services
    
    # Análisis directo sin mostrar información técnica confusa
    st.markdown("#### 🍽️ Análisis por Servicios de Alimentación")
    
    st.markdown("""
    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 2rem;">
        <strong>📊 Análisis Consolidado:</strong> Productos agrupados por servicio según su consumo histórico
    </div>
    """, unsafe_allow_html=True)
    
    # Selector de servicio
    selected_service = st.selectbox(
        "🔍 Selecciona un servicio para análisis detallado:",
        options=sorted(services),
        index=0
    )
    
    # Análisis del servicio seleccionado
    service_data = data[data['servicio'] == selected_service]
    
    if len(service_data) == 0:
        st.warning(f"No hay datos para el servicio {selected_service}")
        return
    
    # Métricas del servicio
    col1, col2, col3, col4 = st.columns(4)
    
    total_products = len(service_data)
    critical_count = len(service_data[service_data['estado_stock'] == 'CRÍTICO'])
    avg_consumption = service_data['consumo_diario'].mean()
    total_consumption = service_data['consumo_diario'].sum()
    
    with col1:
        st.metric("📦 Productos", total_products)
    
    with col2:
        st.metric("🚨 Críticos", critical_count)
    
    with col3:
        st.metric("⚡ Consumo Promedio", f"{avg_consumption:.1f}")
    
    with col4:
        st.metric("📊 Consumo Total", f"{total_consumption:.1f}")
    
    # Distribución por curva en este servicio
    st.markdown("#### 📊 Distribución por Curva ABC en este Servicio")
    
    curva_dist = service_data['curva'].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if len(curva_dist) > 0:
            fig_curva_service = px.pie(
                values=curva_dist.values,
                names=curva_dist.index,
                title=f"Distribución ABC - {selected_service}",
                color=curva_dist.index,
                color_discrete_map={
                    'A': '#FF6B6B',
                    'B': '#4ECDC4', 
                    'C': '#45B7D1'
                }
            )
            fig_curva_service.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_curva_service, use_container_width=True, key=f"service_curva_{selected_service}")
    
    with col2:
        st.markdown("**Productos por Curva:**")
        for curva, count in curva_dist.items():
            pct = (count / total_products * 100)
            color_icons = {'A': '🔴', 'B': '🟡', 'C': '🟢'}
            icon = color_icons.get(curva, '⚪')
            st.markdown(f"{icon} **Curva {curva}**: {count} productos ({pct:.1f}%)")
    
    # Top productos más consumidos en este servicio
    st.markdown("#### 🏆 Top 10 Productos Más Consumidos")
    
    top_consumed = service_data.nlargest(10, 'consumo_diario')
    
    if len(top_consumed) > 0:
        st.dataframe(
            top_consumed[['codigo', 'descripcion', 'curva', 'consumo_diario', 'estado_stock']],
            width='stretch',
            hide_index=True,
            column_config={
                'codigo': st.column_config.TextColumn('Código', width='small'),
                'descripcion': st.column_config.TextColumn('Descripción', width='large'),
                'curva': st.column_config.TextColumn('Curva', width='small'),
                'consumo_diario': st.column_config.NumberColumn('Consumo Diario', format='%.2f'),
                'estado_stock': st.column_config.TextColumn('Estado', width='small')
            }
        )
    
    # Comparación entre servicios
    st.markdown("#### 📈 Comparación entre Servicios")
    
    services_comparison = data.groupby('servicio').agg({
        'codigo': 'count',
        'consumo_diario': ['sum', 'mean'],
        'estado_stock': lambda x: (x == 'CRÍTICO').sum()
    }).round(2)
    
    services_comparison.columns = ['Total Productos', 'Consumo Total', 'Consumo Promedio', 'Productos Críticos']
    services_comparison = services_comparison.reset_index()
    
    st.dataframe(services_comparison, width='stretch', hide_index=True)

def show_consolidated_expert_analysis(analyzer, data):
    """Análisis EXPERTO consolidado - Enfoque Stock y Criticidad"""
    
    st.markdown("### 🎯 Análisis Experto Consolidado - Stock vs Criticidad")
    
    # 1. ANÁLISIS DE RIESGO OPERACIONAL
    st.markdown("#### 🚨 Análisis de Riesgo Operacional")
    
    # Calcular métricas de riesgo
    total_products = len(data)
    critical_products = len(data[data['estado_stock'] == 'CRÍTICO'])
    low_products = len(data[data['estado_stock'] == 'BAJO'])
    risk_products = critical_products + low_products
    
    # Productos sin stock
    zero_stock = len(data[data['stock'] <= 0])
    
    # Productos de alta rotación en riesgo (Curva A críticos)
    high_rotation_risk = len(data[(data['curva'] == 'A') & (data['estado_stock'].isin(['CRÍTICO', 'BAJO']))])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        risk_pct = (risk_products / total_products * 100) if total_products > 0 else 0
        st.metric(
            "🚨 Riesgo Total", 
            f"{risk_pct:.1f}%",
            delta=f"{risk_products} productos",
            help="Productos críticos + bajos que requieren atención"
        )
    
    with col2:
        st.metric(
            "❌ Sin Stock", 
            zero_stock,
            delta=f"{(zero_stock/total_products*100):.1f}%" if total_products > 0 else "0%",
            help="Productos completamente agotados"
        )
    
    with col3:
        st.metric(
            "🔴 Alta Rotación en Riesgo", 
            high_rotation_risk,
            help="Productos Curva A (alta importancia) con problemas de stock"
        )
    
    with col4:
        avg_coverage = data['dias_cobertura'].mean()
        coverage_status = "🟢" if avg_coverage > 10 else "🟡" if avg_coverage > 5 else "🔴"
        st.metric(
            f"{coverage_status} Cobertura Promedio", 
            f"{avg_coverage:.1f} días",
            help="Días promedio hasta agotamiento según consumo actual"
        )
    
    # 2. MATRIZ DE CRITICIDAD INTELIGENTE
    st.markdown("#### 🎯 Matriz de Criticidad Inteligente")
    
    # Crear matriz de criticidad: Curva ABC vs Estado de Stock
    criticality_matrix = pd.crosstab(data['curva'], data['estado_stock'], margins=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Matriz: Curva ABC vs Estado Stock**")
        st.dataframe(criticality_matrix, width='stretch')
    
    with col2:
        # Análisis de la matriz
        st.markdown("**🧠 Interpretación Experta:**")
        
        curva_a_critical = criticality_matrix.loc['A', 'CRÍTICO'] if 'A' in criticality_matrix.index and 'CRÍTICO' in criticality_matrix.columns else 0
        curva_b_critical = criticality_matrix.loc['B', 'CRÍTICO'] if 'B' in criticality_matrix.index and 'CRÍTICO' in criticality_matrix.columns else 0
        curva_c_critical = criticality_matrix.loc['C', 'CRÍTICO'] if 'C' in criticality_matrix.index and 'CRÍTICO' in criticality_matrix.columns else 0
        
        if curva_a_critical > 0:
            st.markdown(f"🚨 **ALERTA MÁXIMA:** {curva_a_critical} productos Curva A críticos")
        
        if curva_c_critical > curva_a_critical + curva_b_critical:
            st.markdown("✅ **Patrón Normal:** Más criticidad en Curva C (bajo consumo)")
        
        if curva_b_critical > 0:
            st.markdown(f"⚠️ **Atención:** {curva_b_critical} productos Curva B requieren seguimiento")
    
    # 3. TOP PRODUCTOS DE ALTO RIESGO
    st.markdown("#### 🔥 Top 15 Productos de Mayor Riesgo")
    
    # Calcular score de riesgo
    data_risk = data.copy()
    
    # Score de riesgo basado en múltiples factores
    data_risk['risk_score'] = 0
    
    # Factor 1: Días de cobertura (menor = mayor riesgo)
    data_risk['risk_score'] += (10 - data_risk['dias_cobertura']).clip(lower=0) * 2
    
    # Factor 2: Importancia por curva (A=alta, B=media, C=baja)
    curva_weight = {'A': 10, 'B': 5, 'C': 1}
    data_risk['risk_score'] += data_risk['curva'].map(curva_weight).fillna(1)
    
    # Factor 3: Estado crítico
    estado_weight = {'CRÍTICO': 20, 'BAJO': 10, 'NORMAL': 2, 'ALTO': 1}
    data_risk['risk_score'] += data_risk['estado_stock'].map(estado_weight).fillna(1)
    
    # Factor 4: Alto consumo
    data_risk['risk_score'] += (data_risk['consumo_diario'] / data_risk['consumo_diario'].max() * 5).fillna(0)
    
    # Top productos de riesgo
    top_risk = data_risk.nlargest(15, 'risk_score')
    
    st.dataframe(
        top_risk[['codigo', 'descripcion', 'curva', 'stock', 'consumo_diario', 'dias_cobertura', 'estado_stock', 'risk_score']],
        width='stretch',
        hide_index=True,
        column_config={
            'codigo': st.column_config.TextColumn('Código', width='small'),
            'descripcion': st.column_config.TextColumn('Descripción', width='large'),
            'curva': st.column_config.TextColumn('Curva', width='small'),
            'stock': st.column_config.NumberColumn('Stock', format='%.1f'),
            'consumo_diario': st.column_config.NumberColumn('Consumo/día', format='%.2f'),
            'dias_cobertura': st.column_config.NumberColumn('Días Cob.', format='%.1f'),
            'estado_stock': st.column_config.TextColumn('Estado', width='small'),
            'risk_score': st.column_config.NumberColumn('Score Riesgo', format='%.1f', help='Score calculado: días cobertura + curva + estado + consumo')
        }
    )
    
    # 4. RECOMENDACIONES INTELIGENTES
    st.markdown("#### 💡 Recomendaciones Estratégicas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🎯 Acciones Inmediatas:**")
        
        if curva_a_critical > 0:
            st.markdown(f"• 🚨 **URGENTE:** Reponer {curva_a_critical} productos Curva A críticos")
        
        if zero_stock > 0:
            st.markdown(f"• ❌ **CRÍTICO:** {zero_stock} productos sin stock - revisar inmediatamente")
        
        urgent_products = len(data[data['dias_cobertura'] <= 1])
        if urgent_products > 0:
            st.markdown(f"• ⏰ **HOY:** {urgent_products} productos se agotan en ≤1 día")
        
        very_urgent = len(data[data['dias_cobertura'] <= 3])
        if very_urgent > 0:
            st.markdown(f"• 📅 **Esta Semana:** {very_urgent} productos se agotan en ≤3 días")
    
    with col2:
        st.markdown("**📈 Optimizaciones:**")
        
        # Productos con exceso de stock
        excess_stock = len(data[data['dias_cobertura'] > 30])
        if excess_stock > 0:
            st.markdown(f"• 📦 **Revisar:** {excess_stock} productos con +30 días de cobertura")
        
        # Balance por curva
        curva_balance = data.groupby('curva')['dias_cobertura'].mean()
        for curva, avg_days in curva_balance.items():
            target_days = {'A': 7, 'B': 14, 'C': 21}
            target = target_days.get(curva, 14)
            
            if avg_days < target * 0.5:
                st.markdown(f"• 🔴 **Curva {curva}:** Cobertura muy baja ({avg_days:.1f}d vs {target}d objetivo)")
            elif avg_days > target * 2:
                st.markdown(f"• 🟡 **Curva {curva}:** Posible sobrestock ({avg_days:.1f}d vs {target}d objetivo)")
    
    # 5. PROYECCIÓN DE QUIEBRES
    st.markdown("#### 📅 Proyección de Quiebres (Próximos 7 días)")
    
    # Productos que se agotarán en los próximos días
    next_days = [1, 2, 3, 7]
    breakage_forecast = []
    
    for days in next_days:
        products_breaking = len(data[data['dias_cobertura'] <= days])
        breakage_forecast.append({
            'Plazo': f"≤ {days} día{'s' if days > 1 else ''}",
            'Productos': products_breaking,
            'Porcentaje': f"{(products_breaking/total_products*100):.1f}%" if total_products > 0 else "0%"
        })
    
    forecast_df = pd.DataFrame(breakage_forecast)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.dataframe(forecast_df, width='stretch', hide_index=True)
    
    with col2:
        # Gráfico de proyección
        fig_forecast = px.bar(
            forecast_df,
            x='Plazo',
            y='Productos',
            title='Productos que se Agotarán',
            color='Productos',
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig_forecast, use_container_width=True, key="breakage_forecast")

def show_intuitive_service_breakdown(analyzer, data):
    """Análisis intuitivo por servicios con explicaciones claras"""
    
    st.markdown("### 🍽️ Análisis Intuitivo por Tipo de Servicio")
    
    st.markdown("""
    <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;">
        <h4 style="color: #2c3e50;">💡 ¿Cómo funciona este análisis?</h4>
        <p><strong>1. Datos de Consumo:</strong> Tomamos el consumo de cada producto durante 8 días (01/09 - 08/09/2025)</p>
        <p><strong>2. Consumo Diario:</strong> Dividimos el consumo total ÷ 8 días = consumo promedio por día</p>
        <p><strong>3. Stock Actual:</strong> Comparamos con el inventario actual que tienes</p>
        <p><strong>4. Días de Cobertura:</strong> Stock actual ÷ consumo diario = cuántos días te durará</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Análisis por categorías de productos (simulando servicios)
    st.markdown("#### 🔍 Análisis por Categorías de Productos")
    
    # Categorizar productos por tipo
    data_categorized = data.copy()
    
    def categorize_product(description):
        desc = str(description).upper()
        if any(word in desc for word in ['HUEVO', 'PAN', 'LECHE', 'YOGURT', 'MANTEQUILLA', 'CAFE', 'TE']):
            return 'Desayuno'
        elif any(word in desc for word in ['EMPANADA', 'POLLO', 'CARNE', 'ARROZ', 'PAPA', 'VERDURA']):
            return 'Almuerzo/Cena'
        elif any(word in desc for word in ['GALLETA', 'CHOCOLATE', 'GASEOSA', 'AGUA', 'JUGO']):
            return 'Colaciones'
        elif any(word in desc for word in ['POSTRE', 'HELADO', 'FLAN', 'DULCE']):
            return 'Postres'
        else:
            return 'Otros'
    
    data_categorized['categoria_servicio'] = data_categorized['descripcion'].apply(categorize_product)
    
    # Análisis por categoría
    category_analysis = data_categorized.groupby('categoria_servicio').agg({
        'codigo': 'count',
        'stock': 'sum',
        'consumo_diario': 'sum',
        'dias_cobertura': 'mean',
        'estado_stock': lambda x: (x == 'CRÍTICO').sum()
    }).round(2)
    
    category_analysis.columns = ['Total Productos', 'Stock Total', 'Consumo Diario Total', 'Cobertura Promedio', 'Productos Críticos']
    category_analysis = category_analysis.reset_index()
    category_analysis.columns = ['Categoría', 'Total Productos', 'Stock Total', 'Consumo Diario Total', 'Cobertura Promedio', 'Productos Críticos']
    
    st.markdown("**📊 Resumen por Categoría de Productos:**")
    st.dataframe(category_analysis, width='stretch', hide_index=True)
    
    # Explicación de cada categoría
    st.markdown("#### 💡 Explicación de Cálculos por Categoría")
    
    for _, category in category_analysis.iterrows():
        cat_name = category['Categoría']
        total_products = int(category['Total Productos'])
        stock_total = category['Stock Total']
        consumo_total = category['Consumo Diario Total']
        cobertura_prom = category['Cobertura Promedio']
        criticos = int(category['Productos Críticos'])
        
        with st.expander(f"🔍 {cat_name} - {total_products} productos", expanded=(criticos > 0)):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 Datos Actuales:**")
                st.markdown(f"• **Stock Total**: {stock_total:,.1f} unidades")
                st.markdown(f"• **Consumo Diario**: {consumo_total:,.1f} unidades/día")
                st.markdown(f"• **Cobertura Promedio**: {cobertura_prom:.1f} días")
                st.markdown(f"• **Productos Críticos**: {criticos}")
            
            with col2:
                st.markdown("**🧮 Cómo se Calculó:**")
                st.markdown(f"1. **Período**: 8 días (01/09 - 08/09/2025)")
                st.markdown(f"2. **Consumo Diario**: Consumo total ÷ 8 días")
                st.markdown(f"3. **Cobertura**: Stock actual ÷ consumo diario")
                st.markdown(f"4. **Crítico**: Si cobertura < umbral por curva ABC")
            
            # Mostrar productos críticos de esta categoría
            cat_data = data_categorized[data_categorized['categoria_servicio'] == cat_name]
            cat_critical = cat_data[cat_data['estado_stock'] == 'CRÍTICO']
            
            if len(cat_critical) > 0:
                st.markdown(f"**🚨 Productos Críticos en {cat_name}:**")
                st.dataframe(
                    cat_critical[['codigo', 'descripcion', 'stock', 'consumo_diario', 'dias_cobertura']].head(5),
                    width='stretch',
                    hide_index=True,
                    column_config={
                        'codigo': st.column_config.TextColumn('Código', width='small'),
                        'descripcion': st.column_config.TextColumn('Descripción', width='large'),
                        'stock': st.column_config.NumberColumn('Stock Actual', format='%.1f'),
                        'consumo_diario': st.column_config.NumberColumn('Consumo/día', format='%.2f'),
                        'dias_cobertura': st.column_config.NumberColumn('Días Cobertura', format='%.1f')
                    }
                )
                
                # Explicación específica para productos críticos
                st.markdown(f"""
                <div style="background: #fff3cd; padding: 1rem; border-radius: 8px; border-left: 4px solid #ffc107;">
                    <strong>🧠 Interpretación:</strong> Estos productos de {cat_name} se agotarán pronto porque 
                    su consumo diario es alto comparado con el stock actual disponible.
                </div>
                """, unsafe_allow_html=True)
    
    # Gráfico comparativo por categoría
    st.markdown("#### 📈 Comparación Visual por Categorías")
    
    fig_categories = px.scatter(
        category_analysis,
        x='Consumo Diario Total',
        y='Cobertura Promedio', 
        size='Total Productos',
        color='Productos Críticos',
        hover_name='Categoría',
        title='Consumo vs Cobertura por Categoría',
        labels={
            'Consumo Diario Total': 'Consumo Diario Total (unidades/día)',
            'Cobertura Promedio': 'Días de Cobertura Promedio',
            'Productos Críticos': 'Productos Críticos'
        },
        color_continuous_scale='Reds'
    )
    
    st.plotly_chart(fig_categories, use_container_width=True, key="categories_analysis")
    
    # Explicación del gráfico
    st.markdown("""
    <div style="background: #e8f5e8; padding: 1rem; border-radius: 8px; border-left: 4px solid #28a745;">
        <strong>📊 Cómo leer el gráfico:</strong><br>
        • <strong>Eje X (Consumo Diario):</strong> Cuánto se consume por día de esa categoría<br>
        • <strong>Eje Y (Cobertura):</strong> Cuántos días dura el stock actual<br>
        • <strong>Tamaño del círculo:</strong> Cantidad de productos en esa categoría<br>
        • <strong>Color rojo:</strong> Más productos críticos en esa categoría
    </div>
    """, unsafe_allow_html=True)

def show_detailed_curva_analysis(analyzer, data, curva):
    """Análisis detallado de una curva específica"""
    
    curva_data = data[data['curva'] == curva]
    
    if len(curva_data) == 0:
        st.warning(f"No hay productos en la Curva {curva}")
        return
    
    # Información contextual
    curva_info = {
        'A': {
            'title': '🔴 Curva A - Productos Estratégicos',
            'description': 'Estos productos representan el 80% de tu consumo. Son críticos para la operación.',
            'color': '#FF6B6B',
            'priority': 'MÁXIMA PRIORIDAD'
        },
        'B': {
            'title': '🟡 Curva B - Productos Importantes', 
            'description': 'Representan el 15% del consumo. Importantes pero con menor rotación que A.',
            'color': '#4ECDC4',
            'priority': 'PRIORIDAD MEDIA'
        },
        'C': {
            'title': '🟢 Curva C - Productos de Bajo Consumo',
            'description': 'Solo el 5% del consumo total. Menor rotación y prioridad.',
            'color': '#45B7D1', 
            'priority': 'MENOR PRIORIDAD'
        }
    }
    
    info = curva_info.get(curva, curva_info['C'])
    
    st.markdown(f"""
    <div style="background: {info['color']}15; padding: 1.5rem; border-radius: 10px; border-left: 4px solid {info['color']}; margin-bottom: 2rem;">
        <h4 style="color: {info['color']}; margin-bottom: 0.5rem;">{info['title']}</h4>
        <p style="color: #2c3e50; margin-bottom: 0.5rem;">{info['description']}</p>
        <strong style="color: {info['color']};">🎯 {info['priority']}</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas de la curva
    col1, col2, col3, col4 = st.columns(4)
    
    total_products = len(curva_data)
    critical_count = len(curva_data[curva_data['estado_stock'] == 'CRÍTICO'])
    avg_consumption = curva_data['consumo_diario'].mean()
    avg_coverage = curva_data['dias_cobertura'].mean()
    
    with col1:
        st.metric("📦 Total Productos", total_products)
    
    with col2:
        st.metric("🚨 Productos Críticos", critical_count, 
                 delta=f"{(critical_count/total_products*100):.1f}%" if total_products > 0 else "0%")
    
    with col3:
        st.metric("⚡ Consumo Diario Promedio", f"{avg_consumption:.1f}")
    
    with col4:
        st.metric("📊 Cobertura Promedio", f"{avg_coverage:.1f} días")
    
    # Estados de stock para esta curva
    st.markdown("#### 📊 Distribución por Estado de Stock")
    
    status_dist = curva_data['estado_stock'].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de estados
        fig_status = px.pie(
            values=status_dist.values,
            names=status_dist.index,
            title=f"Estados de Stock - Curva {curva}",
            color=status_dist.index,
            color_discrete_map={
                'CRÍTICO': '#FF4444',
                'BAJO': '#FF8800', 
                'NORMAL': '#44AA44',
                'ALTO': '#0088FF'
            }
        )
        fig_status.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_status, use_container_width=True, key=f"detailed_status_chart_curva_{curva}")
    
    with col2:
        st.markdown("**Resumen por Estado:**")
        for estado, count in status_dist.items():
            pct = (count / total_products * 100) if total_products > 0 else 0
            color_icons = {
                'CRÍTICO': '🚨',
                'BAJO': '⚠️',
                'NORMAL': '✅', 
                'ALTO': '📈'
            }
            icon = color_icons.get(estado, '⚪')
            st.markdown(f"{icon} **{estado}**: {count} productos ({pct:.1f}%)")
    
    # Productos más críticos de esta curva
    critical_products = curva_data[curva_data['estado_stock'] == 'CRÍTICO'].nsmallest(10, 'dias_cobertura')
    
    if len(critical_products) > 0:
        st.markdown(f"#### 🚨 Productos Críticos en Curva {curva}")
        st.markdown(f"""
        <div style="background: #fff3cd; padding: 1rem; border-radius: 8px; border-left: 4px solid #ffc107; margin-bottom: 1rem;">
            <strong>⚠️ ATENCIÓN:</strong> {len(critical_products)} productos de Curva {curva} requieren reposición inmediata.
            {' Estos son productos estratégicos de alto consumo.' if curva == 'A' else ''}
        </div>
        """, unsafe_allow_html=True)
        
        st.dataframe(
            critical_products[['codigo', 'descripcion', 'stock', 'consumo_diario', 'dias_cobertura']],
            width='stretch',
            hide_index=True,
            column_config={
                'codigo': st.column_config.TextColumn('Código', width='small'),
                'descripcion': st.column_config.TextColumn('Descripción', width='large'),
                'stock': st.column_config.NumberColumn('Stock Actual', format='%.2f'),
                'consumo_diario': st.column_config.NumberColumn('Consumo Diario', format='%.2f'),
                'dias_cobertura': st.column_config.NumberColumn('Días Cobertura', format='%.1f')
            }
        )
    else:
        st.markdown(f"""
        <div style="background: #d1edff; padding: 1rem; border-radius: 8px; border-left: 4px solid #0088ff;">
            <strong>✅ Excelente:</strong> No hay productos críticos en Curva {curva}
        </div>
        """, unsafe_allow_html=True)
    
    # Tabla completa con filtros
    st.markdown(f"#### 📋 Todos los Productos - Curva {curva}")
    
    # Filtros
    col1, col2 = st.columns(2)
    
    with col1:
        status_filter = st.multiselect(
            "Filtrar por Estado:",
            options=curva_data['estado_stock'].unique(),
            default=curva_data['estado_stock'].unique(),
            key=f"status_filter_{curva}"
        )
    
    with col2:
        sort_options = {
            'Días de Cobertura (Menor a Mayor)': ('dias_cobertura', True),
            'Días de Cobertura (Mayor a Menor)': ('dias_cobertura', False), 
            'Consumo Diario (Mayor a Menor)': ('consumo_diario', False),
            'Stock Actual (Mayor a Menor)': ('stock', False)
        }
        sort_choice = st.selectbox(
            "Ordenar por:",
            options=list(sort_options.keys()),
            index=0,
            key=f"sort_choice_{curva}"
        )
    
    # Aplicar filtros
    filtered_data = curva_data[curva_data['estado_stock'].isin(status_filter)]
    
    # Aplicar ordenamiento
    sort_col, ascending = sort_options[sort_choice]
    filtered_data = filtered_data.sort_values(sort_col, ascending=ascending)
    
    if len(filtered_data) > 0:
        st.markdown(f"**Mostrando {len(filtered_data)} de {len(curva_data)} productos**")
        
        st.dataframe(
            filtered_data[['codigo', 'descripcion', 'stock', 'consumo_diario', 'dias_cobertura', 'estado_stock']],
            width='stretch',
            hide_index=True,
            column_config={
                'codigo': st.column_config.TextColumn('Código', width='small'),
                'descripcion': st.column_config.TextColumn('Descripción', width='large'),
                'stock': st.column_config.NumberColumn('Stock', format='%.2f'),
                'consumo_diario': st.column_config.NumberColumn('Consumo Diario', format='%.2f'),
                'dias_cobertura': st.column_config.NumberColumn('Días Cobertura', format='%.1f'),
                'estado_stock': st.column_config.TextColumn('Estado', width='small')
            }
        )
    else:
        st.warning("No hay productos que coincidan con los filtros seleccionados")

def show_advanced_analysis_tab(analyzer):
    """Tab de análisis detallado completamente rediseñado"""
    
    data = analyzer.data
    
    st.markdown("### 🔍 Análisis Detallado por Segmentos")
    
    # Tabs secundarias para diferentes vistas
    sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs([
        "📊 Por Curva ABC", 
        "⚡ Por Estado", 
        "🏷️ Por Familia",
        "📈 Tendencias"
    ])
    
    with sub_tab1:
        show_curva_analysis(analyzer, data)
    
    with sub_tab2:
        show_status_analysis(analyzer, data)
    
    with sub_tab3:
        show_family_analysis(analyzer, data)
    
    with sub_tab4:
        show_trends_analysis(analyzer, data)

def show_curva_analysis(analyzer, data):
    """Análisis por curva ABC mejorado"""
    
    st.markdown("#### 🎯 Análisis por Importancia Estratégica (Curva ABC)")
    
    # Mostrar todas las curvas disponibles
    available_curvas = sorted(data['curva'].unique())
    
    if len(available_curvas) == 0:
        st.warning("No hay datos de curva ABC disponibles")
        return
    
    # Selector mejorado
    col1, col2 = st.columns([1, 3])
    
    with col1:
        curva_selected = st.selectbox(
            "🔍 Selecciona Curva:",
            options=available_curvas,
            index=0,
            help="A: Productos críticos (80% valor), B: Importantes (15% valor), C: Normales (5% valor)"
        )
    
    with col2:
        # Explicación de cada curva
        curva_info = {
            'A': "🔴 **Productos Estratégicos** - Alta rotación, máxima prioridad",
            'B': "🟡 **Productos Importantes** - Rotación media, prioridad moderada", 
            'C': "🟢 **Productos Normales** - Baja rotación, menor prioridad"
        }
        st.markdown(curva_info.get(curva_selected, "Información no disponible"))
    
    # Obtener datos de la curva seleccionada
    curva_data = analyzer.get_products_by_curva(curva_selected)
    
    if len(curva_data) == 0:
        st.warning(f"No hay productos en la Curva {curva_selected}")
        return
    
    # Métricas de la curva seleccionada
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📦 Total Productos", 
            len(curva_data),
            help=f"Productos clasificados en Curva {curva_selected}"
        )
    
    with col2:
        critical_count = len(curva_data[curva_data['estado_stock'] == 'CRÍTICO'])
        critical_pct = (critical_count / len(curva_data) * 100) if len(curva_data) > 0 else 0
        st.metric(
            "🚨 Críticos", 
            critical_count,
            delta=f"{critical_pct:.1f}%",
            help="Productos que requieren reposición inmediata"
        )
    
    with col3:
        avg_coverage = curva_data['dias_cobertura'].mean()
        st.metric(
            "📊 Cobertura Promedio", 
            f"{avg_coverage:.1f} días",
            help="Días promedio hasta agotamiento"
        )
    
    with col4:
        total_stock_value = (curva_data['stock'] * curva_data.get('precio', 0)).sum()
        st.metric(
            "💰 Valor en Stock", 
            f"${total_stock_value:,.0f}",
            help="Valor total del inventario en esta curva"
        )
    
    # Distribución por estado
    st.markdown("#### 📊 Distribución por Estado de Stock")
    
    status_dist = curva_data['estado_stock'].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de distribución
        fig_pie = px.pie(
            values=status_dist.values,
            names=status_dist.index,
            title=f"Estados de Stock - Curva {curva_selected}",
            color=status_dist.index,
            color_discrete_map={
                'CRÍTICO': '#FF4444',
                'BAJO': '#FF8800',
                'NORMAL': '#44AA44',
                'ALTO': '#0088FF'
            }
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True, key=f"pie_chart_curva_{curva_selected}")
    
    with col2:
        # Tabla resumen por estado
        st.markdown("**Resumen por Estado:**")
        for estado, count in status_dist.items():
            pct = (count / len(curva_data) * 100)
            color_map = {
                'CRÍTICO': '🔴',
                'BAJO': '🟡', 
                'NORMAL': '🟢',
                'ALTO': '🔵'
            }
            icon = color_map.get(estado, '⚪')
            st.markdown(f"{icon} **{estado}**: {count} productos ({pct:.1f}%)")
    
    # Tabla detallada con filtros
    st.markdown("#### 📋 Productos Detallados")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.multiselect(
            "Filtrar por Estado:",
            options=curva_data['estado_stock'].unique(),
            default=curva_data['estado_stock'].unique()
        )
    
    with col2:
        min_coverage = st.number_input(
            "Días mínimos de cobertura:",
            min_value=0,
            max_value=int(curva_data['dias_cobertura'].max()),
            value=0
        )
    
    with col3:
        max_coverage = st.number_input(
            "Días máximos de cobertura:",
            min_value=0,
            max_value=int(curva_data['dias_cobertura'].max()),
            value=int(curva_data['dias_cobertura'].max())
        )
    
    # Aplicar filtros
    filtered_data = curva_data[
        (curva_data['estado_stock'].isin(status_filter)) &
        (curva_data['dias_cobertura'] >= min_coverage) &
        (curva_data['dias_cobertura'] <= max_coverage)
    ]
    
    # Mostrar datos filtrados
    if len(filtered_data) > 0:
        st.markdown(f"**Mostrando {len(filtered_data)} de {len(curva_data)} productos**")
        
        # Ordenar por criticidad
        display_data = filtered_data.sort_values(['estado_stock', 'dias_cobertura'])
        
        st.dataframe(
            display_data[['codigo', 'descripcion', 'stock', 'consumo_diario', 'dias_cobertura', 'estado_stock']],
            width='stretch',
            hide_index=True,
            column_config={
                'codigo': st.column_config.TextColumn('Código', width='small'),
                'descripcion': st.column_config.TextColumn('Descripción', width='large'),
                'stock': st.column_config.NumberColumn('Stock', format='%.2f'),
                'consumo_diario': st.column_config.NumberColumn('Consumo Diario', format='%.2f'),
                'dias_cobertura': st.column_config.NumberColumn('Días Cobertura', format='%.1f'),
                'estado_stock': st.column_config.TextColumn('Estado', width='small')
            }
        )
    else:
        st.warning("No hay productos que coincidan con los filtros seleccionados")

def show_status_analysis(analyzer, data):
    """Análisis por estado de stock"""
    st.markdown("#### ⚡ Análisis por Estado de Stock")
    
    status_counts = data['estado_stock'].value_counts()
    
    for status in ['CRÍTICO', 'BAJO', 'NORMAL', 'ALTO']:
        if status in status_counts.index:
            status_data = data[data['estado_stock'] == status]
            count = len(status_data)
            pct = (count / len(data) * 100)
            
            with st.expander(f"{status} - {count} productos ({pct:.1f}%)", expanded=(status=='CRÍTICO')):
                if len(status_data) > 0:
                    avg_coverage = status_data['dias_cobertura'].mean()
                    st.metric(f"Cobertura promedio - {status}", f"{avg_coverage:.1f} días")
                    
                    st.dataframe(
                        status_data[['codigo', 'descripcion', 'curva', 'dias_cobertura']].head(10),
                        width='stretch',
                        hide_index=True
                    )

def show_family_analysis(analyzer, data):
    """Análisis por familia de productos"""
    st.markdown("#### 🏷️ Análisis por Familia de Productos")
    
    if 'familia' not in data.columns:
        st.warning("No hay información de familias de productos disponible")
        return
    
    family_analysis = data.groupby('familia').agg({
        'codigo': 'count',
        'dias_cobertura': 'mean',
        'estado_stock': lambda x: (x == 'CRÍTICO').sum()
    }).rename(columns={
        'codigo': 'total_productos',
        'dias_cobertura': 'cobertura_promedio',
        'estado_stock': 'productos_criticos'
    })
    
    family_analysis['pct_criticos'] = (family_analysis['productos_criticos'] / family_analysis['total_productos'] * 100)
    family_analysis = family_analysis.sort_values('pct_criticos', ascending=False)
    
    st.dataframe(family_analysis, width='stretch')

def show_trends_analysis(analyzer, data):
    """Análisis de tendencias"""
    st.markdown("#### 📈 Análisis de Tendencias y Proyecciones")
    
    # Distribución de días de cobertura
    fig_hist = px.histogram(
        data, 
        x='dias_cobertura', 
        nbins=20,
        title="Distribución de Días de Cobertura",
        labels={'dias_cobertura': 'Días de Cobertura', 'count': 'Cantidad de Productos'}
    )
    st.plotly_chart(fig_hist, use_container_width=True, key="coverage_histogram")
    
    # Análisis por rangos de cobertura
    coverage_ranges = pd.cut(data['dias_cobertura'], 
                           bins=[0, 3, 7, 15, 30, float('inf')], 
                           labels=['0-3 días', '4-7 días', '8-15 días', '16-30 días', '30+ días'])
    
    range_analysis = coverage_ranges.value_counts().sort_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Distribución por Rangos de Cobertura:**")
        for range_name, count in range_analysis.items():
            pct = (count / len(data) * 100)
            st.markdown(f"• **{range_name}**: {count} productos ({pct:.1f}%)")
    
    with col2:
        fig_bar = px.bar(
            x=range_analysis.index,
            y=range_analysis.values,
            title="Productos por Rango de Cobertura",
            labels={'x': 'Rango de Días', 'y': 'Cantidad de Productos'}
        )
        st.plotly_chart(fig_bar, use_container_width=True, key="coverage_ranges_bar")

def show_export_tab(analyzer, data):
    """Tab de exportación"""
    
    st.subheader("📤 Descargar Reportes Profesionales")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📊 Reporte Excel Ejecutivo**
        
        Incluye:
        - Resumen ejecutivo con KPIs
        - Dashboard de productos críticos  
        - Análisis completo por producto
        - Reporte de reposición sugerida
        - Gráficos y métricas por curva ABC
        """)
        
        if st.button("📥 Generar Reporte Excel", key="generate_excel"):
            with st.spinner("Generando reporte profesional..."):
                try:
                    exporter = ExcelExporter()
                    analysis_summary = analyzer.get_summary_metrics()
                    
                    excel_file = exporter.create_professional_report(data, analysis_summary, st.session_state.processor)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"reporte_stock_critico_{timestamp}.xlsx"
                    
                    st.download_button(
                        label="📥 Descargar Reporte Completo",
                        data=excel_file,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
                    st.success("✅ Reporte generado exitosamente!")
                    
                except Exception as e:
                    st.error(f"Error generando reporte: {str(e)}")
    
    with col2:
        st.markdown("**📋 Exportaciones Rápidas**")
        
        # Export productos críticos
        critical_products = analyzer.get_critical_products()
        if len(critical_products) > 0:
            csv_critical = critical_products.to_csv(index=False)
            st.download_button(
                label="📥 Productos Críticos (CSV)",
                data=csv_critical,
                file_name="productos_criticos.csv",
                mime="text/csv"
            )
        
        # Export datos completos
        csv_complete = data.to_csv(index=False)
        st.download_button(
            label="📥 Análisis Completo (CSV)",
            data=csv_complete,
            file_name="analisis_completo.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()