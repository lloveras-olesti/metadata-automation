# Data Dictionary — Dashboard de Medición SEO
**Cliente:** Llibres del Mirall (anonimizado en versión pública)  
**Herramienta:** Looker Studio  
**Fuentes de datos:** Google Analytics 4 (conector nativo), Google Search Console (conector nativo)  
**Última actualización:** Mayo 2026

---

## Índice

1. [Filtros globales aplicados](#1-filtros-globales-aplicados)
2. [Métricas de audiencia y comportamiento — fuente GA4](#2-métricas-de-audiencia-y-comportamiento--fuente-ga4)
3. [Métricas de ecommerce — fuente GA4](#3-métricas-de-ecommerce--fuente-ga4)
4. [Campos calculados — ratios de conversión](#4-campos-calculados--ratios-de-conversión)
5. [Métricas de rendimiento orgánico — fuente GSC](#5-métricas-de-rendimiento-orgánico--fuente-gsc)
6. [Dimensiones utilizadas](#6-dimensiones-utilizadas)
7. [Configuración de períodos por página](#7-configuración-de-períodos-por-página)

---

## 1. Filtros globales aplicados

Ambas fuentes de datos tienen aplicado un filtro permanente a nivel de conector que excluye el blog de la propiedad. El blog comparte propiedad GA4 y GSC con el ecommerce.

**Campo calculado de filtrado (aplicado en GA4 y GSC):**
```
CASE
  WHEN REGEXP_MATCH(Landing page, ".*/blog/.*") THEN "Blog"
  ELSE "Ecommerce"
END
```
**Filtro activo:** `Segmento contenido = Ecommerce`

Todas las métricas del dashboard se refieren exclusivamente al ecommerce, salvo indicación contraria.

---

## 2. Métricas de audiencia y comportamiento — fuente GA4

| Nombre en dashboard | Nombre nativo GA4 | Definición | Notas |
|---|---|---|---|
| Total de usuarios | `Total users` | Número de usuarios únicos que han tenido al menos una sesión en el período. Incluye usuarios nuevos y recurrentes. | |
| Usuarios nuevos | `New users` | Usuarios que han visitado la web por primera vez en el período. GA4 lo determina por la ausencia del evento `first_visit` previo. | Puede estar sobreestimado si los usuarios borran cookies. |
| Sesiones por usuario | `Sessions per user` | Ratio entre el total de sesiones y el total de usuarios. Indica la frecuencia media de visita. Fórmula: `Sessions / Total users`. | |
| Sesiones | `Sessions` | Número total de sesiones iniciadas en el período. Una sesión es un grupo de eventos de un mismo usuario en un intervalo de 30 minutos. | |
| Sesiones con interacción | `Engaged sessions` | Sesiones que cumplieron al menos uno de estos criterios: duración superior a 10 segundos, al menos 2 páginas vistas, o al menos un evento de conversión. | Métrica propia de GA4, no existe en Universal Analytics. |
| Porcentaje de rebote | `Bounce rate` | Porcentaje de sesiones que NO fueron sesiones con interacción. Fórmula: `1 - (Engaged sessions / Sessions)`. | La definición de rebote en GA4 es la inversa a UA: en GA4 un rebote es la ausencia de interacción, no una sesión de una sola página. |
| Eventos por sesión | `Events per session` | Número medio de eventos registrados por sesión. Fórmula: `Event count / Sessions`. | |
| Duración media de la sesión | `Average session duration` | Tiempo medio en segundos entre el primer y el último evento de cada sesión. | |

---

## 3. Métricas de ecommerce — fuente GA4

| Nombre en dashboard | Nombre nativo GA4 | Definición | Notas |
|---|---|---|---|
| Total de ingresos | `Total revenue` | Suma de ingresos de todas las transacciones completadas en el período, en euros. | Depende de que el evento `purchase` esté correctamente configurado con el parámetro `value` en PrestaShop. |
| Artículos comprados | `Items purchased` | Número total de unidades de producto compradas (no número de transacciones). Un pedido con 3 libros cuenta como 3. | |
| Artículos vistos | `Items viewed` | Número de veces que se ha disparado el evento `view_item`. Equivale a vistas de ficha de producto. | |
| Artículos añadidos al carrito | `Items added to cart` | Número de veces que se ha disparado el evento `add_to_cart`. | |

---

## 4. Campos calculados — ratios de conversión

Estos campos no existen nativamente en GA4. Se han creado como campos calculados en la fuente de datos de Looker Studio.

| Nombre en dashboard | Fórmula | Tipo | Definición |
|---|---|---|---|
| Add_to_Cart / View_item | `Artículos añadidos al carrito / NULLIF(Artículos vistos, 0)` | Porcentaje | De cada 100 vistas de producto, cuántas resultaron en un añadido al carrito. Mide la efectividad de las fichas de producto para generar intención de compra. |
| Purchase / Add_to_Cart | `Artículos comprados / NULLIF(Artículos añadidos al carrito, 0)` | Porcentaje | De cada 100 artículos añadidos al carrito, cuántos llegaron a comprarse. Mide la tasa de cierre del proceso de checkout. |
| Purchase / View_Item | `Artículos comprados / NULLIF(Artículos vistos, 0)` | Porcentaje | Tasa de conversión global desde vista de producto hasta compra. Combina las dos tasas anteriores en un solo indicador. Fórmula equivalente: `(Add_to_Cart/View_item) × (Purchase/Add_to_Cart)`. |
| % Sesiones con interacción | `Sesiones con interacción / NULLIF(Sesiones, 0)` | Porcentaje | Proporción de sesiones que cumplieron el criterio de interacción de GA4. Complementario al porcentaje de rebote. |

**Nota sobre NULLIF:** Todas las divisiones usan `NULLIF(denominador, 0)` para evitar errores en filas con valor cero. Cuando el denominador es 0, el campo devuelve NULL (celda vacía) en lugar de un error.

---

## 5. Métricas de rendimiento orgánico — fuente GSC

Estas métricas provienen del conector nativo de Google Search Console en Looker Studio. Los datos de GSC tienen un retraso típico de 2-3 días respecto a la fecha actual.

| Nombre en dashboard | Nombre nativo GSC | Definición | Notas |
|---|---|---|---|
| Clics (Url Clicks) | `Clicks` | Número de veces que un usuario hizo clic en un resultado de búsqueda de Google que llevaba a la web. | Solo recoge búsquedas web. No incluye Google Images ni Google News. |
| Impresiones (Impressions) | `Impressions` | Número de veces que una URL apareció en los resultados de búsqueda de Google, independientemente de si el usuario hizo clic o no. Se cuenta aunque el resultado no fuera visible sin hacer scroll. | |
| CTR (URL CTR) | `CTR` | Click-through rate. Porcentaje de impresiones que resultaron en un clic. Fórmula: `Clicks / Impressions`. | Un CTR bajo con muchas impresiones indica que el resultado aparece pero no convence al usuario para clicar (title/meta description poco atractivos, o posición muy baja). |
| Posición media (Average Position) | `Average position` | Posición media en los resultados de Google para las consultas en las que aparece esa URL. Posición 1 es el primer resultado orgánico. | Una posición más baja (número mayor) es peor. Al ordenar la tabla, usar orden ascendente para ver primero las URLs mejor posicionadas. La posición media puede ser engañosa si una URL aparece para queries muy dispares. |

**Configuración del conector GSC utilizada:** Search Console (URL), que permite segmentar por URL de destino además de por query. Tipo de búsqueda: Web.

---

## 6. Dimensiones utilizadas

| Dimensión | Fuente | Valores posibles relevantes | Uso en dashboard |
|---|---|---|---|
| Categoría de dispositivo | GA4 | `desktop`, `mobile`, `tablet` | Desglose de usuarios nuevos por dispositivo |
| Fuente de sesión | GA4 | `google`, `(direct)`, `bing`, `t.co`, etc. | Desglose de sesiones por origen de tráfico |
| Nombre del evento | GA4 | `view_item`, `add_to_cart`, `begin_checkout`, `purchase`, `remove_from_cart`, `page_view`, `first_visit`, etc. | Gráfico de volumen de eventos del embudo |
| Navegador | GA4 | `Chrome`, `Safari`, `Firefox`, `Samsung Internet`, etc. | Análisis de anomalía de febrero |
| Ciudad | GA4 | Variable | Análisis de anomalía de febrero |
| Landing Page | GA4 / GSC | URL completa de la página de entrada | Tablas de medición de URLs específicas |
| Query | GSC | Término de búsqueda introducido por el usuario | Tablas de medición de queries específicas |

---

## 7. Configuración de períodos por página

El dashboard combina períodos dinámicos y períodos fijos según la página. Los períodos fijos anulan el selector de fechas global.

| Página | Tipo de período | Configuración | Motivo |
|---|---|---|---|
| Visión general | Dinámico | Últimos 28 días con comparación período anterior | Monitorización continua del estado general |
| Embudo de conversión | Dinámico | Últimos 28 días con comparación período anterior | Seguimiento continuo de tasas de conversión |
| Medición cambios metadata — URLs | Mixto | Tabla dinámica: últimos 28 días / Tabla fija: abril 2026 | Comparar el estado actual con el período post-implementación de metadata |
| Medición cambios metadata — Queries | Mixto | Tabla dinámica: últimos 28 días / Tabla fija: marzo 2026 | Marzo como referencia estable previa a la anomalía de abril (Sant Jordi) |
| Análisis anomalía febrero | Fijo | Pendiente de definir | Investigación ad hoc de pico de tráfico directo |

**Nota sobre abril 2026:** Abril está excluido como período de referencia para queries debido al impacto de Sant Jordi (23 de abril), festividad del libro en Cataluña que genera un pico de tráfico atípico no representativo del rendimiento habitual.

---

*Documento generado como parte del case study de portfolio. Los datos del cliente son reales pero el nombre de la empresa ha sido anonimizado en la versión pública del repositorio.*
