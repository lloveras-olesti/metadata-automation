# Metodología — Dashboard de Medición SEO
**Cliente:** Llibres del Mirall (anonimizado en versión pública)  
**Herramienta:** Looker Studio  
**Última actualización:** Mayo 2026

> Este documento explica las decisiones de construcción del dashboard: qué se eligió, qué se descartó y por qué. Complementa el `data-dictionary.md` (definiciones de métricas) y el `insights.md` (interpretación de resultados).

---

## 1. Alcance del dashboard

El dashboard cubre dos ámbitos distintos que se complementan:

**Rendimiento general de la tienda** (páginas 1 y 2): métricas de audiencia, comportamiento y conversión sobre el **total del tráfico**, sin filtro de canal. Esta decisión es deliberada: el rendimiento de las páginas — incluyendo el embudo de conversión — es independiente del origen del tráfico. Una tasa de abandono en checkout o un tiempo de carga deficiente afectan a cualquier usuario independientemente de cómo llegó al sitio. El canal orgánico se analiza de forma específica en las páginas de medición de metadata.

**Medición del impacto de la implementación SEO** (páginas 3 y 4): seguimiento específico del rendimiento orgánico en las URLs y queries directamente afectadas por el proyecto de automatización de metadata. Estos datos provienen exclusivamente de Google Search Console y miden visibilidad orgánica, no comportamiento en sesión.

**Análisis ad hoc de anomalías** (página 5): documentación del proceso de investigación de la anomalía de tráfico de febrero 2026. Esta página no es de monitorización continua — es un caso de análisis puntual preservado en el dashboard como evidencia del proceso investigador.

---

## 2. Fuentes de datos y conectores

### Google Analytics 4
Conector utilizado: **GA4 nativo de Looker Studio** (gratuito, sin configuración adicional).

Se descartó la conexión vía BigQuery por dos motivos: genera costes variables según el volumen de consultas, y añade complejidad de configuración innecesaria para el nivel de análisis requerido. El conector nativo es suficiente para todas las dimensiones y métricas utilizadas en este dashboard.

Limitación conocida: GA4 aplica sampling en datasets con alta cardinalidad. Para el volumen de tráfico de este cliente (~7.500 sesiones mensuales), el sampling no es un problema activo — los umbrales de GA4 donde el sampling se activa están muy por encima de estos volúmenes.

### Google Search Console
Conector utilizado: **Search Console (URL) nativo de Looker Studio**.

Se eligió el conector URL (en lugar del conector Site) porque permite segmentar por URL de destino además de por query, lo que es necesario para las tablas de medición de páginas específicas.

Limitación conocida: los datos de GSC tienen un retraso típico de 2–3 días respecto a la fecha actual. Las tablas de últimos 28 días no incluyen los últimos 2–3 días del período. Esto es una limitación de la API de GSC, no del conector.

Limitación conocida: GSC limita a 1.000 filas por petición en el análisis de queries. Para este cliente, con un catálogo de ~7.000 páginas pero un volumen de queries activas moderado, este límite no afecta a las tablas del dashboard, que trabajan con selecciones acotadas de URLs y queries específicas.

---

## 3. Filtrado del blog

La propiedad GA4 y la propiedad GSC monitorizan tanto el ecommerce como el blog del cliente en el mismo account. El blog no es objeto de este análisis.

Se aplicó un **filtro permanente a nivel de conector** en ambas fuentes de datos, no a nivel de página o widget. Esto garantiza que el filtro se aplica a cualquier elemento que se añada al dashboard en el futuro sin necesidad de recordarlo.

El filtro se implementó mediante un campo calculado que clasifica cada sesión/URL como `Blog` o `Ecommerce` en función de si la URL contiene el patrón `/blog/`:

```
CASE
  WHEN REGEXP_MATCH(Landing page, ".*/blog/.*") THEN "Blog"
  ELSE "Ecommerce"
END
```

El filtro activo sobre ese campo es `= Ecommerce`. Se verificó previamente que todas las URLs del blog siguen el patrón `/blog/` de forma consistente, incluyendo paginación y páginas de etiqueta.

---

## 4. Decisiones sobre períodos y comparaciones

### Períodos dinámicos
Las páginas de visión general y embudo de conversión usan **últimos 28 días** como período base, con comparación automática contra los 28 días anteriores. Se eligieron 28 días en lugar de mes natural por dos motivos: incluye exactamente 4 semanas completas (elimina el sesgo de días de la semana), y permite una comparación limpia período a período sin los efectos de meses de distinta longitud.

### Períodos fijos en las tablas de medición
Las tablas de medición de URLs y queries tienen una tabla dinámica (últimos 28 días) y una tabla de referencia con período fijo. La lógica de esta estructura es permitir comparar el estado actual contra un punto de referencia estable que no se mueve con el tiempo.

**Abril 2026** se usa como período de referencia para URLs porque es el mes posterior a la implementación de metadata — es el primer mes donde los cambios estaban activos. Se descartó como referencia para queries debido al impacto de Sant Jordi (23 de abril), festividad del libro en Cataluña que genera un pico de búsquedas atípico no representativo del comportamiento habitual.

**Marzo 2026** se usa como período de referencia para queries por ser el mes estable más reciente antes de la anomalía de abril.

**Febrero 2026 está excluido** de cualquier análisis comparativo. Durante ese mes se registró una anomalía de tráfico (>90.000 usuarios nuevos frente a una media de 4.000–5.000) identificada como tráfico automatizado no humano. Ver `insights.md` para el análisis completo.

---

## 5. Decisiones sobre métricas de conversión

Los ratios del embudo de conversión (Add_to_Cart/View_item, Purchase/Add_to_Cart, Purchase/View_Item) se calculan a partir de **métricas nativas de ecommerce de GA4** (`Artículos vistos`, `Artículos añadidos al carrito`, `Artículos comprados`), no a partir de conteos de eventos.

Esta decisión responde a una limitación técnica: cuando `Nombre del evento` se usa como dimensión en Looker Studio, los datos se organizan en filas separadas por tipo de evento. Un campo calculado en Looker Studio evalúa fila a fila y no puede dividir el valor de una fila entre el valor de otra fila diferente. El uso de las métricas nativas de ecommerce, que existen como columnas independientes en GA4, evita esta limitación sin necesidad de soluciones alternativas más complejas.

Prerequisito: estas métricas nativas solo están disponibles si el tracking de ecommerce está correctamente configurado en GA4 con los eventos estándar de ecommerce (`view_item`, `add_to_cart`, `purchase`) y sus parámetros de items. En este caso, la configuración está activa y las métricas son consistentes con los eventos registrados.

---

## 6. Tratamiento del sitio multilingüe

El sitio opera en dos idiomas, español (`/es/`) y catalán (`/ca/`), con URLs completamente separadas. El dashboard no aplica ningún filtro de idioma — todas las métricas muestran datos agregados de ambas versiones.

Las tablas de medición de URLs incluyen mayoritariamente páginas en español por ser las de mayor alcance. La excepción es la página de información de la librería, que se monitoriza en su versión catalana (`/ca/content/8-la-llibreria`) por ser la que históricamente ha recibido más tráfico de las dos versiones y por ser una de las pocas páginas que, sin ser home, producto o categoría, recibió cambios de metadata en el proyecto de automatización.

---

## 7. Limitaciones generales del análisis

- **Datos de campo de CrUX a nivel de origen**, no por URL individual. El tráfico de este cliente no supera los umbrales mínimos de CrUX para datos por URL, por lo que los Core Web Vitals reflejan el comportamiento agregado del dominio.
- **El conector nativo de GA4 no soporta segmentos de GA4.** Los segmentos creados en la interfaz de GA4 (Exploraciones) no son aplicables en Looker Studio. Los filtros equivalentes se replican mediante campos calculados y filtros de gráfico en el dashboard.
- **Retraso de 2–3 días en datos de GSC.** Las tablas de medición no reflejan los últimos días del período seleccionado.
- **Sin acceso a datos de nivel de usuario.** GA4 agrega los datos antes de exponerlos via conector; no se pueden hacer análisis de comportamiento individual de usuario en Looker Studio.

---

*Documento metodológico como parte del case study de portfolio. Los datos del cliente son reales pero el nombre de la empresa ha sido anonimizado en la versión pública del repositorio.*
