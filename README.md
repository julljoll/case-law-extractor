# ⚖️ Extractor & Buscador de Jurisprudencia TSJ Venezuela

[![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-SQLite3-003B57.svg?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Pandas](https://img.shields.io/badge/Export-Pandas%20%7C%20Excel-150458.svg?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![ReportLab](https://img.shields.io/badge/PDF%20Engine-ReportLab-red.svg?style=for-the-badge&logo=adobeacrobatreader&logoColor=white)](https://www.reportlab.com/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg?style=for-the-badge)](#)

Sistema automatizado de **Scraping, Indexación, Búsqueda y Extracción de Decisiones Jurisprudenciales** del Tribunal Supremo de Justicia (TSJ) de Venezuela. 

Diseñado para realizar escaneos globales masivos de todas las Salas (2019-2026), almacenar la información estructurada en una base de datos relacional SQLite local, generar matrices analíticas en Excel (`.xlsx`), e imprimir sentencias en archivos PDF formateados con estándares visuales oficiales del TSJ.

---

## 📑 Tabla de Contenidos
1. [📌 Descripción General](#-descripción-general)
2. [🔄 Pipeline de Funcionamiento (Workflow)](#-pipeline-de-funcionamiento-workflow)
3. [✨ Características Principales](#-características-principales)
4. [📁 Estructura del Proyecto](#-estructura-del-proyecto)
5. [🛠️ Requisitos e Instalación](#️-requisitos-e-instalación)
6. [🚀 Guía de Uso](#-guía-de-uso)
7. [⚙️ Configuración (`config.json`)](#️-configuración-configjson)
8. [🗄️ Esquema de la Base de Datos (SQLite)](#️-esquema-de-la-base-de-datos-sqlite)
9. [🏛️ Cobertura de Salas del TSJ](#️-cobertura-de-salas-del-tsj)
10. [💡 Buenas Prácticas y Consejos](#-buenas-prácticas-y-consejos)

---

## 📌 Descripción General

El **Extractor de Jurisprudencias TSJ** automatiza la recolección de decisiones del portal oficial del TSJ. Reemplaza la búsqueda manual mediante la extracción metódica de campos clave: **Número de Sentencia, Expediente, Fecha, Sala, Tema, Materia, Asunto/Extracto y Enlaces Directos**.

> [!NOTE]  
> El sistema incluye un módulo especializado en **Jurisprudencia Tecnológica**, optimizado para la identificación y clasificación de sentencias vinculadas a **Evidencia Digital, Delitos Informáticos, Peritajes Tecnológicos y Cadena de Custodia Electrónica**.

---

## 🔄 Pipeline de Funcionamiento (Workflow)

El flujo de trabajo está diseñado en **5 etapas secuenciales** altamente optimizadas para garantizar tolerancia a fallos, procesamiento limpia de datos e indexación rápida.

```mermaid
flowchart TD
    subgraph 1_ETAPA_EXTRACCION ["🌐 Etapa 1: Extracción HTTP & Scraping"]
        A[Inicio / CLI / main.py] --> B[Cargar config.json]
        B --> C{Modo de Extracción}
        C -->|Escaneo Global| D[Fetch HTML TSJ 2019-2026]
        C -->|Búsqueda / Actualizar| E[Query Específica o Lote Reciente]
        C -->|Paso a Paso| F[Extracción Interactiva con Impresión PDF]
    end

    subgraph 2_ETAPA_PROCESAMIENTO ["🧹 Etapa 2: Parsing & Limpieza"]
        D --> G[BeautifulSoup Parser]
        E --> G
        F --> G
        G --> H[Limpieza de Texto / Caracteres Especiales]
        H --> I[Extracción de Metadatos: Sala, Expediente, Sentencia, Extracto]
    end

    subgraph 3_ETAPA_CLASIFICACION ["🤖 Etapa 3: Clasificación & Filtro Tecnológico"]
        I --> J{¿Modo Tecnológico Activo?}
        J -->|Sí| K[Escanear Términos Clave: Evidencia Digital, Ciberdelito, etc.]
        J -->|No| L[Indexación Estándar]
        K --> L
    end

    subgraph 4_ETAPA_ALMACENAMIENTO ["🗄️ Etapa 4: Almacenamiento Relacional"]
        L --> M[(SQLite DB: data/tsj_jurisprudencia.db)]
        M --> N[Control de Duplicados ON CONFLICT link_directo]
    end

    subgraph 5_ETAPA_EXPORTACION ["📊 Etapa 5: Generación de Reportes & Documentos"]
        N --> O[Exportación Excel: data/Excel_Buscador/Matriz.xlsx]
        N --> P[Exportación PDF Oficial: data/PDFs/ / data/Jurisprudencia_Tecnologica/]
        N --> Q[JSON / CSV Backups]
    end
```

### Detalle por Etapas:

| Etapa | Nombre | Descripción | Tecnologías Utilizadas |
| :--- | :--- | :--- | :--- |
| **Etapa 1** | **Scraping HTTP** | Consultas automatizadas al portal web del TSJ con manejo de reintentos, timeouts y evasión de bloqueos SSL. | `requests`, `urllib3` |
| **Etapa 2** | **Parsing & Clean** | Procesamiento del DOM HTML, extracción del cuadro de metadatos y limpieza de texto normalizado. | `BeautifulSoup4`, `lxml`, `re` |
| **Etapa 3** | **Clasificación** | Detección de patrones y palabras clave tecnológicas en materias civiles, penales y constitucionales. | Regex, Custom Algorithms |
| **Etapa 4** | **Persistencia DB** | Inserción/Actualización atómica en base de datos relacional SQLite indexada por enlace único. | `sqlite3` (Tabla `decisiones`) |
| **Etapa 5** | **Exportación UX** | Creación de matrices de datos visuales en Excel y maquetación de sentencias en PDF con diseño oficial. | `pandas`, `openpyxl`, `reportlab` |

---

## ✨ Características Principales

- **🌐 Escaneo Multisala Global (2019 - 2026):** Recorre automáticamente las 7 Salas del TSJ indexando miles de decisiones.
- **⚡ Base de Datos SQLite Integrada:** Almacena y actualiza los registros sin duplicar datos gracias a índices en `link_directo`, `expediente`, `sala` y `ano`.
- **📊 Matriz Analítica Excel (.xlsx):** Genera libros de trabajo con formato visual, encabezados estilizados y anchos de columna autoajustados.
- **📑 Generación de PDF Oficiales (ReportLab):** Crea documentos PDF listos para imprimir con encabezado oficial del TSJ, membrete institucional, tablas de metadatos y maquetación jurídica formal.
- **🛡️ Módulo de Jurisprudencia Tecnológica:** Filtra y clasifica sentencias clave sobre peritajes informáticos, delitos cibernéticos, evidencia digital y redes sociales.
- **💻 CLI Interactivo & Menú Colorama:** Interfaz gráfica en consola intuitiva con barra de progreso (`tqdm`) y colores semánticos (`colorama`).

---

## 📁 Estructura del Proyecto

```text
Extractor Jurisprudencias/
├── config.json                     # Configuración principal (salas, años, límites, rutas)
├── main.py                         # Punto de entrada y CLI interactivo
├── ejecutar_extractor.bat          # Lanzador rápido para Windows
├── run.bat                         # Script ejecutable directo
├── create_bat.py                   # Generador de ejecutables bat
├── requirements.txt                # Dependencias del sistema
│
├── src/                            # Código fuente del núcleo
│   ├── extractor.py                # Clase JurisprudenciaExtractor (Scraper & Orquestador)
│   ├── database.py                 # Gestor TSJDatabaseManager (SQLite)
│   ├── buscador_tsj_excel.py       # Consultor y exportador a Excel
│   ├── paso_a_paso_scraper.py      # Extractor guiado paso a paso con PDF
│   └── utils.py                    # Utilidades de parsing, PDF ReportLab, exportaciones
│
├── data/                           # Directorio de persistencia de datos (auto-generado)
│   ├── tsj_jurisprudencia.db       # Base de datos relacional SQLite
│   ├── Excel_Buscador/             # Archivos Excel generados (.xlsx)
│   ├── PDFs/                       # Sentencias extraídas en PDF oficial
│   └── Jurisprudencia_Tecnologica/ # PDFs clasificados en área digital/tecnológica
│
├── assets/                         # Recursos gráficos y logos para PDF
└── tests/                          # Suite de pruebas unitarias (test_extractor.py)
```

---

## 🛠️ Requisitos, Dependencias y Puesta en Marcha

### 📋 Prerrequisitos del Sistema
- **Python 3.9** o superior ([Descargar Python](https://www.python.org/downloads/)).
- **Git** ([Descargar Git](https://git-scm.com/)).
- Conexión a Internet activa para realizar peticiones al portal del TSJ.

---

### 📦 Dependencias del Proyecto (`requirements.txt`)

Todas las dependencias necesarias están especificadas en `requirements.txt`. A continuación se detalla el propósito de cada paquete:

| Paquete | Versión Mínima | Propósito / Función en el Proyecto |
| :--- | :--- | :--- |
| `requests` | `>= 2.31.0` | Cliente HTTP para realizar scraping y descargas desde el portal del TSJ. |
| `beautifulsoup4` | `>= 4.12.0` | Parser del DOM HTML para extraer metadatos de las sentencias. |
| `lxml` | `>= 4.9.0` | Motor de parsing C de alto rendimiento para procesar HTML complejo. |
| `pandas` | `>= 2.0.0` | Estructuración y manipulación de datos en dataframes analíticos. |
| `openpyxl` | `>= 3.1.0` | Generación y formateo de libros de trabajo Excel (`.xlsx`). |
| `colorama` | `>= 0.4.6` | Formato visual con colores semánticos en la interfaz de consola CLI. |
| `tqdm` | `>= 4.66.0` | Barras de progreso animadas en la terminal durante el escaneo. |
| `reportlab` | `>= 4.0.0` | Motor de maquetación y generación de documentos PDF con formato oficial. |
| `pillow` | `>= 10.0.0` | Procesamiento e inserción de imágenes/emblemas en los encabezados PDF. |

---

### 🏁 Guía Paso a Paso para Poner en Marcha el Proyecto

Sigue estos 6 pasos detallados para clonar, configurar y ejecutar el proyecto desde cero en cualquier equipo:

#### Paso 1: Clonar el Repositorio
Abre tu terminal o PowerShell y ejecuta:
```bash
git clone https://github.com/julljoll/case-law-extractor.git
cd case-law-extractor
```

#### Paso 2: Crear el Entorno Virtual (`venv`)
Es recomendable aislar las dependencias dentro de un entorno virtual:

- **En Windows (PowerShell / CMD):**
  ```powershell
  python -m venv venv
  ```
- **En Linux / macOS:**
  ```bash
  python3 -m venv venv
  ```

#### Paso 3: Activar el Entorno Virtual

- **En Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
  *(Si PowerShell bloquea los scripts, ejecuta antes: `Set-ExecutionPolicy Unrestricted -Scope Process`)*

- **En Windows (CMD):**
  ```cmd
  venv\Scripts\activate.bat
  ```

- **En Linux / macOS:**
  ```bash
  source venv/bin/activate
  ```

#### Paso 4: Instalar las Dependencias
Con el entorno virtual activado, instala todos los paquetes requeridos con un solo comando:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Paso 5: Generar Recursos Visuales e Inicializar Entorno
Ejecuta el script auxiliar para verificar la creación del emblema institucional para los documentos PDF:
```bash
python src/create_assets.py
```
*(Este comando generará el archivo `assets/escudo_venezuela.png` necesario para los reportes PDF).*

#### Paso 6: Ejecutar el Sistema

- **Opción A: Modo Menú Interactivo (Consola)**
  ```bash
  python main.py
  ```

- **Opción B: Lanzador Automático en Windows**
  Hacer doble clic en `ejecutar_extractor.bat` o ejecutarlo desde la terminal:
  ```cmd
  ejecutar_extractor.bat
  ```

---

### ⚡ Solución de Problemas Frecuentes (Troubleshooting)

> [!WARNING]  
> **Error SSL Handshake (`SSLCertVerificationError`):**  
> El servidor del TSJ a menudo presenta inconsistencias SSL. El proyecto ya incluye `verify=False` en las peticiones HTTP y desactiva las advertencias con `urllib3.disable_warnings()`, por lo que no requiere configuración adicional de certificados.

> [!TIP]  
> **Permisos de Ejecución de Scripts `.bat` en Windows:**  
> Si Windows bloquea la ejecución de `ejecutar_extractor.bat`, haz clic derecho sobre el archivo -> *Propiedades* -> marca la casilla **Desbloquear** (*Unblock*) -> *Aplicar*.

---

## 🚀 Guía de Uso

El proyecto puede ejecutarse de manera **interactiva** o mediante **comandos directos por consola (CLI)**.

### 1. Menú Interactivo (Recomendado para usuarios)

Simplemente ejecuta `main.py` sin argumentos:

```bash
python main.py
```

Aparecerá el menú interactivo en consola:

```text
===========================================================================
       BUSCADOR Y BASE DE DATOS DE JURISPRUDENCIA TSJ VENEZUELA
  Escaneo Global (2019-2026) a SQLite DB Local + Matriz Excel (.xlsx)
===========================================================================

Seleccione la opción deseada:
  [1] Escaneo Global de Todas las Páginas del TSJ (2019 a 2026) -> SQLite + Excel
  [2] Actualizar Base de Datos SQLite y Excel (Últimas Jurisprudencias)
  [3] Búsqueda Personalizada por Palabra Clave, Materia o Expediente (SQLite + Excel)
  [4] Ver Estadísticas y Registros de la Base de Datos SQLite Local
  [5] Extracción Guiada Paso a Paso (Ventana Emergente e Impresión PDF)
  [6] Salir
```

### 2. Argumentos por Línea de Comandos (CLI)

| Opción / Flag | Descripción | Comando Ejemplo |
| :--- | :--- | :--- |
| `-g` / `--global` | Ejecuta el escaneo global de todas las salas (2019-2026). | `python main.py -g` |
| `-u` / `--actualizar` | Sincroniza y actualiza la base de datos con las sentencias más recientes. | `python main.py -u` |
| `--stats` / `--db` | Muestra estadísticas y número de registros en SQLite. | `python main.py --db` |
| `-p` / `--paso-a-paso` | Ejecuta el extractor en modo paso a paso con impresión en PDF. | `python main.py -p` |
| `<archivo_config.json>` | Ejecuta el extractor utilizando un archivo JSON personalizado. | `python main.py config.json` |

### 3. Ejecución Directa en Windows

Puedes hacer doble clic sobre los archivos lanzadores:
- **`ejecutar_extractor.bat`**: Abre la consola interactiva lista para operar.
- **`run.bat`**: Ejecución rápida del pipeline principal.

---

## ⚙️ Configuración (`config.json`)

El comportamiento del extractor se controla mediante el archivo `config.json`:

```json
{
  "sala": "Sala Constitucional",
  "sala_id": "constitucional",
  "ano": 2026,
  "ano_inicio": 2019,
  "ano_fin": 2026,
  "palabra_clave": "",
  "limite": 20,
  "formato_salida": "excel",
  "carpeta_salida": "data/PDFs",
  "carpeta_excel": "data/Excel_Buscador",
  "descargar_pdf_directo": false,
  "modo_tecnologia": true,
  "escanear_todas_las_salas": true,
  "carpeta_tecnologia": "data/Jurisprudencia_Tecnologica"
}
```

### Descripción de Parámetros:

> [!TIP]  
> Modifica `ano_inicio` y `ano_fin` en `config.json` para acotar los rangos de búsqueda cuando requieras análisis específicos por período.

| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `sala_id` | `string` | Identificador de la sala por defecto (`constitucional`, `casacion_penal`, `casacion_civil`, etc.). |
| `ano_inicio` / `ano_fin` | `integer` | Rango cronológico para el escaneo masivo de sentencias. |
| `limite` | `integer` | Límite máximo de sentencias a procesar por consulta en modo manual. |
| `modo_tecnologia` | `boolean` | Si es `true`, activa el filtro y guardado prioritario de casos sobre tecnología y evidencia digital. |
| `escanear_todas_las_salas` | `boolean` | Recorre secuencialmente las 7 Salas del TSJ en escaneos automáticos. |
| `carpeta_excel` | `string` | Ruta donde se exportarán los archivos `.xlsx` compilados. |
| `carpeta_tecnologia` | `string` | Ruta de salida para los PDFs catalogados en la categoría de tecnología. |

---

## 🗄️ Esquema de Bases de Datos SQLite Dedicadas

Cada búsqueda o fórmula ejecutada genera una base de datos SQLite independiente ubicada en `data/Databases_SQLite/` que se empareja 1:1 con su correspondiente libro de trabajo en Excel en `data/Excel_Buscador/`.

**Ejemplos de archivos emparejados generados:**
- Búsqueda: `"delitos informáticos"` -> `data/Databases_SQLite/Busqueda_delitos_informaticos.db` y `data/Excel_Buscador/Busqueda_delitos_informaticos.xlsx`
- Escaneo Global: -> `data/Databases_SQLite/Escaneo_Global_TSJ_2019_2026.db` y `data/Excel_Buscador/Escaneo_Global_TSJ_2019_2026.xlsx`

### Tabla: `decisiones`

```sql
CREATE TABLE IF NOT EXISTS decisiones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sala TEXT NOT NULL,
    numero_sentencia TEXT,
    expediente TEXT,
    fecha TEXT,
    ano INTEGER,
    tema TEXT,
    materia TEXT,
    asunto TEXT,
    extracto TEXT,
    link_directo TEXT UNIQUE,
    fecha_escaneo TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Índices de Rendimiento:
- `idx_link_directo`: Búsqueda rápida por URL y prevención de duplicados (`UNIQUE`).
- `idx_sala`: Filtro optimizado por Sala.
- `idx_expediente`: Consultas ágiles por número de expediente.
- `idx_ano`: Agrupación y reportes cronológicos.

---

## 🏛️ Cobertura de Salas del TSJ

El extractor cubre la totalidad de las salas jurisdiccionales del Tribunal Supremo de Justicia de Venezuela:

| Clave (`sala_id`) | Nombre Oficial de la Sala | Código TSJ |
| :--- | :--- | :--- |
| `constitucional` | **Sala Constitucional** | `scon` |
| `politico_administrativa` | **Sala Político-Administrativa** | `spa` |
| `casacion_civil` | **Sala de Casación Civil** | `scc` |
| `casacion_penal` | **Sala de Casación Penal** | `scp` |
| `casacion_social` | **Sala de Casación Social** | `scs` |
| `electoral` | **Sala Electoral** | `se` |
| `plena` | **Sala Plena** | `plena` |

---

## 💡 Buenas Prácticas y Consejos

> [!IMPORTANT]  
> **Conexión al Portal del TSJ:** El sitio oficial del TSJ a menudo utiliza certificados SSL autofirmados o desactualizados. El extractor omite las advertencias SSL inseguras de forma segura para evitar interrupciones en las consultas.

> [!WARNING]  
> **Reintentos y Rate Limiting:** En escaneos globales masivos, asegúrate de mantener un `timeout` prudente (configurado por defecto en 15s) para evitar que el servidor remoto del TSJ rechace peticiones por exceso de tráfico.

> [!TIP]  
> **Generación de PDFs Oficiales:** Para obtener documentos PDF idénticos a los dictámenes oficiales, asegúrate de tener la librería `reportlab` instalada y actualizada.

---

<div align="center">

**Desarrollado para la Automatización y Análisis Jurídico Avanzado**  
⚖️ Extractor Jurisprudencias TSJ • Venezuela

</div>
