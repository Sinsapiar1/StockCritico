import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
import re

class ERPDataProcessor:
    def __init__(self):
        self.curva_abc_data = None
        self.stock_data = None
        self.consolidated_data = None
    
    def process_curva_abc(self, file_path: str) -> pd.DataFrame:
        """
        Procesa el archivo de Curva ABC manejando celdas combinadas
        """
        try:
            print("Iniciando procesamiento de Curva ABC...")
            
            # Leer archivo sin headers
            df = pd.read_excel(file_path, header=None)
            print(f"Archivo leído: {df.shape[0]} filas, {df.shape[1]} columnas")
            
            # Debug básico: mostrar estructura
            print("\n=== MUESTRA DEL ARCHIVO ===")
            for i in range(min(50, len(df))):
                row_values = []
                for j in range(min(8, len(df.columns))):
                    cell = df.iloc[i, j]
                    if pd.notna(cell):
                        row_values.append(f"Col{j}:'{str(cell)[:25]}'")
                
                if row_values:
                    print(f"F{i:2d}: {' | '.join(row_values)}")
            print("=== FIN MUESTRA ===\n")
            
            # Búsqueda simple de productos
            consolidated_data = []
            current_service = "Servicio General"
            current_curva = "C"  # Default
            
            for idx, row in df.iterrows():
                try:
                    # Buscar códigos de producto en cualquier columna
                    for col_idx in range(min(4, len(row))):
                        cell = row.iloc[col_idx]
                        if pd.isna(cell):
                            continue
                        
                        cell_str = str(cell).strip()
                        
                        # Intentar detectar código de producto
                        try:
                            code = int(float(cell_str))
                            if 1 <= code <= 999999:  # Rango válido de códigos
                                
                                # Buscar descripción en columnas siguientes
                                description = "Sin descripción"
                                consumption = 0
                                
                                for desc_col in range(col_idx + 1, len(row)):
                                    desc_cell = row.iloc[desc_col]
                                    if pd.isna(desc_cell):
                                        continue
                                    
                                    desc_str = str(desc_cell).strip()
                                    
                                    # Si es texto largo, probablemente es descripción
                                    if (len(desc_str) > 5 and 
                                        not desc_str.replace('.', '').replace(',', '').isdigit() and
                                        "Total" not in desc_str):
                                        description = desc_str
                                        break
                                
                                # Buscar consumo (primer número grande después del código)
                                for cons_col in range(col_idx + 1, len(row)):
                                    cons_cell = row.iloc[cons_col]
                                    if pd.isna(cons_cell):
                                        continue
                                    
                                    try:
                                        cons_val = float(str(cons_cell).replace(',', '.'))
                                        if cons_val > 0:
                                            consumption = cons_val
                                            break
                                    except:
                                        continue
                                
                                # Si encontramos código + descripción + consumo válido
                                if description != "Sin descripción" and consumption > 0:
                                    product_data = [
                                        str(code), description, "Und", consumption, 
                                        0, 0, current_curva, current_service, 
                                        "01/09/2025", "08/09/2025"
                                    ]
                                    consolidated_data.append(product_data)
                                    print(f"✓ PRODUCTO: {code} - {description[:30]} - Consumo: {consumption}")
                                    break  # No buscar más en esta fila
                        
                        except ValueError:
                            continue
                
                except Exception as e:
                    continue
            
            print(f"\nProductos encontrados: {len(consolidated_data)}")
            
            if consolidated_data:
                columns = ['codigo', 'descripcion', 'unidad', 'consumo', 'costo_unit', 
                          'costo_total', 'curva', 'servicio', 'fecha_inicio', 'fecha_fin']
                
                result_df = pd.DataFrame(consolidated_data, columns=columns)
                result_df = self._clean_curva_dataframe(result_df)
                
                print(f"DataFrame final: {len(result_df)} productos")
                self.curva_abc_data = result_df
                return result_df
            else:
                raise Exception("No se encontraron productos válidos en el archivo")
                
        except Exception as e:
            print(f"Error en process_curva_abc: {str(e)}")
            raise Exception(f"Error procesando Curva ABC: {str(e)}")
    
    def _extract_service_name(self, text: str) -> str:
        """Extrae nombre del servicio de forma simple"""
        try:
            if "Desayuno" in text:
                return "Desayuno"
            elif "Almuerzo" in text:
                return "Almuerzo"
            elif "Cena" in text:
                return "Cena"
            elif "Colacion" in text:
                return "Colación"
            else:
                # Extraer texto después de ":"
                parts = text.split(":")
                if len(parts) > 1:
                    return parts[1].strip()[:50]  # Primeros 50 caracteres
                return "Servicio"
        except:
            return "Servicio"
    
    def _extract_dates(self, text: str) -> Tuple[str, str]:
        """Extrae fechas de forma robusta"""
        try:
            # Buscar patrón DD/MM/YYYY
            dates = re.findall(r'\d{2}/\d{2}/\d{4}', text)
            if len(dates) >= 2:
                return dates[0], dates[1]
            return ("01/09/2025", "08/09/2025")  # Default
        except:
            return ("01/09/2025", "08/09/2025")
    
    def _is_product_row(self, row: pd.Series) -> bool:
        """Detecta si es fila de producto (primera celda es número)"""
        try:
            first_cell = row.iloc[0]
            if pd.isna(first_cell):
                return False
            
            # Verificar si es un número (código de producto)
            first_str = str(first_cell).strip()
            
            # Debe ser un número y no ser un total o texto
            if (first_str.isdigit() and 
                len(first_str) <= 6 and  # Códigos típicos son <= 6 dígitos
                "Total" not in str(row.iloc[1] if len(row) > 1 else "")):
                return True
            
            return False
        except:
            return False
    
    def _extract_product_data_simple(self, row: pd.Series, service: str, 
                                   dates: Tuple[str, str], curva: str) -> List:
        """Extrae datos del producto de forma simple y robusta"""
        try:
            # Necesitamos al menos código, descripción y consumo
            if len(row) < 3:
                return None
            
            codigo = str(row.iloc[0]).strip()
            descripcion = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else "Sin descripción"
            
            # Buscar columna de consumo (puede estar en posición 2, 3 o 4)
            consumo = None
            unidad = "Und"
            
            # Intentar encontrar unidad y consumo
            for i in range(2, min(len(row), 6)):
                cell_value = row.iloc[i]
                if pd.notna(cell_value):
                    cell_str = str(cell_value).strip()
                    
                    # Si parece unidad (texto corto)
                    if len(cell_str) <= 5 and not cell_str.replace('.', '').replace(',', '').isdigit():
                        unidad = cell_str
                    
                    # Si parece consumo (número)
                    numeric_value = self._safe_numeric_convert(cell_value)
                    if numeric_value is not None and numeric_value > 0 and consumo is None:
                        consumo = numeric_value
                        break
            
            # Si no encontró consumo, intentar posición fija
            if consumo is None:
                for i in [3, 2, 4]:  # Posiciones típicas para consumo
                    if i < len(row):
                        consumo = self._safe_numeric_convert(row.iloc[i])
                        if consumo is not None and consumo > 0:
                            break
            
            # Validar que tenemos datos mínimos
            if consumo is None or consumo <= 0:
                return None
            
            # Extraer costos opcionales
            costo_unit = 0
            costo_total = 0
            
            # Buscar costos en las últimas columnas
            for i in range(len(row)-1, max(3, len(row)-4), -1):
                if i < len(row):
                    value = self._safe_numeric_convert(row.iloc[i])
                    if value is not None and value > 0:
                        if costo_total == 0:
                            costo_total = value
                        elif costo_unit == 0:
                            costo_unit = value
            
            fecha_inicio, fecha_fin = dates if dates else ("01/09/2025", "08/09/2025")
            
            print(f"  -> Extraído: {codigo} | {descripcion[:20]} | {unidad} | {consumo}")
            
            return [codigo, descripcion, unidad, consumo, costo_unit, 
                   costo_total, curva, service, fecha_inicio, fecha_fin]
            
        except Exception as e:
            print(f"  -> Error extrayendo: {str(e)}")
            return None
    
    def _safe_numeric_convert(self, value):
        """Convierte valor a numérico de manera segura"""
        if pd.isna(value):
            return 0
        
        try:
            # Limpiar formato de números
            if isinstance(value, str):
                # Remover espacios, comas como separadores de miles
                cleaned = value.replace(' ', '').replace(',', '')
                # Si hay punto seguido de exactamente 2 dígitos, es decimal
                if '.' in cleaned and len(cleaned.split('.')[-1]) <= 2:
                    return float(cleaned)
                # Si hay punto pero más de 2 dígitos después, es separador de miles
                elif '.' in cleaned:
                    cleaned = cleaned.replace('.', '')
                return float(cleaned)
            
            return float(value)
        except:
            return 0
    
    def _clean_curva_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia el DataFrame de curva ABC"""
        # Eliminar filas sin código o consumo válido
        df = df.dropna(subset=['codigo'])
        df = df[df['consumo'] > 0]
        
        # Limpiar códigos
        df['codigo'] = df['codigo'].astype(str).str.strip()
        
        # Asegurar que curva tiene valores válidos
        df['curva'] = df['curva'].fillna('C')  # Default a C si no tiene curva
        
        return df.reset_index(drop=True)
    
    def process_stock(self, file_path: str) -> pd.DataFrame:
        """
        Procesa el archivo de stock usando el mismo enfoque exitoso que ABC
        """
        try:
            print("Iniciando procesamiento de Stock...")
            
            # Leer archivo
            df = pd.read_excel(file_path, header=None)
            print(f"Archivo stock leído: {df.shape[0]} filas, {df.shape[1]} columnas")
            
            # Debug: mostrar estructura real
            print("\n=== MUESTRA ARCHIVO STOCK ===")
            for i in range(min(30, len(df))):
                row_values = []
                for j in range(min(8, len(df.columns))):
                    cell = df.iloc[i, j]
                    if pd.notna(cell):
                        row_values.append(f"Col{j}:'{str(cell)[:25]}'")
                
                if row_values:
                    print(f"F{i:2d}: {' | '.join(row_values)}")
            print("=== FIN MUESTRA STOCK ===\n")
            
            stock_data = []
            current_family = "Sin familia"
            
            for idx, row in df.iterrows():
                try:
                    # Detectar familia (igual que antes)
                    row_str = ' '.join([str(cell) for cell in row if pd.notna(cell)])
                    
                    if self._is_family_header(row_str):
                        current_family = self._extract_family_name(row_str)
                        print(f"Familia detectada: {current_family}")
                        continue
                    
                    # Buscar productos usando enfoque similar a ABC
                    for col_idx in range(min(4, len(row))):
                        cell = row.iloc[col_idx]
                        if pd.isna(cell):
                            continue
                        
                        cell_str = str(cell).strip()
                        
                        # Intentar detectar código de producto
                        try:
                            code = int(float(cell_str))
                            if 1 <= code <= 999999:  # Rango válido de códigos
                                
                                # Buscar descripción, unidad y stock
                                description = "Sin descripción"
                                unit = "Und"
                                stock_value = 0
                                price = 0
                                total = 0
                                
                                for search_col in range(col_idx + 1, len(row)):
                                    search_cell = row.iloc[search_col]
                                    if pd.isna(search_cell):
                                        continue
                                    
                                    search_str = str(search_cell).strip()
                                    
                                    # Si es texto largo, probablemente es descripción
                                    if (description == "Sin descripción" and 
                                        len(search_str) > 5 and 
                                        not search_str.replace('.', '').replace(',', '').replace('-', '').isdigit() and
                                        "Total" not in search_str):
                                        description = search_str
                                        continue
                                    
                                    # Si es texto corto, puede ser unidad
                                    if (unit == "Und" and 
                                        len(search_str) <= 5 and 
                                        not search_str.replace('.', '').replace(',', '').isdigit()):
                                        unit = search_str
                                        continue
                                    
                                    # Si es número, puede ser stock, precio o total
                                    try:
                                        numeric_val = float(search_str.replace(',', '.'))
                                        if stock_value == 0:
                                            stock_value = numeric_val
                                        elif price == 0:
                                            price = numeric_val
                                        elif total == 0:
                                            total = numeric_val
                                    except:
                                        continue
                                
                                # Si encontramos código + descripción válida
                                if description != "Sin descripción":
                                    product_data = [
                                        str(code), description, unit, stock_value, 
                                        price, total, current_family
                                    ]
                                    stock_data.append(product_data)
                                    print(f"✓ STOCK: {code} - {description[:30]} - Stock: {stock_value}")
                                    break  # No buscar más en esta fila
                        
                        except ValueError:
                            continue
                
                except Exception as e:
                    continue
            
            print(f"\nProductos de stock encontrados: {len(stock_data)}")
            
            if stock_data:
                columns = ['codigo', 'descripcion', 'unidad', 'stock', 'precio', 'total', 'familia']
                result_df = pd.DataFrame(stock_data, columns=columns)
                result_df = self._clean_stock_dataframe(result_df)
                
                print(f"DataFrame stock final: {len(result_df)} productos")
                self.stock_data = result_df
                return result_df
            else:
                raise Exception("No se encontraron productos válidos en el archivo de stock")
                
        except Exception as e:
            print(f"Error en process_stock: {str(e)}")
            raise Exception(f"Error procesando archivo de stock: {str(e)}")
    
    def _is_family_header(self, text: str) -> bool:
        """Detecta headers de familia"""
        text = text.strip()
        # Buscar patrón: número + espacios + texto en mayúsculas
        return bool(re.match(r'^\d+\s+[A-ZÁÉÍÓÚÑ\s]+$', text))
    
    def _extract_family_name(self, text: str) -> str:
        """Extrae nombre de familia"""
        try:
            # Remover números del inicio
            cleaned = re.sub(r'^\d+\s*', '', text.strip())
            return cleaned[:50] if cleaned else "Sin familia"
        except:
            return "Sin familia"
    
    def _is_stock_product_row(self, row: pd.Series) -> bool:
        """Detecta filas de productos en stock"""
        try:
            if len(row) < 4:  # Mínimo: código, descripción, unidad, stock
                return False
            
            first_cell = str(row.iloc[0]).strip()
            
            # Debe ser código numérico y tener descripción
            if (first_cell.isdigit() and 
                len(first_cell) <= 6 and
                pd.notna(row.iloc[1]) and
                str(row.iloc[1]).strip() != ""):
                return True
            
            return False
        except:
            return False
    
    def _extract_stock_product_simple(self, row: pd.Series, family: str) -> List:
        """Extrae producto de stock usando búsqueda flexible"""
        try:
            # Buscar código en las primeras columnas
            codigo = None
            descripcion = "Sin descripción"
            unidad = "Und" 
            stock = 0
            precio = 0
            total = 0
            
            # Buscar código de producto
            for col_idx in range(min(4, len(row))):
                cell = row.iloc[col_idx]
                if pd.isna(cell):
                    continue
                
                cell_str = str(cell).strip()
                
                try:
                    code = int(float(cell_str))
                    if 1 <= code <= 999999:
                        codigo = str(code)
                        
                        # Buscar descripción, unidad y valores en columnas siguientes
                        for search_col in range(col_idx + 1, len(row)):
                            search_cell = row.iloc[search_col]
                            if pd.isna(search_cell):
                                continue
                            
                            search_str = str(search_cell).strip()
                            
                            # Buscar descripción (texto largo, no número)
                            if (descripcion == "Sin descripción" and 
                                len(search_str) > 5 and 
                                not search_str.replace('.', '').replace(',', '').isdigit() and
                                "Total" not in search_str):
                                descripcion = search_str
                                continue
                            
                            # Buscar unidad (texto corto)
                            if (unidad == "Und" and 
                                len(search_str) <= 5 and 
                                not search_str.replace('.', '').replace(',', '').isdigit()):
                                unidad = search_str
                                continue
                            
                            # Buscar valores numéricos (stock, precio, total)
                            try:
                                numeric_val = float(search_str.replace(',', '.'))
                                if numeric_val >= 0:
                                    if stock == 0:
                                        stock = numeric_val
                                    elif precio == 0:
                                        precio = numeric_val
                                    elif total == 0:
                                        total = numeric_val
                            except:
                                continue
                        
                        # Validar que tenemos datos mínimos
                        if descripcion != "Sin descripción":
                            print(f"✓ STOCK: {codigo} - {descripcion[:30]} - Stock: {stock}")
                            return [codigo, descripcion, unidad, stock, precio, total, family]
                        
                        break  # No buscar más códigos en esta fila
                
                except ValueError:
                    continue
            
            return None
            
        except Exception as e:
            return None
    
    def _clean_stock_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia DataFrame de stock"""
        # Eliminar filas sin código
        df = df.dropna(subset=['codigo'])
        
        # Limpiar códigos
        df['codigo'] = df['codigo'].astype(str).str.strip()
        
        # Asegurar que stock es numérico
        df['stock'] = pd.to_numeric(df['stock'], errors='coerce').fillna(0)
        
        return df.reset_index(drop=True)
    
    def calculate_coverage_analysis(self, days_period: int = 8) -> pd.DataFrame:
        """
        Calcula análisis de cobertura combinando datos
        """
        try:
            if self.curva_abc_data is None or self.stock_data is None:
                raise Exception("Debe procesar ambos archivos primero")
            
            print(f"Calculando análisis con {len(self.curva_abc_data)} productos ABC y {len(self.stock_data)} productos stock")
            
            # Consolidar consumo por código (sumar todos los servicios)
            consumo_consolidado = self.curva_abc_data.groupby('codigo').agg({
                'descripcion': 'first',
                'unidad': 'first', 
                'consumo': 'sum',
                'curva': 'first'
            }).reset_index()
            
            print(f"Productos consolidados: {len(consumo_consolidado)}")
            
            # Calcular consumo promedio diario
            consumo_consolidado['consumo_diario'] = consumo_consolidado['consumo'] / days_period
            
            # Hacer merge con stock (inner join para tener solo productos que están en ambos)
            analysis = pd.merge(
                consumo_consolidado,
                self.stock_data[['codigo', 'stock', 'familia']],
                on='codigo',
                how='inner'
            )
            
            print(f"Productos después del merge: {len(analysis)}")
            
            if len(analysis) == 0:
                raise Exception("No hay productos en común entre Curva ABC y Stock. Verificar códigos de productos.")
            
            # Calcular días de cobertura
            analysis['dias_cobertura'] = analysis.apply(
                lambda row: row['stock'] / row['consumo_diario'] 
                if row['consumo_diario'] > 0 else 999, axis=1
            )
            
            # Clasificar estado según curva ABC
            analysis['estado_stock'] = analysis.apply(self._classify_stock_status, axis=1)
            
            # Calcular fecha de quiebre
            analysis['fecha_quiebre'] = analysis.apply(self._calculate_breakage_date, axis=1)
            
            print(f"Análisis completado con {len(analysis)} productos")
            
            # Mostrar estadísticas básicas
            print("Distribución por estado:")
            print(analysis['estado_stock'].value_counts())
            
            self.consolidated_data = analysis
            return analysis
            
        except Exception as e:
            print(f"Error en calculate_coverage_analysis: {str(e)}")
            raise Exception(f"Error calculando análisis: {str(e)}")
    
    def _classify_stock_status(self, row) -> str:
        """Clasifica estado del stock según curva"""
        try:
            dias = row['dias_cobertura']
            curva = row['curva']
            
            # Umbrales por curva
            umbrales = {'A': 3, 'B': 5, 'C': 7}
            umbral = umbrales.get(curva, 5)
            
            if dias <= umbral:
                return 'CRÍTICO'
            elif dias <= umbral * 2:
                return 'BAJO'
            elif dias <= umbral * 4:
                return 'NORMAL'
            else:
                return 'ALTO'
        except:
            return 'NORMAL'
    
    def _calculate_breakage_date(self, row) -> str:
        """Calcula fecha de quiebre"""
        try:
            from datetime import datetime, timedelta
            
            if row['consumo_diario'] > 0:
                dias_restantes = int(row['dias_cobertura'])
                fecha_quiebre = datetime.now() + timedelta(days=dias_restantes)
                return fecha_quiebre.strftime('%d/%m/%Y')
            else:
                return 'Sin consumo'
        except:
            return 'Error cálculo'