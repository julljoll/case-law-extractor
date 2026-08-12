# 🏛️ Canonical Directives: Case Law Extractor powered by sha256.us

> **Status:** Top-Level Canonical Specification (`.agents/AGENTS.md`)  
> **Scope:** Multi-Agent Governance, Role Specifications, Architecture Standards & LegalTech Excellence Guidelines  
> **Target Environment:** Python 3.11+, Playwright Chromium, SQLite3, ReportLab, Pandas, Podman, GitHub Actions  
> **Engine Version:** v2.0 — Playwright Headless (2026-08)

---

## 📌 Visión General del Documento Canónico

Este documento establece la guía directiva oficial de nivel canónico para el desarrollo, mantenimiento, evolución y aseguramiento de calidad del proyecto **Case Law Extractor powered by sha256.us**. Define los roles multidisciplinarios, los estándares de codificación, las habilidades requeridas, las reglas de QA y las directivas de arquitectura que cualquier agente de IA o desarrollador debe cumplir de forma estricta.

> **v2.0 Breaking Change:** El motor de scraping migró de `requests + BeautifulSoup` estático a **Playwright Chromium headless** para superar las restricciones del portal Liferay del TSJ Venezuela. La API pública del TSJ no existe como REST endpoint libre — todos los datos se sirven vía XHR JavaScript dentro del navegador. Solo Playwright puede interceptar esas respuestas de forma confiable.

---

## 👥 Matriz de Roles y Habilidades Canónicas (Skills Framework)

### 1. 🏛️ Arquitecto de Software & LegalTech (LegalTech System Architect)
- **Responsabilidad:** Diseñar la arquitectura del sistema end-to-end, asegurando resiliencia, tolerancia a fallos en Playwright y escalabilidad en el almacenamiento relacional.
- **Habilidades Clave:**
  - Diseño de sistemas de scraping headless con **Playwright Chromium** (navegación 3 pasos: carga → sala → año), interceptación de respuestas XHR (`page.on("response", callback)`) y parsers tri-modal (JSON → HTML → DOM).
  - Modelado de base de datos relacional idempotente en SQLite (`ON CONFLICT DO UPDATE`) con indexación estratégica por `link_directo`, `sala`, `expediente` y `ano`.
  - Desacoplamiento de componentes: `BuscadorTSJExcel`, `TSJDatabaseManager`, `PasoAPasoScraper`, `utils`, `scheduler`.
  - Containerización con **Podman** (`Containerfile`, `podman-compose.yml`) para despliegue multi-plataforma.
- **Directivas Técnicas:**
  - Ninguna operación de base de datos debe causar duplicidad de registros.
  - El scraper Playwright debe cerrar el browser en el bloque `finally` para evitar procesos zombie.
  - Toda llamada de red debe incluir `ignore_https_errors=True` y manejo de timeout `networkidle`.

---

### 2. 🤖 Arquitecto de IA, NLP & Clasificación Inteligente (AI & Data Intelligence Architect)
- **Responsabilidad:** Implementar algoritmos de extracción de entidades (NER), minería de texto y clasificación semántica de jurisprudencia.
- **Habilidades Clave:**
  - Filtrado semántico avanzado mediante términos clave de **Evidencia Digital, Delitos Informáticos, Ciberseguridad y Cadena de Custodia**.
  - Normalización y limpieza profunda de texto: `clean_text()`, eliminación de caracteres no imprimibles, corrección de codificación `utf-8` / `latin-1` / `apparent_encoding`.
  - Preparación de datos para integración con modelos LLM y RAG (Retrieval-Augmented Generation) para análisis de la *Ratio Decidendi*.
  - Parser JSON normalizado `_normalize_json_item()` que mapea campos Liferay WS (`SNUMEROSENTENCIA`, `SLINKDIRECTO`, `STEMA`) a schema canónico.
- **Directivas Técnicas:**
  - La clasificación de jurisprudencia tecnológica debe ser extensible vía listas configurables (`TECH_KEYWORDS`).
  - Mantener trazabilidad del extracto vs. el cuerpo completo de la decisión.

---

### 3. 📊 Especialista en Data Analysis & Analytics (Data Scientist & Analyst)
- **Responsabilidad:** Extraer insights jurídicos, generar matrices analíticas estructuradas y asegurar la integridad estadística de la base de datos.
- **Habilidades Clave:**
  - Procesamiento analítico con `pandas` y generación de archivos Excel avanzados con `openpyxl`.
  - Agregación y reporte de métricas por Sala, año cronológico (2019-2026), materia y volumen de sentencias.
  - Auditoría de completitud de datos (detección de valores nulos o campos por defecto como `S/N` o `S/E`).
  - Exportación 1:1 por Sala: `sala_<nombre>.db` + `sala_<nombre>.xlsx` (7 pares canónicos).
- **Directivas Técnicas:**
  - Las exportaciones a Excel deben incluir formato de celdas automático, encabezados DC3 visuales y anchos ajustados dinámicamente.
  - Proveer funciones de consulta de estadísticas rápidas (`--stats`).

---

### 4. 🧪 Especialista en QA & Testing (Quality Assurance & Test Automation Engineer)
- **Responsabilidad:** Garantizar la estabilidad del software mediante suites de pruebas automatizadas y validación continua de regresiones.
- **Habilidades Clave:**
  - Pruebas unitarias e integrales (`unittest`, `pytest`) sobre cada módulo del sistema (`tests/test_extractor.py`).
  - Mocking de respuestas Playwright: simular `page.on("response")` con fixtures de HTML/JSON del portal TSJ.
  - Verificación de la integridad de PDFs generados y consistencia de esquemas SQLite.
  - Validar que el `progress_callback` del worker Playwright actualiza correctamente `sync_progress` dict.
- **Directivas Técnicas:**
  - Prohibido marcar una tarea como completada sin ejecutar la suite de pruebas y validar su éxito con cero errores.
  - Ante fallos de scraping, auditar primero la estructura HTML del DOM de la página del TSJ antes de modificar lógica de negocio.
  - Test de smoke: `from src.buscador_tsj_excel import BuscadorTSJExcel; BuscadorTSJExcel()._get_playwright_scraper() is not None`.

---

### 5. 🎨 Diseñador UX/UI Especialista & Frontend Documental (UX/UI & Document Design Specialist)
- **Responsabilidad:** Maximizar la usabilidad, legibilidad y belleza visual tanto en consola CLI como en documentos impresos PDF y archivos Markdown.
- **Habilidades Clave:**
  - Maquetación de PDFs con fidelidad a estándares oficiales del TSJ utilizando `reportlab` (membrete institucional, encabezados, tablas estilizadas, fuentes legibles).
  - Experiencia de usuario en CLI mediante retroalimentación visual (`colorama`), barras de progreso (`tqdm`) y menús formateados.
  - **Sistema de Diseño DC3 (Department of Defense Cyber Crime Center):** Todas las interfaces creadas (CLI en consola, scripts `.bat`, GUIs web, reportes PDF y artefactos visuales) deben adoptar el estilo visual institucional de **DC3 Cyber Center**:
    - **Fondo & Encabezados:** Azul Marino Profundo Táctico (`#061830` / `#0A192F`).
    - **Accentos & Botones:** Oro Ciber Táctico / Amarillo militar (`#FFC809` / `#FFCC00`).
    - **Bordes & Selecciones:** Azul Acero Ciber (`#0066CC` / `#1E88E5`).
    - **Contenedores & Tarjetas:** Tarjetas Blancas/Flotantes (`#FFFFFF` con bordes `#E2E8F0` y sombras) o tarjetas de consola nítidas.
    - **Badges Capsulares:** Cápsulas ovaladas con texto dorado (`[ DC3 CYBER FORENSICS LAB ]`).
    - **Diagramación SVG Imprimible & SEO (Formato Folio Vertical):** Todos los diagramas `.svg` generados deben construirse estrictamente en **orientación vertical (portrait)** con proporciones de **Hoja Folio / Legal (`viewBox="0 0 900 1350"`)**. **Además, el fondo de estos SVG debe ser blanco** mientras se mantiene el resto de la paleta y estilos del DC3 Design System.
    - **Optimización SEO & Accesibilidad Estándar:** Cada gráfico SVG e interfaz web debe incluir metadatos semánticos SEO completos (`role="img"`, `aria-labelledby`, etiquetas `<title>`, `<desc>` y bloque `<metadata>` con Schema.org/Dublin Core), garantizando la indexabilidad por motores de búsqueda y la accesibilidad para lectores de pantalla.
- **Directivas Técnicas:**
  - Evitar interfaces genéricas o desordenadas; priorizar la estética visual oficial de **DC3 Federal Cyber Center**.
  - Los archivos PDF, interfaces de terminal CLI, ejecutables `.bat`, GUIs y diagramas SVG deben aplicar rigurosamente la paleta de DC3, límites sin desbordamiento de texto y metadatos SEO.

---

### 6. 💻 Programador Full-Stack / Backend Experto (Senior Full-Stack & Systems Engineer)
- **Responsabilidad:** Escribir código Python modular, eficiente, seguro y portable para ambientes Windows, Linux y macOS (y Podman containers).
- **Habilidades Clave:**
  - Programación orientada a objetos en Python 3.11+ con manejo riguroso de excepciones y tipado estático (`typing`).
  - Automatización de entornos en Windows (`.bat`, scripts de instalación y ejecutable directo).
  - Containerización con **Podman**: `Containerfile` (multi-stage), `podman-compose.yml` con volúmenes persistentes para `data/`.
  - Control de versiones avanzado en Git y flujos CI/CD en GitHub Actions.
- **Directivas Técnicas:**
  - Seguir principios PEP 8 de legibilidad de código.
  - Documentar funciones con docstrings claros en español e inglés técnico.
  - El `Containerfile` debe instalar `playwright install chromium --with-deps` y exponer el puerto `8050`.

---

### 7. ⚖️ Especialista en Derecho Procesal & Jurisprudencia (Legal Domain Consultant)
- **Responsabilidad:** Garantizar la precisión técnica y procedimental en la clasificación y captura de sentencias.
- **Habilidades Clave:**
  - Conocimiento profundo de la estructura orgánica del TSJ de Venezuela (Salas: Constitucional, Político-Administrativa, Casación Civil, Casación Penal, Casación Social, Electoral, Plena).
  - Identificación clara de Expedientes, Sentencias, Autos, Ponentes y materias sustantivas/procesales.
  - Mapeo de IDs Liferay a Salas: `id=1` → Constitucional, `id=2` → Político-Administrativa, ... `id=7` → Plena.
- **Directivas Técnicas:**
  - Mapear correctamente los alias y códigos oficiales de las Salas (`scon`, `spa`, `scc`, `scp`, `scs`, `se`, `plena`).
  - Los nombres de archivo canónicos para SQLite y Excel deben seguir el patrón `sala_<snake_case>.db/.xlsx`.

---

## 🔄 Workflow y Ciclo de Vida del Desarrollo (SDLC Directives)

Cualquier cambio o extensión en el proyecto debe seguir el siguiente flujo estricto:

```mermaid
flowchart LR
    A[Requisito / Issue] --> B[Diseño Playwright & UX]
    B --> C[Implementación de Código]
    C --> D[Auditoría QA & Test Automation]
    D --> E[Reportes / PDF / DB / Excel]
    E --> F[Containerfile + Podman Build]
    F --> G[Commit & Sync a GitHub]
```

1. **Planificación:** Definir el impacto en los módulos `src/` y verificar configuración en `config.json`.
2. **Desarrollo:** Mantener la separación de responsabilidades entre Scraping (Playwright), Base de Datos (SQLite), Reportes (Excel/PDF) y UI (Dash).
3. **Pruebas (QA):** Ejecutar `python -m unittest discover tests` para validar la ausencia de regresiones. Smoke test: `python -c "from src.buscador_tsj_excel import BuscadorTSJExcel; b=BuscadorTSJExcel(); print(b._get_playwright_scraper() is not None)"`.
4. **Containerización:** Verificar `podman build -t case-law-extractor .` completa sin errores.
5. **Documentación:** Actualizar [README.md](file:///c:/VS%20CODE/CODIGO/Extractor%20Jurisprudencias/README.md) y este documento canónico si cambian especificaciones o arquitecturas.

---

## 💡 Reglas Canónicas Inquebrantables

> [!IMPORTANT]  
> **1. Idempotencia de Datos:** Nunca duplicar sentencias en SQLite. El campo `link_directo` es la clave única universal. `ON CONFLICT(link_directo) DO UPDATE SET` es obligatorio en todo INSERT.

> [!WARNING]  
> **2. Portal TSJ — Sin API REST Pública:** El portal del TSJ Venezuela usa Liferay Portal (Java) con XHR AJAX. Las peticiones directas `requests.get()` solo devuelven `{}` vacío. **Obligatorio usar Playwright Chromium headless** para navegar el portal y interceptar respuestas XHR via `page.on("response", callback)`. Los intentos de acceso directo a la API deben documentarse como fallidos.

> [!TIP]  
> **3. Formato PDF de Alta Fidelidad:** Los PDFs generados en `src/utils.py` mediante ReportLab representan documentos legales oficiales y deben mantener los márgenes, logos y tipografías mencionadas.

> [!NOTE]  
> **4. Ajuste Tipográfico y Cero Desbordamiento Visual (SVG/PDF/UI):** Todos los diagramas gráficos, interfaces vectoriales `.svg`, documentos PDF y componentes visuales deben calibrar minuciosamente los tamaños de letra (`font-size`), márgenes e interlineados para garantizar que **ningún texto desborde** los límites de las tarjetas o del lienzo (`viewBox="0 0 900 1350"` en formato Folio Vertical).

> [!NOTE]  
> **5. Optimización SEO & Accesibilidad Universal Obligatoria:** Todas las entregas documentales, recursos gráficos SVG e interfaces web deben incorporar de forma automática estándares completos de SEO y accesibilidad: atributos `role="img"`, `aria-labelledby`, metadatos `<metadata>` con Schema.org / Dublin Core, etiquetas `<title>` y `<desc>` semánticas, y estructura HTML5 / Markdown optimizada para motores de búsqueda y lectores de pantalla.

> [!NOTE]  
> **6. Arquitectura Web Dashboard 100% Python (Dash + Bootstrap):** Todas las interfaces gráficas web desarrolladas deben proveer una alternativa 100% Python mediante `dash` y `dash-bootstrap-components` (`gui/dash_app.py`), garantizando la selección interactiva de Sala (0-7), Mes (0-12), barra de progreso en tiempo real desde Playwright (`sync_progress` polling cada 400ms), visor emergente de Pop-Ups y exportación emparejada 1:1 de bases de datos SQLite (`.db`) y matrices Excel (`.xlsx`) respetando la paleta institucional DC3 Cyber Center.

> [!NOTE]  
> **7. Containerización Obligatoria (Podman):** El proyecto debe mantenerse siempre deployable vía `podman build` + `podman run`. El `Containerfile` debe instalar Chromium headless con `playwright install chromium --with-deps`. Los datos (SQLite + Excel) deben persistir en un volumen montado `./data:/app/data`.

> [!NOTE]  
> **8. Fondo Blanco Obligatorio en Diagramas SVG Formato Folio:** Al crear o actualizar archivos gráficos vectoriales `.svg` en orientación vertical u Hoja Folio / Legal (`viewBox="0 0 900 1350"`), el fondo del lienzo debe ser estrictamente blanco (`<rect width="100%" height="100%" fill="#FFFFFF"/>`), ajustando minuciosamente la tipografía, tarjetas, bordes y conectores para preservar la paleta y contraste institucional del DC3 Cyber Center (`#061830`, `#0066CC`, `#FFC809`).

> [!NOTE]  
> **9. Layout Ultra-Minimalista de 50px en Encabezados y Pies de Página (UI Web & SVG):** Todas las barras superiores de navegación/encabezados (Top Menu / Header Navbar) y los pies de página (Footer), tanto en la interfaz de usuario web (`gui/dash_app.py`) como en la diagramación gráfica vectorial (`assets/*.svg`), deben construirse con un diseño ultra-minimalista de **exactamente 50px de alto** (`height: 50px`). Esto evita el consumo excesivo de espacio vertical, optimizando la visibilidad del contenido principal.

---

<div align="center">

**Documento Canónico Oficial de Gobernanza del Proyecto**  
⚖️ Case Law Extractor powered by sha256.us  
v2.0 — Motor Playwright Chromium Headless • Agosto 2026

</div>
