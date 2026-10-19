"""Limpia los libros extraídos y exporta un conjunto de datos reproducible."""

import math
from pathlib import Path
import warnings

import pandas as pd

from scraper import obtener_libros


RUTA_CSV = Path(__file__).resolve().parent / "libros.csv"
COLUMNAS = ["titulo", "precio", "disponibilidad", "calificacion"]


def procesar_libros(libros: list[dict]) -> pd.DataFrame:
    """Limpia textos, valida tipos y elimina duplicados por título normalizado.

    Se omiten con una advertencia las filas sin título o disponibilidad, con
    precio no finito o negativo, o con una calificación que no sea un entero
    entre 1 y 5. Ante títulos repetidos, se conserva la primera fila válida.
    """
    df = pd.DataFrame(libros, columns=COLUMNAS)

    for columna in ["titulo", "disponibilidad"]:
        df[columna] = df[columna].fillna("").astype(str).str.replace(r"\s+", " ", regex=True).str.strip()

    df["titulo_normalizado"] = df["titulo"].str.lower()
    df["precio"] = pd.to_numeric(df["precio"], errors="coerce")
    df["calificacion"] = pd.to_numeric(df["calificacion"], errors="coerce")

    filas_validas = (
        df["titulo"].ne("")
        & df["disponibilidad"].ne("")
        & df["precio"].map(math.isfinite)
        & df["precio"].ge(0)
        & df["calificacion"].between(1, 5)
        & df["calificacion"].mod(1).eq(0)
    )
    descartados = int((~filas_validas).sum())
    if descartados:
        warnings.warn(
            f"Se omitieron {descartados} registros con campos vacíos o valores numéricos inválidos.",
            stacklevel=2,
        )

    df = df.loc[filas_validas].copy()
    df = df.drop_duplicates(subset="titulo_normalizado", keep="first").reset_index(drop=True)
    df["precio"] = df["precio"].astype(float)
    df["calificacion"] = df["calificacion"].astype(int)
    return df


def main() -> None:
    """Realiza una extracción, muestra su resumen y guarda el CSV en esta carpeta."""
    libros = obtener_libros()
    df = procesar_libros(libros)

    print("Primeras cinco filas:")
    print(df.head())
    print("\nInformación de las columnas:")
    df.info()
    print(f"\nDimensiones del conjunto de datos: {df.shape}")
    print(f"Columnas: {df.columns.tolist()}")
    print(f"Total de libros después de la limpieza: {len(df)}")
    if not df.empty:
        print(f"Precio promedio: £{df['precio'].mean():.2f}")
    else:
        print("Precio promedio: no hay libros válidos para calcularlo.")

    df.to_csv(RUTA_CSV, index=False, encoding="utf-8")
    print(f"Archivo CSV guardado en: {RUTA_CSV}")


if __name__ == "__main__":
    main()
