import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Cargar y preparar documentos
libros = pd.read_csv("libros.csv")
libros = libros.dropna(subset=["titulo_normalizado"]).copy()
libros["titulo_normalizado"] = libros["titulo_normalizado"].astype(str).str.strip()
libros = libros[libros["titulo_normalizado"] != ""].reset_index(drop=True)

if libros.empty:
    raise SystemExit("No hay titulos validos en libros.csv. Ejecute primero python procesamiento.py")

# Construir el indice (una sola vez)
vectorizador = TfidfVectorizer()
matriz_tfidf = vectorizador.fit_transform(libros["titulo_normalizado"])


def buscar(consulta: str, top_k: int = 5):
    consulta = consulta.strip().lower()
    if not consulta:
        print("La consulta está vacía. Se requiere al menos una palabra.")
        return []

    # Transformar la consulta usando el vocabulario aprendido
    vector_consulta = vectorizador.transform([consulta])
    puntuaciones = cosine_similarity(vector_consulta, matriz_tfidf).ravel()
    # Orden de mayor a menor; en empates se respeta el orden del CSV
    indices = (-puntuaciones).argsort(kind="stable")

    resultados = []
    for i in indices:
        if puntuaciones[i] <= 0:
            break
        resultados.append({
            "titulo": libros.iloc[i]["titulo"],
            "precio": libros.iloc[i]["precio"],
            "similitud": float(puntuaciones[i])
        })
        if len(resultados) >= top_k:
            break
    return resultados


if __name__ == "__main__":
    consulta = input("Ingrese una palabra o titulo: ")
    resultados = buscar(consulta, top_k=3)

    if consulta.strip() and not resultados:
        print("No se encontraron libros con coincidencias para la consulta.")

    for posicion, r in enumerate(resultados, start=1):
        print(f"{posicion}. {r['titulo']}")
        print(f"   Precio: GBP {r['precio']:.2f} | Similitud: {r['similitud']:.4f}")
