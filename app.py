import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

# --- Cargar archivo CSV ---
try:
    df = pd.read_csv(
        r"C:\Users\122215\OneDrive\Documentos\UAdeO\SEMESTRE 3\PE\WebScraping_Revistas-main\utf8\AUTHORS_master_v3_limpio.csv",
        encoding="utf8",
        on_bad_lines="skip",
        sep=",",
        engine="python"
    )

    # Normalizar nombres de columnas
    df.columns = [c.strip().lower() for c in df.columns]

    # Verificar columnas necesarias
    if "keywords" not in df.columns:
        messagebox.showerror("Error", "No se encontró la columna 'keywords' en el archivo CSV.")
        raise SystemExit

    if "author_name" not in df.columns:
        messagebox.showerror("Error", "No se encontró la columna 'author_name' en el archivo CSV.")
        raise SystemExit

    messagebox.showinfo("Archivo cargado", f"Se cargaron {len(df)} autores del archivo CSV correctamente.")

except Exception as e:
    messagebox.showerror("Error al cargar CSV", f"No se pudo leer el archivo:\n{e}")
    raise SystemExit


# --- Función principal ---
def buscar_autores():
    entrada = entry_palabras.get().strip().lower()
    if not entrada:
        messagebox.showwarning("Aviso", "Por favor ingresa las palabras clave del paper.")
        return

    # Palabras ingresadas separadas por coma
    palabras_paper = [p.strip() for p in entrada.split(";")]

    resultados = []

    for _, fila in df.iterrows():
        # Obtener las keywords del autor (separadas por ;)
        palabras_autor = str(fila["keywords"]).lower().split(";")
        palabras_autor = [p.strip() for p in palabras_autor if p.strip()]

        # Coincidencias exactas
        coincidencias = set(palabras_paper).intersection(palabras_autor)
        score = len(coincidencias)

        if score > 0:
            resultados.append({
                "Nombre": fila["author_name"],
                "Coincidencias": score,
                "Palabras coincidentes": "; ".join(coincidencias)
            })

    # Ordenar resultados por coincidencias (mayor a menor)
    resultados.sort(key=lambda x: x["Coincidencias"], reverse=True)
    top10 = resultados[:10]

    # Limpiar tabla
    for fila in tabla.get_children():
        tabla.delete(fila)

    # Mostrar resultados
    for r in top10:
        tabla.insert("", tk.END, values=(r["Nombre"], r["Coincidencias"], r["Palabras coincidentes"]))

    if not top10:
        messagebox.showinfo("Sin resultados", "No se encontraron coincidencias con esas palabras clave.")


# --- Interfaz gráfica ---
ventana = tk.Tk()
ventana.title("Buscador de Autores por Palabras Clave")
ventana.geometry("950x500")
ventana.resizable(False, False)

# Entrada
tk.Label(ventana, text="Palabras clave del paper (separadas por ;):", font=("Arial", 11)).pack(pady=10)
entry_palabras = tk.Entry(ventana, width=100)
entry_palabras.pack(pady=5)

# Botón de búsqueda
btn_buscar = tk.Button(
    ventana,
    text="Buscar autores",
    command=buscar_autores,
    bg="#0078D7",
    fg="white",
    font=("Arial", 11, "bold")
)
btn_buscar.pack(pady=10)

# Tabla de resultados
frame_tabla = tk.Frame(ventana)
frame_tabla.pack(pady=10)

columnas = ("Nombre", "Coincidencias", "Palabras coincidentes")
tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=10)

for col in columnas:
    tabla.heading(col, text=col)
    tabla.column(col, width=300 if col == "Nombre" else 200, anchor="center")

tabla.pack(side="left")

# Scrollbar
scroll = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
scroll.pack(side="right", fill="y")
tabla.configure(yscroll=scroll.set)

ventana.mainloop()
