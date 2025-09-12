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
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard Principal", 
        "🚨 Stock Crítico", 
        "📈 Análisis Detallado",
        "📤 Exportar Reportes"
    ])
    
    with tab1:
        show_dashboard_tab(analyzer)
    
    with tab2:
        show_critical_tab(analyzer)
    
    with tab3:
        show_detailed_tab(analyzer)
    
    with tab4:
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
    """Muestra KPIs principales en cards atractivas"""
    
    metrics = analyzer.get_summary_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{metrics['total_productos']}</div>
            <div class="metric-label">Total Productos</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-container" style="border-top-color: #ff6b6b;">
            <div class="metric-value" style="color: #ff6b6b;">{metrics['productos_criticos']}</div>
            <div class="metric-label">Stock Crítico</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-container" style="border-top-color: #ffa726;">
            <div class="metric-value" style="color: #ffa726;">{metrics['productos_bajo']}</div>
            <div class="metric-label">Stock Bajo</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-container" style="border-top-color: #66bb6a;">
            <div class="metric-value" style="color: #66bb6a; font-size: 1.8rem;">{metrics['porcentaje_critico']}</div>
            <div class="metric-label">% Críticos</div>
        </div>
        """, unsafe_allow_html=True)

def show_dashboard_tab(analyzer):
    """Tab del dashboard principal"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_status = analyzer.create_status_distribution_chart()
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        fig_curva = analyzer.create_coverage_by_curva_chart()
        st.plotly_chart(fig_curva, use_container_width=True)
    
    # Gráfico de productos críticos
    fig_critical = analyzer.create_critical_products_chart()
    st.plotly_chart(fig_critical, use_container_width=True)

def show_critical_tab(analyzer):
    """Tab de productos críticos"""
    
    critical_products = analyzer.get_critical_products()
    
    if len(critical_products) == 0:
        st.markdown("""
        <div class="alert-success">
            🎉 <strong>¡Excelente!</strong> No hay productos en estado crítico en este momento.
        </div>
        """, unsafe_allow_html=True)
        return
    
    st.markdown(f"""
    <div class="alert-warning">
        ⚠️ <strong>Atención:</strong> {len(critical_products)} productos requieren reposición inmediata
    </div>
    """, unsafe_allow_html=True)
    
    # Tabla de productos críticos
    display_critical = critical_products.copy()
    display_critical = display_critical.round(2)
    
    st.dataframe(
        display_critical[['codigo', 'descripcion', 'curva', 'stock', 'consumo_diario', 'dias_cobertura', 'estado_stock']],
        use_container_width=True,
        hide_index=True
    )

def show_detailed_tab(analyzer):
    """Tab de análisis detallado"""
    
    data = analyzer.data
    
    # Análisis por curva
    st.subheader("📈 Análisis por Curva ABC")
    
    curva_selected = st.selectbox(
        "Selecciona una curva:",
        options=['A', 'B', 'C'],
        index=0
    )
    
    curva_data = analyzer.get_products_by_curva(curva_selected)
    
    if len(curva_data) > 0:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Productos", len(curva_data))
        
        with col2:
            critical_count = len(curva_data[curva_data['estado_stock'] == 'CRÍTICO'])
            st.metric("Productos Críticos", critical_count)
        
        with col3:
            avg_coverage = curva_data['dias_cobertura'].mean()
            st.metric("Cobertura Promedio", f"{avg_coverage:.1f} días")
        
        st.dataframe(curva_data, use_container_width=True, hide_index=True)

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
                    
                    excel_file = exporter.create_professional_report(data, analysis_summary)
                    
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