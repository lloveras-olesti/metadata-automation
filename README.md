# Case study SEO — Llibres del Mirall

**Proyecto SEO end-to-end sobre un ecommerce real de ~7.000 páginas: automatización de metadata, auditorías técnicas y medición de impacto.**

Este repositorio documenta un proyecto SEO completo realizado para **Llibres del Mirall**, una librería anticuaria de Barcelona con tienda online sobre PrestaShop. El proyecto se aborda como tres líneas de trabajo complementarias —automatización, auditoría y medición— que cubren el ciclo completo del trabajo de un SEO: detectar problemas, ejecutar la solución y medir su impacto.

Está publicado como **proyecto de portfolio**. La documentación prioriza la metodología y las decisiones de criterio sobre los datos comerciales del cliente.

---

## Contexto del proyecto

La tienda presentaba un volumen alto de páginas (~7.000 entre productos, categorías y CMS) con metadata mal optimizada: títulos y meta descriptions duplicados, vacíos, fuera de rango de longitud o sin keywords relevantes. Optimizar esto manualmente página a página no era viable.

A partir de ese problema inicial, el alcance se amplió a una revisión técnica del sitio y a la construcción de un sistema de medición que no existía: el cliente no disponía de ningún panel de seguimiento del rendimiento orgánico.

El trabajo se dividió por responsabilidad: el rol de este proyecto fue **auditar, recomendar y automatizar la generación de contenido SEO**. La implementación de cambios a nivel de servidor y tema fue responsabilidad del equipo de desarrollo del cliente; las auditorías están redactadas como entregables accionables pensados para ese equipo.

---

## Estructura del repositorio

```
.
├── automation/   → Pipeline de automatización de metadata SEO
├── audits/       → Auditorías técnicas (schema markup y Core Web Vitals)
└── reporting/    → Dashboard de medición en Looker Studio (documentación)
```

---

## 1. Automatización de metadata — `automation/`

Pipeline en Python que automatiza la corrección de la metadata SEO de todo el catálogo.

Toma como entrada los CSV de auditoría de **Screaming Frog** (URLs con issues de título, meta description o texto alternativo), clasifica cada URL por tipo, y genera un CSV de salida con metadata nueva y optimizada para SEO. La generación combina dos enfoques: **reglas deterministas** por plantilla para las páginas de volumen, y la **API de Claude** para las páginas de mayor competencia, donde la calidad del texto justifica el coste. Los cambios se publican en PrestaShop a través de su Webservice API.

El pipeline procesó **7.009 URLs** (productos, categorías y páginas CMS) en un sitio multilingüe (español y catalán).

> **Para el detalle completo** —arquitectura de scripts, lógica de clasificación, estrategia plantilla vs. LLM, manejo de errores— ver el **[`README.md` propio de la carpeta `automation/`](automation/)**.

**Conceptos SEO cubiertos:** optimización on-page a escala, rastreo e indexación, arquitectura de URLs, SEO ecommerce, SEO internacional (hreflang / multilingüe).

---

## 2. Auditorías técnicas — `audits/`

Dos auditorías técnicas del sitio, redactadas como documentos de consultoría: resumen ejecutivo, metodología, hallazgos, análisis de causa raíz y **recomendaciones priorizadas por matriz impacto/esfuerzo**.

### [`schema-markup-audit.md`](audits/schema-markup-audit.md)

Auditoría del marcado de datos estructurados sobre tres *page types* representativos (homepage, categoría, producto), combinando análisis de código fuente con el Google Rich Results Test.

Conclusión central: **markup técnicamente válido pero estratégicamente incompleto**. El sitio pasa la validación de Google con 0 errores, pero implementa solo el mínimo: usa `Product` genérico en lugar de `Book`, omite `itemCondition` (clave para una librería de segunda mano), no marca la organización ni los breadcrumbs, y usa Microdata en lugar de JSON-LD. La auditoría incluye **bloques JSON-LD listos para implementar**.

### [`core-web-vitals-audit.md`](audits/core-web-vitals-audit.md)

Auditoría de rendimiento combinando datos de campo (CrUX) y de laboratorio (Lighthouse vía PageSpeed Insights API) sobre los mismos tres *page types*, en mobile y desktop.

Conclusión central: **Core Web Vitals suspendido en mobile y desktop**. El hallazgo más relevante se identificó inspeccionando el código fuente: las portadas de libros se cargan como `background-image` CSS sobre un placeholder GIF, lo que impide al navegador descubrirlas y dispara el LCP en mobile hasta 23–28 segundos. La auditoría documenta la causa raíz de cada problema y entrega **12 recomendaciones priorizadas en 4 niveles**, con código de ejemplo específico para PrestaShop.

**Herramientas:** Screaming Frog · Google Rich Results Test · Schema.org Validator · PageSpeed Insights API · Lighthouse · Chrome UX Report.

**Conceptos SEO cubiertos:** datos estructurados / schema, Core Web Vitals, SEO técnico, auditoría web.

---

## 3. Dashboard de medición — `reporting/`

Documentación de un **dashboard de medición SEO construido en Looker Studio**, unificando datos de **Google Analytics 4** y **Google Search Console** a través de sus conectores nativos.

El dashboard responde a tres necesidades: monitorizar el rendimiento general de la tienda (audiencia, comportamiento y embudo de conversión), **medir el impacto del proyecto de automatización de metadata** sobre las URLs y queries afectadas (rendimiento orgánico pre/post implementación vía GSC), y servir de base para análisis ad hoc —incluyendo la investigación de una anomalía de tráfico de febrero 2026 identificada como tráfico automatizado no humano.

Como el dashboard es un objeto vivo y no un archivo, esta carpeta documenta el proyecto mediante:

| Archivo | Contenido |
|---|---|
| [`methodology.md`](reporting/methodology.md) | Decisiones de construcción: fuentes, conectores, filtrado, períodos de comparación y sus motivos. |
| [`data-dictionary.md`](reporting/data-dictionary.md) | Definición exacta de cada métrica, dimensión y campo calculado del dashboard. |
| [`insights.md`](reporting/insights.md) | Interpretación de resultados y análisis de la anomalía de tráfico de febrero. |
| [`assets/`](reporting/assets/) | Exportaciones del dashboard en PDF: [`Medición_Llibres_del_Mirall_(Demo_Data).pdf`](reporting/assets/Medición_Llibres_del_Mirall_(Demo_Data).pdf) (informe completo con datos de ejemplo) y [`Medición_Anomalía_Febrero.pdf`](reporting/assets/Medición_Anomalía_Febrero.pdf) (análisis de la anomalía de tráfico con datos reales). |

**Herramientas:** Looker Studio · Google Analytics 4 · Google Search Console.

**Conceptos SEO cubiertos:** reporting SEO, GA4, Search Console, medición de impacto, análisis de embudo de conversión.

---

## Nota sobre los datos del cliente

El proyecto se basa en datos reales de un cliente real. La documentación pública se ha redactado evitando exponer información comercial sensible (contenido específico de la metadata generada, datos de facturación). El foco está deliberadamente puesto en **metodología y criterio**, no en los datos en bruto del cliente.

Los PDFs incluidos en `reporting/assets/` han sido seleccionados con este criterio: el informe general del dashboard utiliza **datos de ejemplo** (mock data) para ilustrar la estructura y las métricas sin exponer cifras reales; el informe de la anomalía de febrero se publica con **datos reales** al tratarse de un análisis técnico sobre tráfico automatizado, sin implicaciones comerciales sensibles.

---

**Autor:** Blai Lloveras · Mayo 2026
