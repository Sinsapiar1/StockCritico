import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
import re

class ERPDataProcessor:
    def __init__(self):
        self.curva_abc_data = None
        self.stock_data = None
        self.consolidated_data = None
        self.analysis_period_start = None
        self.analysis_period_end = None
        self.analysis_days = 8  # Default
    
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
            
            # Extraer fechas del archivo automáticamente
            self._extract_analysis_period(df)
            
            # Búsqueda inteligente de productos con detección de servicios y curvas
            consolidated_data = []
            current_service = "Servicio General"
            current_curva = "C"  # Default
            
            for idx, row in df.iterrows():
                try:
                    # DEBUG ESPECÍFICO para productos problema
                    row_str = ' '.join([str(cell) for cell in row if pd.notna(cell)])
                    if any(code in row_str for code in ['453', '641']):
                        print(f"\n🔍 DEBUG FILA {idx} - PRODUCTO PROBLEMA:")
                        print(f"   Fila completa: {row_str}")
                        for col_idx, cell in enumerate(row):
                            if pd.notna(cell):
                                print(f"   Col{col_idx}: '{cell}'")
                    
                    # Detectar servicios y curvas
                    
                    # Detectar servicio (múltiples patrones)
                    if ("Servicio" in row_str and ":" in row_str) or ("10000" in row_str and "Desayuno" in row_str) or ("10001" in row_str and "Almuerzo" in row_str) or ("10003" in row_str and "Cena" in row_str):
                        current_service = self._extract_service_name(row_str)
                        print(f"🍽️ Servicio detectado: {current_service}")
                        continue
                    
                    # Detectar curva ABC
                    if "Curva A" in row_str:
                        current_curva = "A"
                        print(f"Curva A detectada")
                        continue
                    elif "Curva B" in row_str:
                        current_curva = "B"
                        print(f"Curva B detectada")
                        continue
                    elif "Curva C" in row_str:
                        current_curva = "C"
                        print(f"Curva C detectada")
                        continue
                    
                    # Buscar códigos de producto en cualquier columna - MEJORADO
                    for col_idx in range(min(6, len(row))):  # Ampliado de 4 a 6
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
                                
                                # MEJORADA: Búsqueda más flexible de descripción
                                for desc_col in range(col_idx + 1, len(row)):
                                    desc_cell = row.iloc[desc_col]
                                    if pd.isna(desc_cell):
                                        continue
                                    
                                    desc_str = str(desc_cell).strip()
                                    
                                    # Si es texto largo, probablemente es descripción
                                    if (len(desc_str) > 2 and  # Cambiado de 5 a 2 para casos como "LIMON"
                                        not desc_str.replace('.', '').replace(',', '').isdigit() and
                                        "Total" not in desc_str):
                                        description = desc_str
                                        break
                                
                                # MEJORADA: Búsqueda más flexible de consumo
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
                                
                                # VALIDACIÓN MÁS FLEXIBLE para casos especiales
                                if (description != "Sin descripción" and consumption > 0) or \
                                   (len(str(description).strip()) > 1 and consumption > 0):
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
        """Extrae nombre del servicio de forma inteligente"""
        try:
            # Patrones específicos de servicios
            if "10000" in text and "Desayuno" in text:
                return "Desayuno"
            elif "10001" in text and "Almuerzo" in text:
                return "Almuerzo"
            elif "10003" in text and "Cena" in text:
                return "Cena"
            elif "10007" in text and "Nochera" in text:
                return "Cena Nochera"
            elif "10008" in text and "Colacion" in text:
                return "Colación Reemplazo"
            elif "10066" in text and "Gimnasio" in text:
                return "Choca Gimnasio"
            elif "10948" in text and "Bajada" in text:
                return "Colación Bajada"
            elif "11198" in text and "Satelital" in text:
                return "Almuerzo Satelital"
            elif "Desayuno" in text:
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
                    service_name = parts[1].strip()
                    # Limpiar números y caracteres especiales
                    import re
                    clean_name = re.sub(r'^\d+\s*-\s*', '', service_name)
                    return clean_name[:30]  # Primeros 30 caracteres
                return "Servicio General"
        except:
            return "Servicio General"
    
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
    
    def _extract_analysis_period(self, df: pd.DataFrame):
        """Extrae automáticamente el período de análisis del archivo"""
        try:
            print("\n📅 Extrayendo período de análisis del archivo...")
            
            # Buscar fechas en las primeras 20 filas
            for idx, row in df.head(20).iterrows():
                row_str = ' '.join([str(cell) for cell in row if pd.notna(cell)])
                
                if "Rango" in row_str and "Facha" in row_str:
                    dates = re.findall(r'\d{2}/\d{2}/\d{4}', row_str)
                    if len(dates) >= 2:
                        self.analysis_period_start = dates[0]
                        self.analysis_period_end = dates[1]
                        self.analysis_days = self._calculate_period_days(dates[0], dates[1])
                        
                        print(f"✅ Período detectado: {self.analysis_period_start} - {self.analysis_period_end}")
                        print(f"✅ Días de análisis: {self.analysis_days}")
                        return
            
            # Si no encuentra fechas, usar defaults
            self.analysis_period_start = "01/09/2025"
            self.analysis_period_end = "08/09/2025"
            self.analysis_days = 8
            print(f"⚠️ Fechas no detectadas, usando default: {self.analysis_period_start} - {self.analysis_period_end}")
            
        except Exception as e:
            print(f"Error extrayendo fechas: {e}")
            self.analysis_period_start = "01/09/2025"
            self.analysis_period_end = "08/09/2025" 
            self.analysis_days = 8

    def _calculate_period_days(self, start_date: str, end_date: str) -> int:
        """Calcula días del período de análisis"""
        try:
            from datetime import datetime
            start = datetime.strptime(start_date, '%d/%m/%Y')
            end = datetime.strptime(end_date, '%d/%m/%Y')
            days = (end - start).days + 1  # +1 para incluir ambos días
            return days if days > 0 else 8  # Default 8 días
        except:
            return 8  # Default
    
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
            
            # Debug: mostrar estructura real con más detalle
            print("\n=== MUESTRA ARCHIVO STOCK (DETALLADO) ===")
            for i in range(min(50, len(df))):
                row_values = []
                for j in range(min(10, len(df.columns))):
                    cell = df.iloc[i, j]
                    if pd.notna(cell):
                        cell_str = str(cell)[:30]
                        # Detectar si parece código de producto
                        is_code = False
                        try:
                            code = int(float(str(cell).strip()))
                            if 1 <= code <= 999999:
                                is_code = True
                        except:
                            pass
                        
                        marker = " [CÓDIGO?]" if is_code else ""
                        row_values.append(f"Col{j}:'{cell_str}'{marker}")
                
                if row_values:
                    print(f"F{i:2d}: {' | '.join(row_values)}")
                else:
                    print(f"F{i:2d}: [VACÍA]")
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
        print(f"\n🚨 INICIANDO ANÁLISIS DE COBERTURA")
        print(f"📊 ABC disponible: {len(self.curva_abc_data) if self.curva_abc_data is not None else 'None'}")
        print(f"📦 Stock disponible: {len(self.stock_data) if self.stock_data is not None else 'None'}")
        
        if self.curva_abc_data is None or self.stock_data is None:
            raise Exception("Debe procesar ambos archivos primero")
        
        print(f"\n=== ANÁLISIS EXPERTO DE COBERTURA ===")
        print(f"📊 Productos Curva ABC: {len(self.curva_abc_data)}")
        print(f"📦 Productos Stock: {len(self.stock_data)}")
        print(f"📅 Período de análisis: {days_period} días")
        
        # PASO 1: Consolidar consumo por código con debugging detallado
        print(f"\n🔄 PASO 1: Consolidando consumo por producto...")
        try:
            consumo_consolidado = self.curva_abc_data.groupby('codigo').agg({
                'descripcion': 'first',
                'unidad': 'first', 
                'consumo': 'sum',  # SUMA de todos los servicios
                'curva': 'first',
                'servicio': 'first'  # Tomar el primer servicio donde aparece
            }).reset_index()
            
            print(f"✅ Productos consolidados: {len(consumo_consolidado)}")
            
            # Debug productos específicos en consolidación
            for code in ['453', '641']:
                if code in consumo_consolidado['codigo'].values:
                    row = consumo_consolidado[consumo_consolidado['codigo'] == code].iloc[0]
                    print(f"   ✅ {code}: {row['descripcion']} - Consumo: {row['consumo']}")
                else:
                    print(f"   ❌ {code}: NO encontrado en consolidación")
                    
        except Exception as e:
            print(f"💥 ERROR EN PASO 1: {str(e)}")
            raise e
        
        # PASO 2: Calcular consumo promedio diario
        print(f"\n🧮 PASO 2: Calculando consumo promedio diario...")
        try:
            consumo_consolidado['consumo_diario'] = consumo_consolidado['consumo'] / days_period
            
            # Mostrar ejemplos del cálculo
            top_consumers = consumo_consolidado.nlargest(3, 'consumo')
            for _, product in top_consumers.iterrows():
                print(f"   📈 {product['codigo']}: {product['consumo']:.1f} total ÷ {days_period} días = {product['consumo_diario']:.2f}/día")
                
            # Debug productos específicos después del cálculo diario
            for code in ['453', '641']:
                if code in consumo_consolidado['codigo'].values:
                    row = consumo_consolidado[consumo_consolidado['codigo'] == code].iloc[0]
                    print(f"   ✅ {code}: Consumo diario = {row['consumo_diario']:.2f}")
                else:
                    print(f"   ❌ {code}: NO encontrado para cálculo diario")
                    
        except Exception as e:
            print(f"💥 ERROR EN PASO 2: {str(e)}")
            raise e
        
        # PASO 3: Preparar datos para merge
        print(f"\n🔗 PASO 3: Preparando datos para merge...")
        try:
            # Asegurar que códigos sean strings para merge correcto
            print(f"   🔧 Limpiando códigos para merge...")
            consumo_consolidado['codigo'] = consumo_consolidado['codigo'].astype(str).str.strip()
            self.stock_data['codigo'] = self.stock_data['codigo'].astype(str).str.strip()
            
            print(f"   📊 Consumo consolidado: {len(consumo_consolidado)} productos")
            print(f"   📦 Stock data: {len(self.stock_data)} productos")
            
            # Verificar que los códigos problema están en ambos DataFrames antes del merge
            for code in ['453', '641']:
                in_consumo = code in consumo_consolidado['codigo'].values
                in_stock = code in self.stock_data['codigo'].values
                print(f"   🔍 {code}: Consumo={in_consumo}, Stock={in_stock}")
                
        except Exception as e:
            print(f"💥 ERROR EN PASO 3: {str(e)}")
            raise e
        
        # PASO 4: Realizar merge con debugging detallado
        print(f"\n🔀 PASO 4: Realizando merge RIGHT JOIN...")
        try:
            analysis = pd.merge(
                consumo_consolidado,
                self.stock_data[['codigo', 'descripcion', 'stock', 'familia']],  # Incluir descripción del stock
                on='codigo',
                how='right',  # RIGHT JOIN: incluye TODOS los productos de stock
                suffixes=('_abc', '_stock')  # Distinguir columnas duplicadas
            )
            
            print(f"✅ Merge completado: {len(analysis)} productos")
            
            # Debug inmediato después del merge
            for code in ['453', '641']:
                if code in analysis['codigo'].values:
                    print(f"   ✅ {code}: PRESENTE en merge")
                else:
                    print(f"   ❌ {code}: AUSENTE después del merge")
                    
        except Exception as e:
            print(f"💥 ERROR EN PASO 4 (MERGE): {str(e)}")
            print(f"   Columnas consumo_consolidado: {list(consumo_consolidado.columns)}")
            print(f"   Columnas self.stock_data: {list(self.stock_data.columns)}")
            raise e
        
        # PASO 5: Completar datos faltantes
        print(f"\n🛠️ PASO 5: Completando datos faltantes...")
        try:
            # Usar descripción del stock cuando no hay en ABC
            analysis['descripcion'] = analysis['descripcion_abc'].fillna(analysis['descripcion_stock'])
            analysis['descripcion'] = analysis['descripcion'].fillna('Producto en inventario')
            
            # Limpiar columnas duplicadas
            analysis = analysis.drop(['descripcion_abc', 'descripcion_stock'], axis=1, errors='ignore')
            
            analysis['unidad'] = analysis['unidad'].fillna('Und')
            analysis['consumo'] = analysis['consumo'].fillna(0)
            analysis['curva'] = analysis['curva'].fillna('NO CONSUMIDO')  # Más claro
            analysis['servicio'] = analysis['servicio'].fillna('No consumido en período')
            analysis['consumo_diario'] = analysis['consumo_diario'].fillna(0)
            
            print(f"✅ Datos completados: {len(analysis)} productos")
            
            # Debug después de completar datos
            for code in ['453', '641']:
                if code in analysis['codigo'].values:
                    row = analysis[analysis['codigo'] == code].iloc[0]
                    print(f"   ✅ {code}: {row['descripcion']} - Consumo diario: {row['consumo_diario']:.2f}")
                else:
                    print(f"   ❌ {code}: NO encontrado después de completar datos")
                    
        except Exception as e:
            print(f"💥 ERROR EN PASO 5: {str(e)}")
            raise e
        
        # PASO 6: Calcular días de cobertura
        print(f"\n⏱️ PASO 6: Calculando días de cobertura...")
        try:
            analysis['dias_cobertura'] = analysis.apply(
                lambda row: row['stock'] / row['consumo_diario'] 
                if row['consumo_diario'] > 0 else 999, axis=1  # 999 = Sin consumo en período
            )
            
            print(f"✅ Días de cobertura calculados")
            
            # Debug después de calcular cobertura
            for code in ['453', '641']:
                if code in analysis['codigo'].values:
                    row = analysis[analysis['codigo'] == code].iloc[0]
                    print(f"   ✅ {code}: Stock={row['stock']}, Consumo diario={row['consumo_diario']:.2f}, Cobertura={row['dias_cobertura']:.1f} días")
                else:
                    print(f"   ❌ {code}: NO encontrado para cálculo cobertura")
                    
        except Exception as e:
            print(f"💥 ERROR EN PASO 6: {str(e)}")
            raise e
        
        # PASO 7: Clasificar estado y fecha de quiebre
        print(f"\n🏷️ PASO 7: Clasificando estados...")
        try:
            analysis['estado_stock'] = analysis.apply(self._classify_stock_status, axis=1)
            analysis['fecha_quiebre'] = analysis.apply(self._calculate_breakage_date, axis=1)
            
            print(f"✅ Estados clasificados")
            
            # Debug final de los productos problema
            for code in ['453', '641']:
                if code in analysis['codigo'].values:
                    row = analysis[analysis['codigo'] == code].iloc[0]
                    print(f"   ✅ {code}: Estado={row['estado_stock']}, Fecha quiebre={row['fecha_quiebre']}")
                else:
                    print(f"   ❌ {code}: NO encontrado para clasificación")
                    
        except Exception as e:
            print(f"💥 ERROR EN PASO 7: {str(e)}")
            raise e
        
        # ESTADÍSTICAS FINALES
        print(f"\n📊 ESTADÍSTICAS COMPLETAS DEL ANÁLISIS:")
        productos_con_consumo = len(analysis[analysis['consumo_diario'] > 0])
        productos_sin_consumo = len(analysis[analysis['consumo_diario'] == 0])
        
        print(f"   • Total productos en stock original: {len(self.stock_data)}")
        print(f"   • Total productos en análisis final: {len(analysis)}")
        print(f"   • Con consumo en período: {productos_con_consumo}")
        print(f"   • Sin consumo en período: {productos_sin_consumo}")
        
        # Verificar productos faltantes
        if len(analysis) < len(self.stock_data):
            missing_count = len(self.stock_data) - len(analysis)
            print(f"   ⚠️ ATENCIÓN: {missing_count} productos del stock no aparecen en análisis")
        
        # Estadísticas solo para productos con consumo
        analysis_with_consumption = analysis[analysis['consumo_diario'] > 0]
        if len(analysis_with_consumption) > 0:
            print(f"   • Cobertura promedio (con consumo): {analysis_with_consumption['dias_cobertura'].mean():.1f} días")
            print(f"   • Productos con <3 días: {len(analysis_with_consumption[analysis_with_consumption['dias_cobertura'] < 3])}")
            print(f"   • Productos con <7 días: {len(analysis_with_consumption[analysis_with_consumption['dias_cobertura'] < 7])}")
        
        # Mostrar distribución por estado
        print("   • Distribución por estado:")
        for estado, count in analysis['estado_stock'].value_counts().items():
            print(f"     - {estado}: {count}")
        
        # DEBUG FINAL - PRODUCTOS ESPECÍFICOS
        print(f"\n🔍 DEBUG FINAL - PRODUCTOS PROBLEMA:")
        test_codes = ['453', '641']
        
        for code in test_codes:
            print(f"\n📦 Producto {code}:")
            
            # ¿Está en ABC?
            in_abc = self.curva_abc_data['codigo'].astype(str).str.strip().eq(code).any()
            print(f"   ABC: {'✅' if in_abc else '❌'}")
            
            # ¿Está en Stock?
            in_stock = self.stock_data['codigo'].astype(str).str.strip().eq(code).any()
            print(f"   Stock: {'✅' if in_stock else '❌'}")
            
            # ¿Está en análisis final?
            in_final = analysis['codigo'].astype(str).str.strip().eq(code).any()
            print(f"   Final: {'✅' if in_final else '❌'}")
            
            if in_final:
                row = analysis[analysis['codigo'].astype(str).str.strip() == code].iloc[0]
                print(f"   Estado: {row['estado_stock']}")
                print(f"   Descripción: {row['descripcion']}")
                print(f"   Consumo: {row['consumo']}")
                print(f"   Stock: {row['stock']}")
                print(f"   Días cobertura: {row['dias_cobertura']:.1f}")
            else:
                print(f"   🚨 SE PERDIÓ EN EL PROCESO")
                
                # Investigar dónde se perdió
                if in_abc and not in_stock:
                    print(f"   🔍 Causa: Producto está en ABC pero NO en Stock")
                elif not in_abc and in_stock:
                    print(f"   🔍 Causa: Producto está en Stock pero NO en ABC")
                elif not in_abc and not in_stock:
                    print(f"   🔍 Causa: Producto NO está en ninguno de los archivos")
                else:
                    print(f"   🔍 Causa: Error en el merge - está en ambos pero se perdió")
        
        print(f"\n🎉 ANÁLISIS COMPLETADO EXITOSAMENTE - {len(analysis)} productos procesados")
        
        self.consolidated_data = analysis
        return analysis
            
    def _classify_stock_status(self, row) -> str:
        """Clasifica estado del stock según curva (incluye productos sin consumo)"""
        try:
            dias = row['dias_cobertura']
            curva = row['curva']
            consumo_diario = row.get('consumo_diario', 0)
            
            # Productos sin consumo en el período
            if consumo_diario == 0 or dias >= 999:
                return 'NO CONSUMIDO (01/09-08/09)'
            
            # Umbrales por curva para productos con consumo
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
