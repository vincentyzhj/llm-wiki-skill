# LLM Wiki — Habilidad de Grafo de Conocimiento Multimodal

> *«El LLM escribe y mantiene el wiki; los humanos leen y hacen preguntas.»*

![Arquitectura LLM Wiki](../skills/llm-wiki/assets/llm-wiki.svg)

**Otros idiomas:** [English](../README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Français](README.fr.md) | [Русский](README.ru.md)

---

## ¿Qué es esto?

`llm-wiki` es una Skill que funciona dentro de Claude Code que ingiere documentos brutos de cualquier formato (PDF, DOCX, PPTX, XLSX, Markdown, imágenes) en un Wiki estructurado y construye automáticamente un grafo de conocimiento interactivo (`graph.html`).

Implementa la filosofía de gestión del conocimiento propuesta por Karpathy: **el conocimiento se sintetiza en el momento de la ingestión, no en el momento de la consulta**. Cada vez que se agrega un nuevo documento, el LLM extrae automáticamente los puntos clave, establece referencias cruzadas, marca contradicciones y actualiza el resumen de síntesis, permitiendo que la base de conocimiento crezca de forma compuesta con cada ingestión.

La diferencia fundamental con RAG: RAG arroja documentos brutos en un almacén vectorial y ensambla respuestas sobre la marcha en el momento de la consulta; llm-wiki compila el conocimiento en páginas wiki duraderas en el momento de la ingestión, de modo que las consultas leen conclusiones ya sintetizadas.

---

## Estructura de Directorios

```
<wiki-root>/
  raw/                  # Documentos brutos (nunca se modifican)
    <topic>/            # Organizado por tema, subdirectorios de un nivel
  wiki/
    index.md            # Tabla de contenidos de todas las páginas (particionada por tema)
    overview.md         # Síntesis viva de todas las fuentes
    log.md              # Registro de operaciones de solo adición
    sources/            # Página de resumen de cada documento bruto
    entities/           # Personas / empresas / proyectos / productos
    concepts/           # Conceptos / marcos / metodologías
    syntheses/          # Respuestas a consultas archivadas
    archive/            # Páginas obsoletas archivadas
  graph/
    graph.json          # Datos de nodos + aristas
    graph.html          # Visualización autónoma basada en vis.js
```

---

## Referencia de Comandos

| Comando | Propósito |
|---|---|
| `wiki-config workspace <path>` | Establecer la ruta del espacio de trabajo wiki |
| `wiki-config show` | Ver la configuración actual y el estado del directorio |
| `wiki-input <path> [--topic <slug>]` | Ingerir cualquier ruta de archivo (archiva automáticamente en `raw/<topic>/`) |
| `wiki-ingest <file>` | Ingerir un archivo ya en `raw/` |
| `wiki-query: <pregunta>` | Consultar la base de conocimiento, sintetizar respuesta |
| `wiki-lint` | Verificar páginas huérfanas, enlaces rotos, contradicciones |
| `wiki-graph` | Construir el grafo de conocimiento interactivo (`graph.html`) |

**Recomendado para uso diario: `wiki-input`** — acepta rutas locales o remotas, copia automáticamente a `raw/<topic>/` antes de ingerir. No se necesita gestión manual del directorio `raw/`.

---

## Flujo de Trabajo

### Ingestión (Ingest)

Al ingerir un documento, el LLM ejecuta secuencialmente:

1. Extracción de contenido multimodal (PDF/DOCX/PPTX/XLSX/imágenes → Markdown)
2. Escritura de `wiki/sources/<slug>.md` (resumen, puntos clave, citas importantes)
3. Actualización de `wiki/index.md` y `wiki/overview.md`
4. Creación o actualización de páginas `wiki/entities/` y `wiki/concepts/`
5. Marcado de contradicciones con el contenido existente
6. Adición del registro de operaciones a `wiki/log.md`

### Consulta (Query)

Lee `wiki/index.md` para identificar páginas relevantes, sintetiza una respuesta con referencias en línea en formato `[[PageName]]`. Opcionalmente archiva la respuesta como `wiki/syntheses/<slug>.md`.

### Grafo de Conocimiento (Graph)

Extrae wikilinks explícitos (`EXTRACTED`) y asociaciones semánticas inferidas por IA (`INFERRED`, confianza ≥ 0.5) entre páginas, generando un `graph.html` autónomo sin dependencias con coloración por tipo de nodo y agrupación por comunidad.

---

## Formatos Soportados

| Formato | Método de Extracción |
|---|---|
| `.md` `.txt` | Lectura directa |
| `.pdf` | pdfplumber (texto + tablas) |
| `.docx` | python-docx (cuerpo + encabezados + tablas) |
| `.pptx` | python-pptx (títulos + cuerpo + notas) |
| `.xlsx` `.csv` | pandas (convertido a tablas Markdown) |
| `.png` `.jpg` `.jpeg` `.webp` `.gif` `.bmp` | Claude vision (multimodal) |

---

## Soporte Multimodal Detallado

`llm-wiki` utiliza la capacidad multimodal nativa de Claude para comprender el contenido de las imágenes — no solo reconocimiento OCR de texto, sino comprensión semántica completa de diagramas, gráficos y capturas de pantalla.

### Ingestión Directa de Archivos de Imagen

Pase cualquier archivo de imagen directamente a `wiki-input` o `wiki-ingest`. Claude lee la imagen y la convierte a Markdown estructurado antes de ejecutar el flujo de ingestión estándar:

```bash
wiki-input ~/capturas/diagrama-arquitectura.png --topic system-design
wiki-input ~/fotos/sesion-pizarra.jpg --topic meetings
```

**Lo que Claude extrae de las imágenes:**
- **Gráficos & curvas** — series de datos, etiquetas de ejes, tendencias, valores numéricos
- **Diagramas & organigramas** — nodos, aristas, relaciones, dirección del flujo
- **Capturas de pantalla** — estructura UI, texto visible, contexto del diseño
- **Notas manuscritas / pizarras** — texto transcrito y estructuras dibujadas
- **Tablas en imágenes** — reconstruidas como tablas Markdown
- **Contenido mixto** — documentos fotografiados o escaneados con texto y figuras

### Imágenes Integradas en Documentos

Al ingerir archivos PDF, DOCX o PPTX que contienen imágenes integradas, la herramienta de extracción correspondiente captura todo el contenido textual. Para figuras y diagramas críticos para la comprensión que la extracción de texto sola no cubre suficientemente, vuélvalos a ingerir como archivos de imagen independientes.

### Formatos de Imagen Soportados

| Formato | Notas |
|---|---|
| `.png` | Sin pérdida; ideal para capturas de pantalla, diagramas |
| `.jpg` / `.jpeg` | Fotos, documentos escaneados |
| `.webp` | Imágenes optimizadas para web |
| `.gif` | Se analiza el primer fotograma (contenido estático) |
| `.bmp` | Mapa de bits sin comprimir |

### Pipeline de Extracción Multimodal

Todo el contenido de imagen sigue el mismo pipeline de ingestión que los documentos de texto — la imagen simplemente se convierte a Markdown primero:

```
Archivo de Imagen
    │
    ▼
Claude Vision (herramienta Read)
    │  Extrae: texto, estructura, datos, relaciones
    ▼
Descripción Markdown
    │
    ▼
Flujo de Ingestión Estándar (Pasos 2–10)
    │  sources/ entities/ concepts/ index/ overview/ log/
    ▼
Páginas Wiki + Grafo de Conocimiento
```

---

## Inicio Rápido

```bash
# 1. Establecer el espacio de trabajo wiki
wiki-config workspace ~/my-wiki

# 2. Ingerir el primer documento
wiki-input ~/Downloads/paper.pdf --topic papers

# 3. Consulta
wiki-query: ¿Cuál es la contribución principal de este artículo?

# 4. Construir el grafo de conocimiento
wiki-graph
```

---

## Referencias

- [Anthropic Skills — Repositorio oficial de habilidades](https://github.com/anthropics/skills)
- [Andrej Karpathy — LLM Wiki concept](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [SamurAIGPT — llm-wiki-agent](https://github.com/SamurAIGPT/llm-wiki-agent)
