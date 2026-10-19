"""Búsqueda de libros mediante TF-IDF y similitud coseno."""

from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


RUTA_CSV = Path(__file__).resolve().with_name("libros.csv")
MAX_RESULTADOS = 5


class ErrorIndice(ValueError):
    """Indica que no fue posible construir el índice de libros."""


class IndiceLibros:
    """Carga el corpus y calcula su matriz TF-IDF una sola vez."""

    def __init__(self, ruta_csv: str | Path = RUTA_CSV) -> None:
        ruta_csv = Path(ruta_csv)
        try:
            libros = pd.read_csv(ruta_csv)
        except FileNotFoundError as error:
            raise ErrorIndice(
                f"No se encontró {ruta_csv.name}. Se debe ejecutar python procesamiento.py "
                "para generar el archivo de libros."
            ) from error
        except (OSError, UnicodeError, pd.errors.ParserError, pd.errors.EmptyDataError) as error:
            raise ErrorIndice(f"No se pudo leer el archivo CSV: {error}") from error

        columnas = {"titulo", "precio", "titulo_normalizado"}
        faltantes = columnas.difference(libros.columns)
        if faltantes:
            raise ErrorIndice(
                "El CSV no contiene las columnas obligatorias: "
                + ", ".join(sorted(faltantes))
                + "."
            )

        # Los documentos sin texto útil no deben formar parte del índice.
        libros = libros.dropna(subset=["titulo_normalizado"]).copy()
        libros["titulo_normalizado"] = libros["titulo_normalizado"].astype(str).str.strip()
        libros = libros.loc[libros["titulo_normalizado"].ne("")].reset_index(drop=True)
        if libros.empty:
            raise ErrorIndice("El CSV no contiene títulos normalizados válidos para indexar.")

        libros["precio"] = pd.to_numeric(libros["precio"], errors="coerce")
        if libros["precio"].isna().any():
            raise ErrorIndice("La columna precio contiene valores vacíos o no numéricos.")

        self.libros = libros
        self.vectorizador = TfidfVectorizer()
        try:
            self.matriz_tfidf = self.vectorizador.fit_transform(
                self.libros["titulo_normalizado"]
            )
        except ValueError as error:
            raise ErrorIndice(
                "Los títulos normalizados no contienen palabras válidas "
                "para construir el vocabulario TF-IDF."
            ) from error

    def buscar(self, consulta: str, top_k: int = MAX_RESULTADOS) -> list[dict]:
        """Devuelve hasta cinco libros con similitud positiva, en orden descendente."""
        consulta = consulta.strip().lower()
        if not consulta:
            return []
        if not isinstance(top_k, int) or top_k < 1:
            raise ValueError("La cantidad de resultados debe ser un entero positivo.")

        # La consulta utiliza el vocabulario aprendido del corpus, sin reajustarlo.
        vector_consulta = self.vectorizador.transform([consulta])
        similitudes = cosine_similarity(vector_consulta, self.matriz_tfidf).ravel()
        orden = (-similitudes).argsort(kind="stable")
        resultados = []

        for posicion in orden:
            similitud = float(similitudes[posicion])
            if similitud <= 0:
                break
            libro = self.libros.iloc[posicion]
            resultados.append(
                {
                    "titulo": str(libro["titulo"]),
                    "precio": float(libro["precio"]),
                    "similitud": similitud,
                }
            )
            if len(resultados) >= min(top_k, MAX_RESULTADOS):
                break

        return resultados


_indice: IndiceLibros | None = None


def cargar_indice(ruta_csv: str | Path | None = None) -> IndiceLibros:
    """Carga un CSV y conserva su índice para las siguientes consultas."""
    global _indice
    _indice = IndiceLibros(RUTA_CSV if ruta_csv is None else ruta_csv)
    return _indice


def buscar(consulta: str, top_k: int = MAX_RESULTADOS) -> list[dict]:
    """Busca en el índice compartido; lo construye en la primera consulta válida."""
    if not consulta.strip():
        print("La consulta está vacía. Se requiere al menos una palabra.")
        return []
    indice = _indice if _indice is not None else cargar_indice()
    return indice.buscar(consulta, top_k=top_k)


def main() -> int:
    """Solicita una consulta y muestra los tres mejores resultados positivos."""
    try:
        consulta = input("Consulta (palabra o frase): ")
        resultados = buscar(consulta, top_k=3)
    except (EOFError, KeyboardInterrupt):
        print("\nNo se recibió una consulta.")
        return 0
    except ErrorIndice as error:
        print(f"Error: {error}")
        return 1

    if not consulta.strip():
        return 0
    if not resultados:
        print("No se encontraron libros con coincidencias para la consulta.")
        return 0

    for posicion, resultado in enumerate(resultados, start=1):
        print(f"{posicion}. {resultado['titulo']}")
        print(
            f"   Precio: GBP {resultado['precio']:.2f} | "
            f"Similitud: {resultado['similitud']:.4f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
