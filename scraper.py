"""Extrae los libros publicados en la primera página de Books to Scrape."""

import warnings

import requests
from bs4 import BeautifulSoup


URL = "https://books.toscrape.com/"
CALIFICACIONES = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def extraer_libros(html: str) -> list[dict]:
    """Obtiene título completo, precio, disponibilidad y calificación del HTML.

    Cada registro requiere sus cuatro campos. Si falta alguno o el precio o la
    calificación no se pueden interpretar, se omite ese libro y se emite una
    advertencia; los demás registros continúan procesándose.
    """
    sopa = BeautifulSoup(html, "html.parser")
    libros = []

    for posicion, articulo in enumerate(sopa.select("article.product_pod"), start=1):
        enlace = articulo.select_one("h3 a")
        precio_elemento = articulo.select_one("p.price_color")
        disponibilidad_elemento = articulo.select_one("p.availability")
        calificacion_elemento = articulo.select_one("p.star-rating")

        titulo = enlace.get("title", "").strip() if enlace else ""
        disponibilidad = (
            " ".join(disponibilidad_elemento.get_text(" ", strip=True).split())
            if disponibilidad_elemento
            else ""
        )
        calificacion = next(
            (
                CALIFICACIONES[clase]
                for clase in calificacion_elemento.get("class", [])
                if clase in CALIFICACIONES
            ),
            None,
        ) if calificacion_elemento else None

        if not titulo or not precio_elemento or not disponibilidad or calificacion is None:
            warnings.warn(
                f"Se omitió el libro de la posición {posicion}: faltan campos obligatorios "
                "o la calificación no es reconocible.",
                stacklevel=2,
            )
            continue

        try:
            precio = float(precio_elemento.get_text(strip=True).replace("£", "").strip())
        except ValueError:
            warnings.warn(
                f"Se omitió el libro «{titulo}»: su precio no se puede convertir a número.",
                stacklevel=2,
            )
            continue

        libros.append(
            {
                "titulo": titulo,
                "precio": precio,
                "disponibilidad": disponibilidad,
                "calificacion": calificacion,
            }
        )

    return libros


def obtener_libros() -> list[dict]:
    """Solicita una vez la primera página; los errores HTTP se propagan al usuario."""
    respuesta = requests.get(URL, timeout=10)
    respuesta.raise_for_status()
    # El sitio utiliza UTF-8; declararlo evita interpretar incorrectamente «£».
    respuesta.encoding = "utf-8"
    return extraer_libros(respuesta.text)


if __name__ == "__main__":
    libros = obtener_libros()
    print(f"Total de libros extraídos de la primera página: {len(libros)}")
    print("Primeros cinco libros:")
    for libro in libros[:5]:
        print(libro)
