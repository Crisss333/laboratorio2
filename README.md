# Laboratorio 2: Web Scraping, procesamiento y recuperación de información

**Asignatura:** Ingeniería Web Avanzada, OII436-1.

**Integrantes:** Cristopher Dauros, Carlos Ruz.

**Repositorio:** [Crisss333/laboratorio2](https://github.com/Crisss333/laboratorio2).

**Fecha de verificación:** 19 de octubre de 2026.

Se desarrolló una solución local en Python para extraer los libros de la primera
página de [Books to Scrape](https://books.toscrape.com/), procesarlos con Pandas
y recuperar títulos mediante TF-IDF y similitud del coseno. Se trabajó únicamente
con `https://books.toscrape.com/`: no se recorrieron páginas siguientes ni fichas
individuales. Los datos del CSV se generaron mediante `procesamiento.py`; no se
copiaron manualmente desde la página.

## 1. Archivos de la entrega

| Archivo | Función |
| --- | --- |
| `scraper.py` | Se solicita la primera página y se extraen los cuatro campos de cada libro. |
| `procesamiento.py` | Se limpian y validan los registros, se calculan indicadores y se exporta el CSV. |
| `buscador.py` | Se construye el índice TF-IDF y se ordenan las coincidencias positivas. |
| `libros.csv` | Se conserva el conjunto de datos real, limpio y codificado en UTF-8. |
| `requirements.txt` | Se registran las versiones instaladas mediante `python -m pip freeze`. |
| `README.md` | Se documentan la reproducción, las decisiones, las respuestas y las evidencias. |
| `.gitignore` | Se excluyen el entorno virtual, las cachés y los archivos temporales o sensibles. |

El directorio `.venv/` se mantiene únicamente en el equipo local y no forma parte
de los archivos versionados.

## 2. Entorno virtual y reproducción

Se trabajó con **Python 3.12.14**. Para reproducir las versiones fijadas se debe
disponer de Python 3.12. En macOS/Linux se muestra el ejecutable `python3.12`;
si la instalación utiliza otro nombre, se debe comprobar que corresponda a esa
versión antes de crear el entorno. No se requieren credenciales para la fuente.

### 2.1. Obtención del repositorio

Se descarga el repositorio y se accede a su carpeta:

```bash
git clone https://github.com/Crisss333/laboratorio2.git
cd laboratorio2
```

### 2.2. Creación y activación en macOS/Linux

Se verifica el intérprete, se crea el entorno y se activa:

```bash
python3.12 --version
python3.12 -m venv .venv
source .venv/bin/activate
```

Si el entorno local ya existe, se requiere únicamente la activación:

```bash
source .venv/bin/activate
```

### 2.3. Creación y activación en Windows

En PowerShell se ejecuta:

```powershell
py -3.12 --version
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

En CMD se utiliza el mismo comando de creación y la siguiente activación:

```bat
.venv\Scripts\activate.bat
```

### 2.4. Verificación e instalación

Una vez activado el entorno, se comprueba la ruta del intérprete y que no se esté
utilizando el entorno base. La primera salida debe apuntar a `.venv` y la segunda
debe ser `True`:

```bash
python -c "import sys; print(sys.executable); print(sys.prefix != sys.base_prefix)"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check
```

Se comprobó que el intérprete local pertenecía a `.venv`. Además, se instaló
`requirements.txt` en un segundo entorno temporal nuevo: `pip check` no detectó
dependencias incompatibles y la consulta `life` devolvió tres resultados.

Durante la preparación inicial se instalaron las bibliotecas exigidas y se generó
el archivo de dependencias con estos comandos:

```bash
python -m pip install requests beautifulsoup4 pandas scikit-learn
python -m pip freeze > requirements.txt
```

Se verificó la exclusión del entorno mediante:

```bash
git check-ignore -v .venv/
```

Se obtuvo la regla `.gitignore:1:.venv/`. El entorno quedó excluido del seguimiento.

### 2.5. Orden de ejecución

Desde la carpeta del repositorio, con el entorno activado, se ejecuta:

```bash
python scraper.py
python procesamiento.py
python buscador.py
```

1. Con `scraper.py` se muestra el total extraído y los primeros cinco registros.
2. Con `procesamiento.py` se realiza una extracción, se muestran `head()`,
   `info()`, `shape` y las columnas, y se genera `libros.csv` junto al script.
3. Con `buscador.py` se ingresa una consulta y se muestran hasta tres resultados
   con título, precio en GBP y similitud.

Los dos primeros comandos solicitan una vez la misma primera página cada uno.
La importación de `scraper`, `procesamiento` o `buscador` no realiza solicitudes
ni solicita entrada: la ejecución se protege con `if __name__ == "__main__":`.
Las búsquedas utilizan el CSV y no vuelven a consultar el sitio. Si solo se desea
regenerar el conjunto de datos, basta con ejecutar `python procesamiento.py`.

Para terminar la sesión del entorno se ejecuta:

```bash
deactivate
```

## 3. Extracción y decisiones de procesamiento

Se inspeccionó el HTML de la primera página en el navegador. Se identificaron
**20 elementos** `article.product_pod` y los siguientes selectores:

| Dato | Selector o atributo | Tratamiento |
| --- | --- | --- |
| Libro | `article.product_pod` | Se procesa cada ficha de la primera página. |
| Título | `h3 a`, atributo `title` | Se conserva el título completo, ya que el texto visible puede estar abreviado. |
| Precio | `p.price_color` | Se elimina `£` y se convierte a `float`. |
| Disponibilidad | `p.availability` | Se compactan saltos de línea y espacios; se conserva el texto de la fuente. |
| Calificación | `p.star-rating`, clases `One` a `Five` | Se transforma a un entero de 1 a 5. |

Se utilizó `requests.get(URL, timeout=10)` y `raise_for_status()` para comprobar
la respuesta HTTP. Se interpretó el HTML como UTF-8 para conservar correctamente
el símbolo de libra. No se incorporaron credenciales ni mecanismos para eludir
restricciones. No se implementaron paginación ni reintentos masivos.

La función `obtener_libros()` devuelve una lista de diccionarios con las claves
`titulo`, `precio`, `disponibilidad` y `calificacion`. Ante un libro sin un campo
obligatorio o con un precio/calificación no interpretable, se emite una advertencia
y se omite ese elemento; los restantes continúan procesándose. Un error de
conexión o HTTP se propaga y no se presenta como una extracción exitosa.

Se construyó el DataFrame con los registros extraídos. Se compactaron los espacios,
se creó `titulo_normalizado` en minúsculas y se eliminaron duplicados por ese título
normalizado, conservando la primera fila válida. También se validaron precios
numéricos finitos y no negativos y calificaciones enteras entre 1 y 5. Se conservaron
los títulos originales para su presentación.

Se exportó el resultado con `index=False` y `encoding="utf-8"`. Se incorporaron
cinco columnas: las cuatro originales y `titulo_normalizado`. Los títulos y la
disponibilidad permanecen en el idioma de la fuente; no se tradujeron los datos.

## 4. Evidencias de extracción y procesamiento

Se obtuvieron los siguientes resultados reales:

| Indicador | Resultado |
| --- | --- |
| Libros extraídos de la primera página | 20 |
| Libros conservados después de la limpieza | 20 |
| Filas eliminadas durante esta extracción | 0 |
| Dimensiones del DataFrame | `(20, 5)` |
| Valores nulos | 0 en las cinco columnas |
| Tipo de `precio` | `float64` |
| Tipo de `calificacion` | `int64` |
| Precio promedio sin redondear a dos decimales | GBP 38.0485 |
| Precio promedio presentado | **GBP 38.05** |

Se registraron los primeros cinco libros extraídos:

| Título | Precio (GBP) | Disponibilidad | Calificación |
| --- | ---: | --- | ---: |
| A Light in the Attic | 51.77 | In stock | 3 |
| Tipping the Velvet | 53.74 | In stock | 1 |
| Soumission | 50.10 | In stock | 1 |
| Sharp Objects | 47.82 | In stock | 4 |
| Sapiens: A Brief History of Humankind | 54.23 | In stock | 5 |

El promedio corresponde únicamente a los 20 libros de la primera página; no se
interpreta como una estadística del catálogo completo.

## 5. Índice TF-IDF y dos búsquedas reales

Se cargó `libros.csv` y se excluyeron los títulos normalizados nulos o vacíos antes
de indexar. Se construyó una matriz con `TfidfVectorizer().fit_transform()` y se
conservó el vectorizador para representar las consultas mediante `transform()`.
Se calculó `cosine_similarity`, se ordenaron las puntuaciones de mayor a menor y
se descartaron las iguales a cero. Los empates conservan el orden del CSV.

La función `buscar(consulta, top_k=5)` admite hasta cinco resultados. Para realizar
el desafío se dejó la llamada de consola como **`buscar(consulta, top_k=3)`**.
El índice se construye en la primera consulta válida y se reutiliza mientras
permanece cargado el módulo. Las consultas se procesan con `strip().lower()`.

Se eligieron `the` y `life`, palabras comprobadas en los títulos extraídos. Se
obtuvieron los siguientes resultados al ejecutar `python buscador.py`:

### 5.1. Consulta `the`

| Orden | Título | Precio (GBP) | Similitud |
| --- | --- | ---: | ---: |
| 1 | The Coming Woman: A Novel Based on the Life of the Infamous Feminist, Victoria Woodhull | 17.93 | 0.4181 |
| 2 | The Boys in the Boat: Nine Americans and Their Epic Quest for Gold at the 1936 Berlin Olympics | 22.60 | 0.3630 |
| 3 | Tipping the Velvet | 53.74 | 0.3282 |

### 5.2. Consulta `life`

| Orden | Título | Precio (GBP) | Similitud |
| --- | --- | ---: | ---: |
| 1 | Scott Pilgrim's Precious Little Life (Scott Pilgrim #1) | 52.29 | 0.2459 |
| 2 | The Coming Woman: A Novel Based on the Life of the Infamous Feminist, Victoria Woodhull | 17.93 | 0.2250 |
| 3 | Our Band Could Be Your Life: Scenes from the American Indie Underground, 1981-1991 | 57.25 | 0.2231 |

Se observó un orden descendente y puntuaciones positivas en ambas búsquedas. Con
`the` se priorizó el primer título por su representación TF-IDF; con `life` se
recuperó primero el título de Scott Pilgrim. El orden depende de los términos y
sus pesos dentro de los títulos completos, no del precio ni de la calificación.
La similitud refleja coincidencia léxica, no comprensión del significado.

### 5.3. Comprobación del desafío

Se ejecutó la comparación siguiente con el mismo índice y la misma consulta:

```bash
python -c "from buscador import buscar; print(len(buscar('the'))); print(len(buscar('the', top_k=3)))"
```

Se obtuvieron **5** resultados con el límite predeterminado y **3** con
`top_k=3`. Se comprobó que los tres conservados tenían similitud positiva y
coincidían con los tres primeros del ranking predeterminado.

## 6. Pruebas funcionales T1-T4

Se ejecutó `python buscador.py` desde la terminal con el entorno activado para
cada caso. Se ingresó la consulta indicada; para T4 se presionó Enter sin texto.

| Caso | Consulta utilizada | Resultado observado | Estado |
| --- | --- | --- | --- |
| T1 | `the` | Se obtuvieron tres coincidencias positivas en orden: The Coming Woman (0.4181), The Boys in the Boat (0.3630) y Tipping the Velvet (0.3282). | **Cumple** |
| T2 | `zzxyz123` | Se mostró «No se encontraron libros con coincidencias para la consulta» y no se devolvieron libros. | **Cumple** |
| T3 | `THE` | Se obtuvo exactamente el mismo orden, títulos, precios y puntuaciones que en T1; solo se cambiaron las mayúsculas de la entrada. | **Cumple** |
| T4 | Vacía | Se mostró «La consulta está vacía. Se requiere al menos una palabra», sin excepción ni resultados. | **Cumple** |

No se detectaron incumplimientos en esos cuatro casos. Las ejecuciones de consola
finalizaron con código de salida 0. Además, se verificaron la importación sin
solicitudes ni entrada automática, la limpieza y deduplicación, los tipos de los
20 registros, el orden de similitudes y la omisión de un libro con precio faltante
sin interrumpir el procesamiento de los otros 19. Se comprobó también el error
informativo ante un corpus sin títulos válidos.

## 7. Respuestas a las preguntas 1-6

### Pregunta 1. ¿Para qué sirve BeautifulSoup y cómo se diferencia de requests?

BeautifulSoup analiza el HTML y permite localizar elementos, atributos y textos
dentro de su estructura. Por su parte, `requests` realiza la solicitud HTTP y
obtiene la respuesta del servidor. En el laboratorio se utilizó `requests` para
descargar la página y BeautifulSoup para extraer los campos de sus libros.

### Pregunta 2. ¿Qué riesgo existe al depender de selectores HTML específicos si el sitio cambia?

Los selectores dependen de etiquetas, clases y jerarquías concretas. Si cambia la
estructura del sitio, pueden dejar de encontrar elementos o extraer información
incorrecta. Por ello, se validaron los campos y se emitieron advertencias ante
registros incompletos, en lugar de asumir que toda extracción era correcta.

### Pregunta 3. ¿Por qué normalizar los títulos antes de implementar la búsqueda?

La normalización reduce diferencias de mayúsculas y espacios que no cambian la
identidad del título. Se creó una columna consistente para los documentos y se
normalizaron también las consultas. Esto facilita las coincidencias y permite
que `the` y `THE` produzcan el mismo ranking.

### Pregunta 4. ¿Qué función cumple fit_transform() sobre los títulos y por qué se usa transform() para la consulta?

`fit_transform()` aprende el vocabulario y los pesos IDF de la colección y
construye la matriz TF-IDF de los títulos. La consulta se representa con
`transform()` para utilizar exactamente el vocabulario y los pesos aprendidos,
sin reajustar el índice. Así, los vectores de la consulta y de los documentos
pertenecen al mismo espacio y pueden compararse mediante el coseno.

### Pregunta 5. Si dos libros obtienen similitudes de 0.75 y 0.20 para la misma consulta, ¿cuál se muestra primero y qué indica una puntuación cercana a cero?

Se muestra primero el libro con **0.75**, porque el ranking se ordena de mayor a
menor similitud. Una puntuación cercana a cero indica poca coincidencia entre
las representaciones vectoriales. En esta configuración TF-IDF no negativa, una
puntuación de cero indica que no se comparten términos del vocabulario; no
significa que se haya evaluado la relación semántica entre los textos.

### Pregunta 6. ¿Qué limitación tiene buscar solo por palabras presentes en títulos mediante TF-IDF y qué mejora concreta se propone?

La recuperación depende de coincidencias léxicas y únicamente considera el texto
del título. Puede omitir libros relacionados cuando la consulta utiliza un sinónimo
o una palabra que no aparece allí. Se propone incorporar un diccionario de
sinónimos para expandir la consulta antes de aplicar `transform()`, conservando
el mismo vocabulario del índice. La mejora se plantea como trabajo posterior y
no se presenta como una función implementada en esta entrega.

## 8. Alcance y comprobación de la entrega

Se mantuvo el alcance solicitado: primera página, procesamiento local y búsqueda
de títulos. Los precios se expresan en GBP y los datos versionados corresponden
a la extracción realizada; una ejecución posterior puede reflejar cambios de la
fuente. Los resultados no se interpretan como una búsqueda de todo el catálogo.

Se excluyeron `.venv/`, `__pycache__/`, archivos compilados, temporales y posibles
archivos de configuración sensibles. Se versionaron únicamente los siete archivos
indicados en la sección 1. La copia HTML utilizada para comprobaciones de
contingencia se mantuvo fuera del repositorio y no reemplazó la extracción remota
que generó `libros.csv`.

Se tomó como especificación el enunciado docente `laboratorio2.pdf`, en especial
los pasos 0-14 y sus seis preguntas. El uso de TF-IDF y coseno corresponde al
material de apoyo proporcionado en ese enunciado.
