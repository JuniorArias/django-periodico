#!/usr/bin/env python3
"""
Script para generar archivo de contexto del proyecto Django
Uso: python generar_contexto.py
"""

import os
from pathlib import Path

# Extensiones de archivos a incluir
EXTENSIONES = {'.py', '.html', '.css', '.js', '.json', '.md', '.txt', '.yml', '.yaml'}

# Carpetas a ignorar
IGNORAR_CARPETAS = {
    'venv', '.venv', 'env', '.env',
    '__pycache__', '.git', '.github',
    'staticfiles', 'media', 'node_modules',
    '.pytest_cache', '.mypy_cache', '.ruff_cache',
    'dist', 'build', '.eggs'
}

# Archivos a ignorar
IGNORAR_ARCHIVOS = {
    '.gitignore', '.env', '.env.local',
    'db.sqlite3', '*.pyc', '*.pyo',
    'contexto_proyecto.txt'
}

def debe_incluir(ruta: Path) -> bool:
    """Determina si un archivo debe ser incluido"""
    # Verificar extensión
    if ruta.suffix.lower() not in EXTENSIONES:
        return False
    
    # Verificar si está en carpetas ignoradas
    for parte in ruta.parts:
        if parte in IGNORAR_CARPETAS:
            return False
    
    # Verificar nombre de archivo
    if ruta.name in IGNORAR_ARCHIVOS:
        return False
    
    # Verificar patrones glob
    for patron in IGNORAR_ARCHIVOS:
        if '*' in patron and ruta.match(patron):
            return False
    
    return True

def generar_contexto(directorio_raiz: str = '.'):
    """Genera archivo de contexto con todo el código del proyecto"""
    
    ruta_raiz = Path(directorio_raiz).resolve()
    archivos_incluidos = []
    
    print(f"🔍 Escaneando proyecto en: {ruta_raiz}")
    print("=" * 60)
    
    # Recorrer todos los archivos
    for ruta_archivo in ruta_raiz.rglob('*'):
        if ruta_archivo.is_file() and debe_incluir(ruta_archivo):
            try:
                # Leer contenido del archivo
                with open(ruta_archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                # Calcular ruta relativa
                ruta_relativa = ruta_archivo.relative_to(ruta_raiz)
                
                archivos_incluidos.append({
                    'ruta': str(ruta_relativa),
                    'contenido': contenido,
                    'lineas': len(contenido.splitlines())
                })
                
                print(f"✅ {ruta_relativa} ({len(contenido.splitlines())} líneas)")
                
            except Exception as e:
                print(f"⚠️  Error leyendo {ruta_archivo}: {e}")
    
    # Ordenar archivos por ruta
    archivos_incluidos.sort(key=lambda x: x['ruta'])
    
    # Generar archivo de salida
    archivo_salida = ruta_raiz / 'contexto_proyecto.txt'
    
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("CONTEXTO DEL PROYECTO DJANGO\n")
        f.write(f"Generado automáticamente desde: {ruta_raiz}\n")
        f.write(f"Total de archivos: {len(archivos_incluidos)}\n")
        f.write("=" * 80 + "\n\n")
        
        # Índice de archivos
        f.write("ÍNDICE DE ARCHIVOS:\n")
        f.write("-" * 80 + "\n")
        for i, archivo in enumerate(archivos_incluidos, 1):
            f.write(f"{i:3d}. {archivo['ruta']} ({archivo['lineas']} líneas)\n")
        f.write("\n" + "=" * 80 + "\n\n")
        
        # Contenido de cada archivo
        for archivo in archivos_incluidos:
            f.write("=" * 80 + "\n")
            f.write(f"ARCHIVO: {archivo['ruta']}\n")
            f.write("=" * 80 + "\n")
            f.write(archivo['contenido'])
            f.write("\n\n")
    
    print("\n" + "=" * 60)
    print(f"✅ Contexto generado exitosamente!")
    print(f"📄 Archivo: {archivo_salida}")
    print(f"📊 Total: {len(archivos_incluidos)} archivos")
    print(f"📏 Tamaño: {archivo_salida.stat().st_size / 1024:.2f} KB")
    print("=" * 60)
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Abre el archivo 'contexto_proyecto.txt'")
    print("2. Copia TODO el contenido")
    print("3. Pégalo en el chat de Claude")
    print("4. Claude tendrá contexto completo de tu proyecto")

if __name__ == '__main__':
    generar_contexto()staticfiles/ 
