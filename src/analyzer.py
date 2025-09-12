import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class StockAnalyzer:
    def __init__(self, consolidated_data: pd.DataFrame):
        self.data = consolidated_data
        self.kpis = self._calculate_kpis()
    
    def _calculate_kpis(self) -> Dict:
        """Calcula KPIs principales del inventario"""
        total_products = len(self.data)
        critical_products = len(self.data[self.data['estado_stock'] == 'CRÍTICO'])
        low_products = len(self.data[self.data['estado_stock'] == 'BAJO'])
        
        # Stock total valorizado
        total_stock_value = (self.data['stock'] * self.data.get('precio', 0)).sum()
        
        # Productos por curva
        curva_distribution = self.data['curva'].value_counts().to_dict()
        
        # Promedio días de cobertura por curva
        avg_coverage = self.data.groupby('curva')['dias_cobertura'].mean().to_dict()
        
        return {
            'total_products': total_products,
            'critical_products': critical_products,
            'low_products': low_products,
            'critical_percentage': (critical_products / total_products * 100) if total_products > 0 else 0,
            'total_stock_value': total_stock_value,
            'curva_distribution': curva_distribution,
            'avg_coverage_by_curva': avg_coverage
        }
    
    def get_critical_products(self) -> pd.DataFrame:
        """Obtiene productos en estado crítico ordenados por días de cobertura"""
        critical = self.data[self.data['estado_stock'] == 'CRÍTICO'].copy()
        return critical.sort_values('dias_cobertura').reset_index(drop=True)
    
    def get_products_by_status(self, status: str) -> pd.DataFrame:
        """Obtiene productos por estado específico"""
        return self.data[self.data['estado_stock'] == status].copy()
    
    def get_products_by_curva(self, curva: str) -> pd.DataFrame:
        """Obtiene productos por curva ABC"""
        return self.data[self.data['curva'] == curva].copy()
    
    def create_status_distribution_chart(self) -> go.Figure:
        """Crea gráfico de distribución de estados de stock"""
        status_counts = self.data['estado_stock'].value_counts()
        
        colors = {
            'CRÍTICO': '#FF4444',
            'BAJO': '#FF8800',
            'NORMAL': '#44AA44',
            'ALTO': '#0088FF'
        }
        
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Distribución de Estados de Stock",
            color=status_counts.index,
            color_discrete_map=colors
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            font_size=12,
            title_font_size=16,
            showlegend=True
        )
        
        return fig
    
    def create_coverage_by_curva_chart(self) -> go.Figure:
        """Crea gráfico de cobertura promedio por curva ABC"""
        coverage_data = self.data.groupby('curva')['dias_cobertura'].agg(['mean', 'median']).reset_index()
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=coverage_data['curva'],
            y=coverage_data['mean'],
            name='Promedio',
            marker_color='lightblue',
            text=coverage_data['mean'].round(1),
            textposition='auto'
        ))
        
        fig.add_trace(go.Bar(
            x=coverage_data['curva'],
            y=coverage_data['median'],
            name='Mediana',
            marker_color='darkblue',
            text=coverage_data['median'].round(1),
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Días de Cobertura Promedio por Curva ABC",
            xaxis_title="Curva ABC",
            yaxis_title="Días de Cobertura",
            barmode='group',
            font_size=12
        )
        
        return fig
    
    def create_critical_products_chart(self) -> go.Figure:
        """Crea gráfico de productos más críticos"""
        critical = self.get_critical_products().head(15)
        
        if len(critical) == 0:
            # Crear gráfico vacío si no hay productos críticos
            fig = go.Figure()
            fig.add_annotation(
                text="No hay productos en estado crítico",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font_size=16
            )
            fig.update_layout(title="Top 15 Productos Más Críticos")
            return fig
        
        # Truncar descripciones largas
        critical['descripcion_short'] = critical['descripcion'].apply(
            lambda x: x[:30] + '...' if len(str(x)) > 30 else str(x)
        )
        
        fig = go.Figure(go.Bar(
            y=critical['descripcion_short'],
            x=critical['dias_cobertura'],
            orientation='h',
            marker_color='red',
            text=critical['dias_cobertura'].round(1),
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Top 15 Productos Más Críticos",
            xaxis_title="Días de Cobertura",
            yaxis_title="Producto",
            height=600,
            font_size=10
        )
        
        return fig
    
    def create_family_analysis_chart(self) -> go.Figure:
        """Crea análisis por familia de productos"""
        if 'familia' not in self.data.columns:
            return self._create_empty_chart("Análisis por familia no disponible")
        
        family_analysis = self.data.groupby(['familia', 'estado_stock']).size().unstack(fill_value=0)
        
        fig = go.Figure()
        
        colors = {'CRÍTICO': '#FF4444', 'BAJO': '#FF8800', 'NORMAL': '#44AA44', 'ALTO': '#0088FF'}
        
        for status in family_analysis.columns:
            fig.add_trace(go.Bar(
                name=status,
                x=family_analysis.index,
                y=family_analysis[status],
                marker_color=colors.get(status, 'gray')
            ))
        
        fig.update_layout(
            title="Análisis de Stock por Familia de Productos",
            xaxis_title="Familia",
            yaxis_title="Cantidad de Productos",
            barmode='stack',
            xaxis_tickangle=-45,
            height=500,
            font_size=10
        )
        
        return fig
    
    def _create_empty_chart(self, message: str) -> go.Figure:
        """Crea gráfico vacío con mensaje"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font_size=16
        )
        return fig
    
    def create_consumption_trend_chart(self) -> go.Figure:
        """Crea gráfico de tendencia de consumo"""
        # Simular tendencia basada en consumo diario
        consumption_by_curva = self.data.groupby('curva')['consumo_diario'].sum().reset_index()
        
        fig = px.bar(
            consumption_by_curva,
            x='curva',
            y='consumo_diario',
            title="Consumo Diario Total por Curva ABC",
            color='curva',
            color_discrete_map={'A': '#FF6B6B', 'B': '#4ECDC4', 'C': '#45B7D1'}
        )
        
        fig.update_layout(
            xaxis_title="Curva ABC",
            yaxis_title="Consumo Diario",
            font_size=12
        )
        
        return fig
    
    def generate_replenishment_report(self) -> pd.DataFrame:
        """Genera reporte de reposición sugerida"""
        # Filtrar productos que necesitan reposición
        needs_replenishment = self.data[
            self.data['estado_stock'].isin(['CRÍTICO', 'BAJO'])
        ].copy()
        
        if len(needs_replenishment) == 0:
            return pd.DataFrame(columns=[
                'Codigo', 'Descripcion', 'Stock Actual', 'Consumo Diario',
                'Dias Cobertura', 'Estado', 'Cantidad Sugerida', 'Prioridad'
            ])
        
        # Calcular cantidad sugerida de reposición
        needs_replenishment['cantidad_sugerida'] = needs_replenishment.apply(
            self._calculate_suggested_quantity, axis=1
        )
        
        # Asignar prioridad
        needs_replenishment['prioridad'] = needs_replenishment['estado_stock'].map({
            'CRÍTICO': 1,
            'BAJO': 2,
            'NORMAL': 3,
            'ALTO': 4
        })
        
        # Seleccionar y renombrar columnas para el reporte
        report = needs_replenishment[[
            'codigo', 'descripcion', 'stock', 'consumo_diario',
            'dias_cobertura', 'estado_stock', 'cantidad_sugerida', 'prioridad'
        ]].copy()
        
        report.columns = [
            'Codigo', 'Descripcion', 'Stock Actual', 'Consumo Diario',
            'Dias Cobertura', 'Estado', 'Cantidad Sugerida', 'Prioridad'
        ]
        
        # Ordenar por prioridad y días de cobertura
        report = report.sort_values(['Prioridad', 'Dias Cobertura']).reset_index(drop=True)
        
        # Formatear números
        report['Stock Actual'] = report['Stock Actual'].round(2)
        report['Consumo Diario'] = report['Consumo Diario'].round(2)
        report['Dias Cobertura'] = report['Dias Cobertura'].round(1)
        report['Cantidad Sugerida'] = report['Cantidad Sugerida'].round(2)
        
        return report
    
    def _calculate_suggested_quantity(self, row) -> float:
        """Calcula cantidad sugerida de reposición"""
        # Objetivo: mantener 30 días de stock para curva A, 20 para B, 15 para C
        target_days = {'A': 30, 'B': 20, 'C': 15}
        target = target_days.get(row['curva'], 20)
        
        target_stock = row['consumo_diario'] * target
        current_stock = row['stock']
        
        suggested = max(0, target_stock - current_stock)
        return suggested
    
    def get_summary_metrics(self) -> Dict:
        """Obtiene métricas resumidas para dashboard"""
        return {
            'total_productos': self.kpis['total_products'],
            'productos_criticos': self.kpis['critical_products'],
            'productos_bajo': self.kpis['low_products'],
            'porcentaje_critico': f"{self.kpis['critical_percentage']:.1f}%",
            'valor_inventario': f"${self.kpis['total_stock_value']:,.0f}",
            'productos_curva_a': self.kpis['curva_distribution'].get('A', 0),
            'productos_curva_b': self.kpis['curva_distribution'].get('B', 0),
            'productos_curva_c': self.kpis['curva_distribution'].get('C', 0),
            'cobertura_promedio_a': f"{self.kpis['avg_coverage_by_curva'].get('A', 0):.1f} días",
            'cobertura_promedio_b': f"{self.kpis['avg_coverage_by_curva'].get('B', 0):.1f} días",
            'cobertura_promedio_c': f"{self.kpis['avg_coverage_by_curva'].get('C', 0):.1f} días"
        }