# Insights y análisis — Dashboard de Medición SEO
**Cliente:** Llibres del Mirall (anonimizado en versión pública)  
**Período principal de análisis:** Enero 2025 – Mayo 2026  
**Última actualización:** Mayo 2026

> Este documento recoge los hallazgos analíticos derivados del dashboard de Looker Studio, complementados con contexto de negocio y con los resultados de las auditorías de Core Web Vitals y Schema Markup. No es un documento técnico de implementación — para eso, ver `/audits/`. Es un documento de interpretación: qué dicen los datos y qué implican para la estrategia.

---

## Índice

1. [Anomalía de tráfico — Febrero 2026](#1-anomalía-de-tráfico--febrero-2026)
2. [Embudo de conversión — Estado y diagnóstico](#2-embudo-de-conversión--estado-y-diagnóstico)
3. [Tasa de rebote y su relación con el rendimiento técnico](#3-tasa-de-rebote-y-su-relación-con-el-rendimiento-técnico)
4. [Rendimiento SEO orgánico — Posicionamiento y oportunidades](#4-rendimiento-seo-orgánico--posicionamiento-y-oportunidades)
5. [Hipótesis de trabajo para los próximos meses](#5-hipótesis-de-trabajo-para-los-próximos-meses)

---

## 1. Anomalía de tráfico — Febrero 2026

### Descripción del fenómeno

Durante febrero de 2026 se registró un volumen de usuarios nuevos completamente atípico: más de 90.000 usuarios nuevos frente a una media mensual de 4.000–5.000. El fenómeno duró aproximadamente 20 días, con dos picos diferenciados:

- **Pico principal:** 11–16 de febrero (~80.000 usuarios en 6 días)
- **Pico secundario:** 18–20 de febrero (volumen menor)
- **Cola residual:** resto de febrero y principios de marzo (~15 usuarios diarios de origen dudoso, actualmente normalizado)

El incremento fue completamente invisible en los ingresos: el total de ingresos de febrero se mantuvo dentro de rangos normales. Esto descartó desde el primer momento que se tratara de tráfico real con intención de compra.

### Metodología de investigación

La investigación siguió un proceso de eliminación de hipótesis mediante la segmentación progresiva del tráfico anómalo:

**Paso 1 — Descarte de problema de tracking:** Se verificó en GA4 → Diagnósticos de datos que no había alertas de configuración activas en febrero. No hubo cambios en la web en ese período que pudieran explicar un artefacto de medición.

**Paso 2 — Análisis de landing pages:** El tráfico anómalo aterrizaba mayoritariamente en la homepage y en un número pequeño de páginas de producto. Nadie escribe a mano URLs de fichas de producto específicas, lo que descartó tráfico orgánico directo genuino.

**Paso 3 — Perfil del usuario:**
- **Canal:** 100% tráfico directo
- **Dispositivo:** 100% desktop
- **Navegador:** Google Chrome exclusivamente
- **Geografía:** países sin relación histórica con el cliente — Alemania, Hong Kong, Singapur, entre otros. El cliente recibe tráfico principalmente de España, EEUU y Latinoamérica.

**Paso 4 — Comportamiento en sesión:**
- Duración media de sesión durante los picos: prácticamente 0 segundos
- Único evento registrado: `first_visit`
- Sin ningún evento de interacción (sin `page_view` adicionales, sin `view_item`, sin `add_to_cart`)

### Conclusión

La convergencia de todos los indicadores apunta con alta probabilidad a **tráfico de bot o spider automatizado**, no a usuarios humanos reales. El perfil es consistente con scrapers de contenido o crawlers de terceros que:

- Ejecutan solicitudes HTTP desde IPs distribuidas geográficamente (técnica habitual para evitar bloqueos por IP)
- Utilizan Chrome como user-agent para parecer tráfico legítimo
- No ejecutan JavaScript completo o lo hacen de forma parcial, lo que explica la ausencia de eventos más allá de `first_visit` y la duración de 0 segundos

La ausencia de impacto en ingresos y la normalización espontánea del tráfico a partir de finales de febrero son coherentes con esta hipótesis. No se detectó un vector de ataque conocido ni un daño operativo directo al sitio.

### Implicaciones para el análisis histórico

Cualquier comparativa de usuarios o sesiones que incluya febrero 2026 como período de referencia producirá métricas distorsionadas. Al elaborar comparativas anuales o tendencias de largo plazo en el dashboard, febrero 2026 debe anotarse como dato atípico o excluirse del rango de comparación.

---

## 2. Embudo de conversión — Estado y diagnóstico

### Los números del embudo (últimos 28 días)

| Evento | Volumen | Tasa respecto al paso anterior |
|--------|---------|-------------------------------|
| `view_item` | 3.027 | — (punto de entrada del embudo) |
| `add_to_cart` | 385 | **12,72 %** |
| `begin_checkout` | 362 | **94,03 %** |
| `purchase` | 100 | **27,62 %** |

*Nota: `remove_from_cart` registra 54 eventos, lo que representa apenas un 14% del total de add_to_cart. El abandono pasivo del carrito es el fenómeno dominante, no la eliminación activa.*

### Interpretación contextualizada

La tasa de `add_to_cart` sobre `view_item` del 12,72% aislada del contexto parece baja. En ecommerce estándar, una tasa del 5–10% ya se considera normal para productos de precio medio-alto, y las referencias del sector para libros de segunda mano de colección son aún menores. El contexto de negocio explica el número: los clientes de Llibres del Mirall son mayoritariamente coleccionistas y bibliófilos que navegan extensamente el catálogo con actitud de exploración, no de compra inmediata. El comportamiento digital refleja el comportamiento que se observa en la tienda física: se miran muchos libros y se compra uno o dos. La tasa del 12,72%, en este contexto, no es una señal de alarma.

El dato realmente significativo está en otro punto del embudo. El 94% de los usuarios que añaden al carrito inician el checkout — una tasa extraordinariamente alta que indica una intención de compra muy real y comprometida en ese segmento de usuario. Sin embargo, de ese 94% que inicia el proceso, solo el 27,62% completa la compra.

**El problema no es la intención. El problema es la fricción en el checkout.**

El abandono no es pasivo — el `remove_from_cart` bajo (14% del add_to_cart) lo confirma. Los usuarios quieren comprar, inician el proceso, y algo durante el checkout los detiene.

### Mapa de fricción del proceso de compra

El checkout actual tiene cuatro pasos secuenciales, y cada uno presenta una fricción identificable:

**Paso 1 — Inicio de sesión o creación de cuenta (obligatorio).** No existe opción de compra como invitado. Un usuario nuevo que llega por primera vez tiene que registrarse antes de poder continuar. El registro en sí es simple — no requiere verificación de email — pero el paso existe y es una barrera documentada en la literatura de ecommerce. Las plataformas que han eliminado el checkout obligatorio con cuenta reportan mejoras de conversión de entre el 20% y el 45%.

**Paso 2 — Pantalla de dirección (con scroll oculto).** Una vez identificado, el usuario llega a la pantalla de dirección de envío. El botón de confirmar no es visible al cargar la página — requiere hacer scroll hacia abajo para encontrarlo. Este problema de UX afecta a cualquier usuario, pero es especialmente relevante en el perfil demográfico del cliente: la base de clientes tiene una media de edad estimada de 50 años, y los usuarios de mayor edad tienen estadísticamente una menor probabilidad de hacer scroll espontáneo cuando no ven una acción clara. El botón oculto probablemente genera una tasa de abandono silenciosa en este paso que los datos agregados no permiten distinguir del abandono total de checkout.

**Paso 3 — Selección de opción de envío (con scroll oculto).** El usuario escoge entre cinco opciones de envío, incluyendo recogida en tienda. De nuevo, el botón de confirmación requiere scroll. La misma fricción del paso anterior se repite aquí.

**Paso 4 — Precio de envío desconocido hasta el día siguiente (crítico).** Este es el hallazgo más importante del análisis del embudo. El precio final del envío no se calcula ni se muestra durante el proceso de compra — se determina al día siguiente en función del peso real de los productos y la opción de envío elegida, y se comunica al cliente por email o desde el panel de pedidos. El usuario finaliza el proceso sin saber cuánto va a pagar en total.

Desde la perspectiva del usuario, esto invierte la lógica esperada de una compra online: normalmente se elige, se ve el precio final y se paga. Aquí se elige, se compromete, y se espera a que alguien le diga cuánto debe. Para un cliente que está comprando un libro de 50€, descubrir al día siguiente que el envío añade 8–12€ puede generar cancelaciones o, en compras futuras, directamente el abandono del proceso en el momento en que recuerda esta experiencia.

### La oportunidad real

El segmento de usuario que añade al carrito tiene intención de compra alta y demostrada. La tasa de checkout del 27,62% no refleja falta de interés — refleja un proceso que pone demasiadas barreras entre la intención y la acción.

Algunas de estas barreras son solucionables con cambios de configuración en PrestaShop (habilitar checkout como invitado, ajustar el diseño para que los botones sean visibles sin scroll). El problema del precio de envío desconocido es estructuralmente más complejo porque responde a una realidad operativa real: los libros varían mucho de peso y el cálculo requiere el producto físico. Una solución parcial sería mostrar durante el checkout un rango orientativo de precio de envío por opción, o comunicar explícitamente que el precio se confirma en 24h y que el usuario puede cancelar sin coste si no está de acuerdo. Esto no elimina la fricción, pero reduce la incertidumbre y gestiona la expectativa del usuario.

---

## 3. Tasa de rebote y su relación con el rendimiento técnico

### El dato

La tasa de rebote actual es del **78,30%**. En la definición de GA4, esto significa que el 78% de las sesiones no cumplen ninguno de los criterios de interacción: no superan los 10 segundos, no generan una segunda pageview y no registran ningún evento de conversión.

### La hipótesis más probable: rendimiento técnico en mobile

La auditoría de Core Web Vitals (mayo 2026) documentó tiempos de carga extremos en dispositivos móviles: **LCP de 23,1 segundos en homepage** y **28,1 segundos en páginas de producto**. La causa identificada es una técnica de carga de imágenes mediante `background-image` CSS que impide al navegador descubrir y priorizar las portadas de libros hasta que todo el CSS ha sido procesado.

Para contextualizar: según datos de Google, el 53% de los usuarios móviles abandona una página que tarda más de 3 segundos en cargar. Con LCP de 23–28 segundos en mobile, es estadísticamente esperable que la mayoría de usuarios móviles abandone antes de que la página termine de renderizarse, sin generar ningún evento de interacción. Esto se registra directamente como rebote en GA4.

La conexión entre CWV y la tasa de rebote no es una hipótesis especulativa — es la consecuencia lógica de los tiempos de carga medidos. Si las recomendaciones R1 (migración de CSS background-image a `<img>` estándar) y R2 (diferimiento de recursos bloqueantes) de la auditoría CWV se implementan, cabe esperar una reducción significativa de la tasa de rebote, especialmente en el segmento móvil.

### Implicación secundaria: ranking SEO

Los Core Web Vitals son un factor de ranking en Google desde 2021. El sitio suspende los CWV tanto en desktop como en mobile según los datos de campo de CrUX. Esto no solo afecta la experiencia del usuario — afecta directamente la capacidad del sitio de posicionarse en queries competidas, especialmente en búsquedas con intención de compra donde Google tiende a favorecer páginas con buena experiencia de página.

---

## 4. Rendimiento SEO orgánico — Posicionamiento y oportunidades

### Estado actual

El posicionamiento orgánico actual del sitio es funcional pero concentrado. Las métricas de GSC muestran que la homepage en español capta la mayor parte de los clics orgánicos, con un CTR del 3,39–3,47% sobre ~8.800–9.200 impresiones mensuales para queries relacionadas con libros de segunda mano en Barcelona. El posicionamiento en primera página para estas queries es el resultado de una optimización de metadata realizada hace dos años, que demostró que el sitio es capaz de posicionarse competitivamente cuando la metadata está bien trabajada.

El problema es la escala: ese éxito está concentrado en la homepage y en un número muy pequeño de URLs. Las páginas de categoría y de producto tienen posicionamiento muy pobre o nulo para sus queries específicas.

### El precedente que valida la estrategia

La optimización de la homepage para queries como *libros de segunda mano Barcelona* y *libros antiguos Barcelona* pasó de posicionamiento nulo a primera página. Este resultado es el argumento más sólido para extender la misma metodología a categorías y productos: no es una hipótesis, es un resultado probado en el mismo dominio y la misma plataforma.

El proyecto de automatización de metadata (repositorio: `automation/`) escala exactamente esta lógica a las 5.890 páginas de producto y 904 categorías del catálogo. La medición del impacto de esa implementación está en curso.

### Las oportunidades por tipo de URL

**Páginas de categoría:** Queries como *poesía catalana de segunda mano* o *novela negra barcelona antigua* tienen potencial de tráfico cualificado con baja competencia. Actualmente, páginas como `/es/229-poesia` tienen 0 clics con posición media de 97 — prácticamente invisibles. La mejora de metadata de categoría es la palanca de mayor impacto potencial a corto plazo.

**Páginas de producto específicas:** Los datos de GSC muestran algunos productos con CTRs muy altos cuando aparecen (66,67% en el caso de *Le Petit Prince* en la edición de Riga), lo que indica que cuando el sitio se posiciona para una búsqueda de libro específico, convierte muy bien en clic. El reto es conseguir posicionamiento para más productos.

**El factor limitante transversal:** Las páginas de categoría con mejores oportunidades de keywords son también las páginas con peor rendimiento de Core Web Vitals (CLS borderline en desktop, LCP catastrófico en mobile). Es difícil ganar posicionamiento sostenible en queries de media-alta competencia con CWV suspendidos. La mejora técnica y la optimización de metadata son estrategias complementarias, no alternativas.

### Schema markup: la oportunidad de diferenciación visual

La auditoría de schema (mayo 2026) identificó que el sitio no implementa `itemCondition: UsedCondition` en ninguna página de producto. Para una librería de segunda mano, este es el schema más relevante posible: Google muestra el estado del producto (*Used*) directamente en el resultado de búsqueda como rich result, diferenciando visualmente el listado de los resultados de librería nueva. En un mercado donde el usuario busca específicamente libros de segunda mano, este diferenciador visual puede tener un impacto significativo en CTR.

---

## 5. Hipótesis de trabajo para los próximos meses

A modo de resumen, los hallazgos del dashboard y las auditorías convergen en tres palancas prioritarias, ordenadas por esfuerzo estimado de menor a mayor:

**Palanca 1 — Reducir fricción en checkout (impacto: conversión, esfuerzo: variable).** El checkout presenta cuatro fricciones identificadas. Dos son solucionables con cambios de configuración o diseño sin desarrollo complejo: habilitar la opción de compra como invitado en PrestaShop, y ajustar el layout de los pasos de dirección y envío para que los botones de confirmación sean visibles sin scroll. La tercera fricción — el precio de envío desconocido hasta el día siguiente — responde a una limitación operativa real y no tiene solución directa, pero puede mitigarse comunicando explícitamente durante el checkout que el precio se confirma en 24h y que el cliente puede cancelar sin coste. El potencial de mejora es alto: el usuario que llega a `begin_checkout` ya tiene intención de compra confirmada, y cualquier reducción de abandono en ese punto se traduce directamente en transacciones adicionales.

**Palanca 2 — Mejorar rendimiento técnico, especialmente en mobile (impacto: rebote + ranking, esfuerzo: medio-alto).** La recomendación R1 de la auditoría CWV (migrar de CSS background-image a `<img>` estándar) es el cambio de mayor impacto pero requiere modificación de plantillas Smarty. Las recomendaciones R3 y R6 (Google Fonts y caché de página) son de bajo esfuerzo y pueden implementarse en horas.

**Palanca 3 — Medir el impacto de la implementación de metadata (impacto: posicionamiento, esfuerzo: bajo — está en curso).** La implementación automática de metadata en las 5.890 páginas de producto y 904 categorías está completada. Los efectos de posicionamiento se empezarán a manifestar en 4–8 semanas. El dashboard de medición tiene configuradas las tablas de seguimiento para capturar este impacto en las URLs y queries monitorizadas.

---

*Documento de análisis como parte del case study de portfolio. Los datos del cliente son reales pero el nombre de la empresa ha sido anonimizado en la versión pública del repositorio.*
