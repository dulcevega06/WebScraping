import os
# Ruta de tu archivo original
ruta = r"C:\Users\122215\OneDrive\Documentos\UAdeO\SEMESTRE 3\PE\WebScraping_Revistas-main\utf8\AUTHORS_master_v3.csv"
# Leer el contenido del archivo
with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
    texto = f.read()
# Diccionario de reemplazos
reemplazos = {
    "Ã¡": "á", "Ã©": "é", "Ã­": "í", "Ã³": "ó", "Ãº": "ú",
    "Ã±": "ñ", "Â": "", "â€“": "–", "â€”": "—",
    "â€œ": '"', "â€�": '"', "â€˜": "'", "â€™": "'"
}
# Aplicar los reemplazos
for malo, bueno in reemplazos.items():
    texto = texto.replace(malo, bueno)

# Guardar el archivo limpio
ruta_salida = ruta.replace(".csv", "_limpio.csv")

with open(ruta_salida, "w", encoding="utf-8-sig", newline="") as f:
    f.write(texto)
print(f"Archivo limpio guardado en:\n{ruta_salida}")