import pandas as pd
import streamlit as st
from io import BytesIO
import xlsxwriter
from datetime import datetime
from typing import Dict, List
import base64

class ExcelExporter:
    """Clase para exportar reportes a Excel con formato profesional"""
    
    def __init__(self):
        self.workbook = None
        self.formats = {}
    
    def create_professional_report(self, data: pd.DataFrame, analysis_data: Dict) -> BytesIO:
        """Crea reporte profesional en Excel"""
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            self.workbook = writer.book
            self._create_formats()
            
            # Hoja 1: Resumen Ejecutivo
            self._create_executive_summary(writer, analysis_data)
            
            # Hoja 2: Productos Críticos
            critical_products = data[data['estado_stock'] == 'CRÍTICO']
            self._create_critical_products_sheet(writer, critical_products)
            
            # Hoja 3: Análisis Completo
            self._create_complete_analysis_sheet(writer, data)
            
            # Hoja 4: Reporte de Reposición
            replenishment = self._generate_replenishment_data(data)
            self._create_replenishment_sheet(writer, replenishment)
            
            # Hoja 5: Métricas por Curva
            self._create_curva_metrics_sheet(writer, data)
        
        output.seek(0)
        return output
    
    def _create_formats(self):
        """Crea formatos para Excel"""
        self.formats = {
            'title': self.workbook.add_format({
                'bold': True, 'font_size': 16, 'align': 'center',
                'valign': 'vcenter', 'bg_color': '#366092', 'font_color': 'white'
            }),
            'header': self.workbook.add_format({
                'bold': True, 'bg_color': '#D7E4BC', 'border': 1,
                'align': 'center', 'valign': 'vcenter'
            }),
            'critical': self.workbook.add_format({
                'bg_color': '#FFC7CE', 'font_color': '#9C0006', 'border': 1
            }),
            'warning': self.workbook.add_format({
                'bg_color': '#FFEB9C', 'font_color': '#9C6500', 'border': 1
            }),
            'normal': self.workbook.add_format({
                'bg_color': '#C6EFCE', 'font_color': '#006100', 'border': 1
            }),
            'number': self.workbook.add_format({
                'num_format': '#,##0.00', 'border': 1
            }),
            'percent': self.workbook.add_format({
                'num_format': '0.0%', 'border': 1
            }),
            'date': self.workbook.add_format({
                'num_format': 'dd/mm/yyyy', 'border': 1
            }),
            'border': self.workbook.add_format({'border': 1})
        }
    
    def _create_executive_summary(self, writer, analysis_data):
        """Crea hoja de resumen ejecutivo"""
        ws = writer.book.add_worksheet('Resumen Ejecutivo')
        
        # Título principal
        ws.merge_range('A1:F1', 'ANÁLISIS DE STOCK CRÍTICO - RESUMEN EJECUTIVO', self.formats['title'])
        ws.merge_range('A2:F2', f'Generado el: {datetime.now().strftime("%d/%m/%Y %H:%M")}', self.formats['border'])
        
        # KPIs principales
        ws.write('A4', 'INDICADORES CLAVE', self.formats['header'])
        
        kpis = [
            ('Total de Productos Analizados', analysis_data.get('total_productos', 0)),
            ('Productos en Estado Crítico', analysis_data.get('productos_criticos', 0)),
            ('Productos en Estado Bajo', analysis_data.get('productos_bajo', 0)),
            ('% Productos Críticos', analysis_data.get('porcentaje_critico', '0%')),
            ('Valor Total Inventario', analysis_data.get('valor_inventario', '$0'))
        ]
        
        for i, (metric, value) in enumerate(kpis, 5):
            ws.write(f'A{i}', metric, self.formats['border'])
            ws.write(f'B{i}', value, self.formats['border'])
        
        # Distribución por Curva ABC
        ws.write('D4', 'DISTRIBUCIÓN POR CURVA ABC', self.formats['header'])
        curva_data = [
            ('Curva A (Críticos)', analysis_data.get('productos_curva_a', 0)),
            ('Curva B (Importantes)', analysis_data.get('productos_curva_b', 0)),
            ('Curva C (Normales)', analysis_data.get('productos_curva_c', 0))
        ]
        
        for i, (curva, count) in enumerate(curva_data, 5):
            ws.write(f'D{i}', curva, self.formats['border'])
            ws.write(f'E{i}', count, self.formats['border'])
        
        # Ajustar anchos de columna
        ws.set_column('A:A', 25)
        ws.set_column('B:B', 15)
        ws.set_column('D:D', 25)
        ws.set_column('E:E', 15)
    
    def _create_critical_products_sheet(self, writer, critical_products):
        """Crea hoja de productos críticos"""
        if len(critical_products) == 0:
            ws = writer.book.add_worksheet('Productos Críticos')
            ws.write('A1', 'No hay productos en estado crítico', self.formats['title'])
            return
        
        critical_products.to_excel(
            writer, sheet_name='Productos Críticos', index=False, startrow=1
        )
        
        ws = writer.sheets['Productos Críticos']
        
        # Título
        ws.merge_range('A1:H1', 'PRODUCTOS EN ESTADO CRÍTICO', self.formats['title'])
        
        # Formatear headers
        for col_num, value in enumerate(critical_products.columns.values):
            ws.write(1, col_num, value, self.formats['header'])
        
        # Formatear datos con colores según criticidad
        for row_num in range(len(critical_products)):
            for col_num in range(len(critical_products.columns)):
                cell_format = self.formats['critical'] if row_num < 5 else self.formats['warning']
                ws.write(row_num + 2, col_num, critical_products.iloc[row_num, col_num], cell_format)
        
        # Ajustar anchos
        ws.set_column('A:A', 10)  # Código
        ws.set_column('B:B', 40)  # Descripción
        ws.set_column('C:H', 12)  # Resto de columnas
    
    def _create_complete_analysis_sheet(self, writer, data):
        """Crea hoja de análisis completo"""
        data.to_excel(writer, sheet_name='Análisis Completo', index=False, startrow=1)
        
        ws = writer.sheets['Análisis Completo']
        ws.merge_range('A1:J1', 'ANÁLISIS COMPLETO DE INVENTARIO', self.formats['title'])
        
        # Headers
        for col_num, value in enumerate(data.columns.values):
            ws.write(1, col_num, value, self.formats['header'])
        
        # Formatear según estado
        for row_num in range(len(data)):
            status = data.iloc[row_num]['estado_stock']
            format_map = {
                'CRÍTICO': self.formats['critical'],
                'BAJO': self.formats['warning'],
                'NORMAL': self.formats['normal'],
                'ALTO': self.formats['border']
            }
            row_format = format_map.get(status, self.formats['border'])
            
            for col_num in range(len(data.columns)):
                ws.write(row_num + 2, col_num, data.iloc[row_num, col_num], row_format)
    
    def _create_replenishment_sheet(self, writer, replenishment_data):
        """Crea hoja de reporte de reposición"""
        replenishment_data.to_excel(
            writer, sheet_name='Reporte Reposición', index=False, startrow=1
        )
        
        ws = writer.sheets['Reporte Reposición']
        ws.merge_range('A1:H1', 'REPORTE DE REPOSICIÓN SUGERIDA', self.formats['title'])
        
        # Headers y formato
        for col_num, value in enumerate(replenishment_data.columns.values):
            ws.write(1, col_num, value, self.formats['header'])
        
        # Formatear según prioridad
        for row_num in range(len(replenishment_data)):
            priority = replenishment_data.iloc[row_num]['Prioridad']
            row_format = self.formats['critical'] if priority == 1 else self.formats['warning']
            
            for col_num in range(len(replenishment_data.columns)):
                ws.write(row_num + 2, col_num, replenishment_data.iloc[row_num, col_num], row_format)
    
    def _create_curva_metrics_sheet(self, writer, data):
        """Crea hoja de métricas por curva"""
        ws = writer.book.add_worksheet('Métricas por Curva')
        
        ws.merge_range('A1:F1', 'MÉTRICAS POR CURVA ABC', self.formats['title'])
        
        # Calcular métricas por curva
        curva_stats = data.groupby('curva').agg({
            'codigo': 'count',
            'stock': ['sum', 'mean'],
            'consumo_diario': ['sum', 'mean'],
            'dias_cobertura': ['mean', 'min', 'max']
        }).round(2)
        
        # Aplanar columnas multi-nivel
        curva_stats.columns = ['_'.join(col).strip() for col in curva_stats.columns.values]
        curva_stats = curva_stats.reset_index()
        
        # Escribir datos
        curva_stats.to_excel(writer, sheet_name='Métricas por Curva', index=False, startrow=2)
        
        # Formatear
        for col_num, value in enumerate(curva_stats.columns.values):
            ws.write(2, col_num, value, self.formats['header'])
    
    def _generate_replenishment_data(self, data):
        """Genera datos de reposición"""
        needs_replenishment = data[data['estado_stock'].isin(['CRÍTICO', 'BAJO'])].copy()
        
        if len(needs_replenishment) == 0:
            return pd.DataFrame(columns=['Codigo', 'Descripcion', 'Estado', 'Cantidad Sugerida'])
        
        # Calcular cantidad sugerida
        target_days = {'A': 30, 'B': 20, 'C': 15}
        needs_replenishment['cantidad_sugerida'] = needs_replenishment.apply(
            lambda row: max(0, row['consumo_diario'] * target_days.get(row['curva'], 20) - row['stock']),
            axis=1
        )
        
        # Prioridad
        needs_replenishment['prioridad'] = needs_replenishment['estado_stock'].map({
            'CRÍTICO': 1, 'BAJO': 2
        })
        
        return needs_replenishment[[
            'codigo', 'descripcion', 'estado_stock', 'stock', 'consumo_diario',
            'dias_cobertura', 'cantidad_sugerida', 'prioridad'
        ]].rename(columns={
            'codigo': 'Codigo',
            'descripcion': 'Descripcion', 
            'estado_stock': 'Estado',
            'stock': 'Stock Actual',
            'consumo_diario': 'Consumo Diario',
            'dias_cobertura': 'Dias Cobertura',
            'cantidad_sugerida': 'Cantidad Sugerida',
            'prioridad': 'Prioridad'
        }).sort_values(['Prioridad', 'Dias Cobertura'])

def create_download_link(file_data: BytesIO, filename: str, link_text: str) -> str:
    """Crea enlace de descarga para archivo"""
    b64 = base64.b64encode(file_data.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">{link_text}</a>'
    return href

def format_number(number, decimals=0):
    """Formatea números con separadores de miles"""
    if pd.isna(number):
        return "N/A"
    
    if decimals == 0:
        return f"{number:,.0f}"
    else:
        return f"{number:,.{decimals}f}"

def format_currency(amount):
    """Formatea valores como moneda"""
    if pd.isna(amount):
        return "N/A"
    return f"${amount:,.0f}"

def get_status_color(status):
    """Retorna color según estado de stock"""
    colors = {
        'CRÍTICO': '#FF4444',
        'BAJO': '#FF8800', 
        'NORMAL': '#44AA44',
        'ALTO': '#0088FF'
    }
    return colors.get(status, '#CCCCCC')

def get_curva_color(curva):
    """Retorna color según curva ABC"""
    colors = {
        'A': '#FF6B6B',
        'B': '#4ECDC4', 
        'C': '#45B7D1'
    }
    return colors.get(curva, '#CCCCCC')

def validate_file_format(file, expected_extensions=['.xlsx', '.xls']):
    """Valida formato de archivo subido"""
    if file is None:
        return False, "No se ha seleccionado ningún archivo"
    
    file_extension = '.' + file.name.split('.')[-1].lower()
    
    if file_extension not in expected_extensions:
        return False, f"Formato no válido. Se esperaba: {', '.join(expected_extensions)}"
    
    return True, "Archivo válido"

def safe_divide(numerator, denominator, default=0):
    """División segura que evita errores por división por cero"""
    try:
        if denominator == 0 or pd.isna(denominator):
            return default
        return numerator / denominator
    except:
        return default

class AlertManager:
    """Gestiona alertas y notificaciones del sistema"""
    
    @staticmethod
    def check_critical_alerts(data: pd.DataFrame) -> List[Dict]:
        """Verifica alertas críticas en el inventario"""
        alerts = []
        
        # Productos sin stock
        no_stock = data[data['stock'] <= 0]
        if len(no_stock) > 0:
            alerts.append({
                'type': 'error',
                'title': 'Productos sin Stock',
                'message': f'{len(no_stock)} productos están sin stock',
                'count': len(no_stock)
            })
        
        # Productos críticos
        critical = data[data['estado_stock'] == 'CRÍTICO']
        if len(critical) > 0:
            alerts.append({
                'type': 'warning',
                'title': 'Stock Crítico',
                'message': f'{len(critical)} productos en estado crítico',
                'count': len(critical)
            })
        
        # Productos Curva A con problemas
        curva_a_problems = data[
            (data['curva'] == 'A') & 
            (data['estado_stock'].isin(['CRÍTICO', 'BAJO']))
        ]
        if len(curva_a_problems) > 0:
            alerts.append({
                'type': 'warning',
                'title': 'Productos Críticos Curva A',
                'message': f'{len(curva_a_problems)} productos de alta importancia con problemas de stock',
                'count': len(curva_a_problems)
            })
        
        return alerts
    
    @staticmethod
    def display_alerts(alerts: List[Dict]):
        """Muestra alertas en Streamlit"""
        for alert in alerts:
            if alert['type'] == 'error':
                st.error(f"🚨 {alert['title']}: {alert['message']}")
            elif alert['type'] == 'warning':
                st.warning(f"⚠️ {alert['title']}: {alert['message']}")
            else:
                st.info(f"ℹ️ {alert['title']}: {alert['message']}")

def calculate_days_between_dates(start_date: str, end_date: str) -> int:
    """Calcula días entre dos fechas en formato DD/MM/YYYY"""
    try:
        start = datetime.strptime(start_date, '%d/%m/%Y')
        end = datetime.strptime(end_date, '%d/%m/%Y')
        return (end - start).days + 1  # +1 para incluir ambos días
    except:
        return 8  # Default 8 días como en el ejemplo