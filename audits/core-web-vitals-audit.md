# Auditoría de Core Web Vitals — llibresdelmirall.com

**Cliente:** Llibres del Mirall  
**Fecha de auditoría:** 12 de mayo de 2026  
**Periodo de datos de campo (CrUX):** 13 de abril – 10 de mayo de 2026  
**Plataforma:** PrestaShop 1.6.x (tema personalizado)  
**Auditor:** Blai Lloveras 
**Versión del documento:** 2.0

---

## Tabla de contenidos

1. [Resumen ejecutivo](#1-resumen-ejecutivo)
2. [Alcance y metodología](#2-alcance-y-metodología)
3. [Resumen de métricas por page type](#3-resumen-de-métricas-por-page-type)
4. [Hallazgos por page type](#4-hallazgos-por-page-type)
5. [Análisis de causa raíz](#5-análisis-de-causa-raíz)
6. [Recomendaciones priorizadas](#6-recomendaciones-priorizadas)
7. [Consideraciones específicas de PrestaShop](#7-consideraciones-específicas-de-prestashop)
8. [Limitaciones del análisis](#8-limitaciones-del-análisis)
9. [Referencias](#9-referencias)

---

## 1. Resumen ejecutivo

La auditoría evalúa el rendimiento de tres page types representativos de `www.llibresdelmirall.com`: homepage, página de categoría y página de producto. El análisis combina datos de campo reales del Chrome UX Report (CrUX) con datos de laboratorio de la API de PageSpeed Insights (Lighthouse), más análisis directo del código fuente HTML.

**Veredicto global: Core Web Vitals SUSPENDIDO en mobile y desktop.**

El hallazgo más importante, identificado al inspeccionar el código fuente, es una **técnica de carga de imágenes que provoca LCP catastróficos en mobile**: todas las portadas de libros se renderizan como `background-image` CSS sobre un placeholder GIF de 1 píxel, en lugar de `<img src>` estándar. El navegador no puede descubrir ni priorizar estas imágenes hasta después de ejecutar todo el CSS, colapsando el LCP en mobile hasta 23–28 segundos.

Los tres problemas sistémicos son:

**CR-1 — Técnica CSS background-image para portadas (causa raíz del LCP catastrófico en mobile).** Todas las portadas de libros usan `<img src="/img/px.gif" style="background: url(cover.jpg)">`. El LCP resultante es de 23.1 s en homepage mobile y 28.1 s en producto mobile.

**CR-2 — 51 recursos síncronos en el `<head>` (render-blocking).** El tema carga 27 archivos CSS y 24 archivos JavaScript síncronos antes de renderizar nada. Lighthouse estima hasta 5.7 s de ahorro en mobile solo difiriendo los recursos no críticos.

**CR-3 — Imágenes sin WebP, sin caché, sin responsive serving.** Las portadas se sirven en JPG, sin cabeceras de caché, con payloads de 5–22 MB por página. Ahorro estimado de hasta 9.3 MB por página con optimización de imágenes.

INP y CLS están dentro del umbral Good y no son prioritarios (salvo el CLS borderline de 0.101 en la página de categoría desktop).

---

## 2. Alcance y metodología

### URLs analizadas

| # | Page type | URL |
|---|-----------|-----|
| 1 | Homepage | `https://www.llibresdelmirall.com/es/` |
| 2 | Categoría | `https://www.llibresdelmirall.com/es/229-poesia` |
| 3 | Producto | `https://www.llibresdelmirall.com/es/juvenil/124008-el-petit-princep-...html` |

### Herramientas utilizadas

- **PageSpeed Insights API v5** — datos de laboratorio (Lighthouse) y de campo (CrUX)
- **Código fuente HTML** — inspeccionado directamente para identificar patrones de carga
- **Chrome UX Report (CrUX)** — datos de campo reales, percentil 75, ventana de 28 días

### Tipos de datos

**Field data:** Mediciones reales de usuarios Chrome en percentil 75. Son los datos que Google usa para ranking. No hay CrUX por URL individual (tráfico insuficiente), por lo que todos los valores reflejan el comportamiento agregado del dominio.

**Lab data:** Tests sintéticos de Lighthouse ejecutados el 12/05/2026. Desktop: cable. Mobile: Moto G Power en 4G lento.

---

## 3. Resumen de métricas por page type

### 3.1 Datos de campo — Desktop y Mobile (origen, p75)

| Métrica | Desktop p75 | Estado | Mobile p75 | Estado |
|---------|-------------|--------|------------|--------|
| LCP | **2.5 s** | 🟡 Límite exacto | **2.9 s** | 🟡 NI |
| INP | **33 ms** | 🟢 Good | **98 ms** | 🟢 Good |
| CLS | **0.03** | 🟢 Good | **0** | 🟢 Good |
| FCP | **2.3 s** | 🟡 NI | **2.8 s** | 🟡 NI |
| TTFB | **1.5 s** | 🟡 NI | **1.7 s** | 🟡 NI |
| **CWV** | | ❌ FAILED | | ❌ FAILED |

### 3.2 Datos de laboratorio — Puntuaciones Lighthouse

| Page type | Desktop | Mobile |
|-----------|---------|--------|
| Homepage | **77 / 100** | **54 / 100** |
| Categoría | **86 / 100** | **58 / 100** |
| Producto | **64 / 100** | **56 / 100** |

### 3.3 Datos de laboratorio — Métricas completas

#### Desktop

| Métrica | Homepage | Categoría | Producto |
|---------|----------|-----------|---------|
| FCP | 1.3 s 🟡 | 1.4 s 🟡 | 1.4 s 🟡 |
| LCP | 2.0 s 🟡 | **1.4 s 🟢** | **4.7 s 🔴** |
| TBT | 40 ms 🟢 | 10 ms 🟢 | 140 ms 🟡 |
| CLS | 0.046 🟢 | **0.101 🟡** | 0.001 🟢 |
| Speed Index | **5.3 s 🔴** | 1.9 s 🟡 | 3.0 s 🔴 |
| TTI | 2.2 s 🟢 | 1.9 s 🟢 | **4.7 s 🔴** |
| TTFB (lab) | 90 ms ✅ | 210 ms ✅ | 70 ms ✅ |

#### Mobile

| Métrica | Homepage | Categoría | Producto |
|---------|----------|-----------|---------|
| FCP | 6.5 s 🔴 | 6.9 s 🔴 | 7.1 s 🔴 |
| LCP | **23.1 s 🔴** | **6.9 s 🔴** | **28.1 s 🔴** |
| TBT | 200 ms 🟡 | 70 ms 🟢 | 150 ms 🟡 |
| CLS | 0 🟢 | 0.062 🟢 | 0 🟢 |
| Speed Index | 8.3 s 🔴 | 7.9 s 🔴 | 7.1 s 🔴 |
| TTI | **23.7 s 🔴** | 9.5 s 🔴 | **28.1 s 🔴** |
| TTFB (lab) | 170 ms ✅ | 140 ms ✅ | 70 ms ✅ |

> **Nota sobre TTFB:** El TTFB en laboratorio (70–210 ms) es excelente, pero los datos de campo muestran 1.5–1.7 s. Esto indica que el servidor responde bien bajo condiciones controladas pero los usuarios reales experimentan latencia adicional, probablemente por ausencia de CDN y/o caché de página completa desactivada.

---

## 4. Hallazgos por page type

### 4.1 Homepage

**Puntuaciones:** Desktop 77/100 · Mobile 54/100

#### Issues de laboratorio

**Render-blocking** — desktop: ahorro estimado **1,220 ms**:
- `themes/llibresdelmirall/js/autoload/15-jquery.uniform-modified.js`
- `themes/llibresdelmirall/css/modules/blockcart/blockcart.css`
- `themes/llibresdelmirall/css/product_list.css`

**Render-blocking** — mobile: ahorro estimado **5,550 ms**:
- `themes/llibresdelmirall/css/global.css`
- `js/jquery/jquery-1.11.0.min.js`
- `themes/llibresdelmirall/js/modules/blockcart/ajax-cart.js`

El código fuente confirma 27 archivos CSS y 24 JS síncronos en el `<head>`.

**Imágenes sin WebP** — ahorro estimado **8,063 KiB** en desktop:
- `/covers/92050_1.jpg`, `/covers/115930_1.jpg`, `/covers/100956_1.jpg`

**Sin caché de imágenes** — ahorro estimado **22,607 KiB**:
- Las mismas portadas carecen de `Cache-Control`.

**Network payload total: 22,919 KiB** — el más alto de los tres page types auditados.

**Fonts bloqueantes** — ahorro estimado **970 ms** desktop / **350 ms** mobile:
- `fontawesome-webfont.woff?v=3.2.1` — sin `font-display: swap`
- `fonts.gstatic.com/s/lora/v37/0QIvMX1D_JOuMwr7I_FMl_E.woff2` — idem

**Logo sin dimensiones CSS estables (mobile):**
`/img/llibres-del-mirall-1418842022.jpg` tiene `width="160" height="188"` en el HTML, pero `class="img-responsive"` de Bootstrap anula estos valores con `height: auto`, causando reflow.

**Speed Index de 5.3 s en desktop** pese a LCP de 2.0 s: indica que las portadas de novedades (cargadas como CSS background) terminan de pintarse mucho más tarde que el elemento LCP.

**Causa raíz específica:** El LCP de 23.1 s en mobile se debe a que las imágenes de novedades/banners se cargan como `background-image` CSS. En mobile con conexión lenta, el navegador no descubre estas imágenes hasta que toda la cadena de CSS se ha procesado, acumulando decenas de segundos de retraso.

---

### 4.2 Página de categoría — Poesia

**Puntuaciones:** Desktop 86/100 · Mobile 58/100

#### Issues de laboratorio

**CLS: 0.101 en desktop** — borderline fail (umbral ≤ 0.1). Lighthouse detecta 3 layout shifts. Causas probables: logo `img-responsive` sin dimensiones CSS fijas, y carga de Google Fonts (Lora, Open Sans) sin `font-display: swap` causando reflow tipográfico.

**Render-blocking** — desktop: ahorro estimado **1,470 ms**:
- `themes/llibresdelmirall/css/global.css`
- `js/jquery/jquery-1.11.0.min.js`
- `themes/llibresdelmirall/js/modules/blockcart/ajax-cart.js`

**Render-blocking** — mobile: ahorro estimado **5,660 ms**:
- `themes/llibresdelmirall/js/autoload/15-jquery.uniform-modified.js`
- `themes/llibresdelmirall/js/modules/blocktopmenu/js/superfish-modified.js`
- `themes/llibresdelmirall/css/modules/blockcurrencies/blockcurrencies.css`

**Imágenes sin WebP** — ahorro estimado **9,306 KiB** (igual en desktop y mobile):
- `/covers/129046_1.jpg`, `/covers/129400_1.jpg`, `/covers/129619_1.jpg`

**Sin caché de imágenes** — ahorro estimado **19,167 KiB**.

**Network payload: 19,544 KiB** — idéntico en desktop y mobile: el sitio no sirve imágenes de menor resolución en mobile.

**Logo sin dimensiones funcionales (mobile):** mismo problema que en homepage.

**Fonts bloqueantes** — ahorro **950 ms** mobile / **340 ms** desktop.

**Forced reflow detectado** — JavaScript de la página ejecuta lecturas y escrituras de layout entrelazadas, forzando recálculos adicionales del navegador.

**Causa raíz específica:** El LCP desktop (1.4 s) es bueno porque la primera imagen del grid es descubierta a tiempo. En mobile (6.9 s) el render-blocking de JS/CSS en conexión lenta retrasa el FCP y con él el LCP. El CLS 0.101 es el problema más accionable a corto plazo: una corrección CSS de bajo esfuerzo lo resuelve.

---

### 4.3 Página de producto — El Petit Príncep

**Puntuaciones:** Desktop 64/100 · Mobile 56/100

> **El LCP de 28.1 s en mobile es el valor más grave de toda la auditoría.** El TTI coincide exactamente (28.1 s), indicando que el hilo principal permanece bloqueado hasta que la imagen del producto termina de cargarse.

#### Issues de laboratorio

**LCP de 4.7 s desktop / 28.1 s mobile** — imagen principal del producto cargada como CSS background:

```html
<!-- Código actual — imagen LCP no descubrible por el navegador -->
<img id="bigpic" src="/img/px.gif"
  style="background: url(/covers/124008_1.jpg) no-repeat; background-size: contain;"
  width="458" height="458" />
```

**Render-blocking** — desktop: ahorro estimado **1,260 ms**:
- `themes/llibresdelmirall/js/modules/blockcart/ajax-cart.js`
- `themes/llibresdelmirall/css/modules/blockcontact/blockcontact.css`
- `themes/llibresdelmirall/js/modules/blocktopmenu/js/hoverIntent.js`

**Render-blocking** — mobile: ahorro estimado **5,740 ms**:
- `themes/llibresdelmirall/css/global.css`
- `modules/llibresdelmirall/views/templates/front/css/llibresdelmirall-v7.css`
- `js/jquery/jquery-1.11.0.min.js`

La página de producto carga scripts adicionales respecto a categoría: `jquery.fancybox.js`, `jquery.idTabs.js`, `jquery.bxslider.js`, `productcomments.js`, `jquery.rating.pack.js`, `mailalerts.js` — todos síncronos en el `<head>`.

**Network payload: 4,913 KiB**:
- `/covers/124008_2.jpg` (imagen secundaria descargada aunque no sea visible)
- `/covers/124008_1.jpg` (imagen LCP)
- `themes/llibresdelmirall/css/global.css`

**Sin caché:** 4,630 KiB — ninguna imagen del producto tiene `Cache-Control`.

**Imagen sin dimensiones:** `/modules/productpaymentlogos/img/payment-logo.png` carece de atributos `width` y `height`.

**Forced reflow** — probablemente el inicializador del viewer de imágenes.

**Google Analytics Universal detectado** — `ga('create', 'UA-59958784-1', 'auto')`. Universal Analytics fue discontinuado por Google. Fuera del scope de CWV pero relevante para el seguimiento de conversiones.

**Causa raíz específica:** La imagen `bigpic` del producto es idéntica en técnica a las portadas del catálogo — CSS background sobre placeholder GIF. Es la causa directa del LCP de 28.1 s en mobile. Convertirla a `<img src>` con `fetchpriority="high"` es la acción de mayor impacto individual de toda la auditoría.

---

## 5. Análisis de causa raíz

### CR-1 — Técnica `replace-2x`: CSS background-image en lugar de `<img src>` (CRÍTICO)

**Impacto:** LCP catastrófico en mobile (23–28 s). Afecta a todos los page types.

Todo el catálogo usa este patrón para portadas de libros:

```html
<img class="replace-2x img-responsive"
  src="/img/px.gif"
  style="background: url(/covers/ID_1.jpg) no-repeat; background-size: contain; background-position: center;"
  width="150" height="175" />
```

Efectos en cascada sobre el rendimiento:

1. El navegador descarga `/img/px.gif` (placeholder de 1 píxel) inmediatamente y lo marca como "imagen cargada"
2. La URL real de la portada está en el atributo `style` inline, que el preloader HTML del navegador ignora
3. La imagen real solo se descubre cuando el CSS completo ha sido descargado, parseado y aplicado
4. No es posible usar `<link rel="preload as="image">` para anticipar su descarga
5. Lighthouse no puede identificarla como candidato LCP de la misma forma que un `<img src>`
6. En mobile (4G lento simulado), la cascada de descarga de la imagen real comienza 20–25 segundos después del inicio de la carga de página

La técnica probablemente se implementó para conseguir un efecto de imagen contenida sin distorsión (usando `background-size: contain`) o como parte de una técnica retina antigua. El mismo efecto visual se consigue con `<img>` estándar usando `object-fit: contain`.

### CR-2 — 51 recursos síncronos en el `<head>`

**Impacto:** FCP de 6.5–7.1 s en mobile. Render-blocking de hasta 5.7 s.

Inventario completo identificado en el código fuente (página de categoría como referencia):

**27 CSS síncronos en el `<head>`:** `global.css`, `highdpi.css`, `responsive-tables.css`, `uniform.default.css`, `product_list.css`, `category.css`, `scenes.css`, CSS de 8 módulos individuales (`blockcart`, `blockcurrencies`, `blocklanguages`, `blockcontact`, `blocknewsletter`, `blocksearch`, `blockuserinfo`, `blockviewed`), CSS de módulos adicionales (`themeconfigurator/hooks.css`, `blockwishlist`, `productcomments`, `newsletterpro`), CSS del menú (`blocktopmenu.css`, `superfish-modified.css`), CSS del módulo custom (`fancybox.css`, `llibresdelmirall-v7.css`, `llibresdelmirall-responsive-v7.css`, `pages-v6.css`), y dos llamadas a `fonts.googleapis.com`.

**24 JS síncronos en el `<head>`:** `jquery-1.11.0.min.js` (jQuery 1.11 de 2014), `jquery-migrate-1.2.1.min.js`, `jquery.easing.js`, `tools.js`, `global.js`, `10-bootstrap.min.js`, `15-jquery.total-storage.min.js`, `15-jquery.uniform-modified.js`, `category.js`/`product.js`, `ajax-cart.js`, `jquery.scrollTo.js`, `jquery.serialScroll.js`, `jquery.bxslider.js`, `blocknewsletter.js`, `ajax-wishlist.js`, `GoogleAnalyticActionLib.js`, tres scripts de `newsletterpro`, `hoverIntent.js`, `superfish-modified.js`, `blocktopmenu.js`, `app5.js`. En producto se añaden `fancybox.js`, `jquery.idTabs.js`, `productcomments.js`, `jquery.rating.pack.js`, `mailalerts.js`.

Ninguno usa `defer` ni `async`. El navegador debe descargar, parsear y ejecutar cada uno antes de pintar cualquier píxel visible.

### CR-3 — Imágenes sin WebP, sin caché, sin responsive serving

**Impacto:** Network payloads de 4.9–22.9 MB por página. Descarga repetida en cada visita.

- Portadas en JPG sin conversión a WebP (ahorro estimado 9–8 MB por página)
- Sin cabeceras `Cache-Control` — las mismas imágenes se descargan en cada visita
- Sin `srcset` ni imágenes responsive — misma imagen en desktop y mobile
- Imagen secundaria del producto (`covers/124008_2.jpg`) descargada aunque el usuario no interactúe con la galería

### CR-4 — Google Fonts bloqueantes sin `font-display: swap`

**Impacto:** FCP retrasado hasta 970 ms (desktop). FOIT en todas las páginas.

```html
<!-- Actual — bloqueante, sin font-display -->
<link href="//fonts.googleapis.com/css?family=Lora:400,700" rel="stylesheet" />
<link href="//fonts.googleapis.com/css?family=Open+Sans:300,600&subset=latin,latin-ext" rel="stylesheet" />
```

Sin `font-display: swap`, el texto permanece invisible hasta que las fuentes cargan.

### CR-5 — Logo sin dimensiones CSS estables (CLS)

**Impacto:** Contribuye al CLS de 0.101 en página de categoría desktop.

El logo tiene `width="160" height="188"` en HTML, pero `class="img-responsive"` de Bootstrap aplica `max-width: 100%; height: auto` que puede invalidar las dimensiones antes de que el CSS del tema aplique sus reglas definitivas, causando un reflow visible.

---

## 6. Recomendaciones priorizadas

### 🔴 Prioridad 1 — Impacto crítico

#### R1 — Migrar portadas de libros de CSS background a `<img src>` estático

**Métricas afectadas:** LCP mobile (−20–25 s), Speed Index  
**Ahorro estimado:** LCP de 28 s → objetivo < 3 s en mobile  
**Esfuerzo:** Medio — modificar plantillas Smarty del tema  
**Page types:** Todos

Cambiar el patrón de imagen en las plantillas `.tpl` del tema:

```html
<!-- ANTES (actual — imagen no descubrible) -->
<img class="replace-2x img-responsive"
  src="/img/px.gif"
  style="background: url(/covers/129619_1.jpg) no-repeat; background-size: contain; background-position: center;"
  width="150" height="175" />

<!-- DESPUÉS — para imágenes below-the-fold (lazy loading) -->
<img src="/covers/129619_1.jpg"
  alt="Título del libro"
  width="150" height="175"
  loading="lazy"
  style="object-fit: contain;" />

<!-- DESPUÉS — para la PRIMERA imagen visible (LCP): no lazy, fetchpriority -->
<img src="/covers/129619_1.jpg"
  alt="Título del libro"
  width="150" height="175"
  fetchpriority="high"
  style="object-fit: contain;" />
```

Plantillas a modificar:
- `templates/catalog/listing/product-list.tpl` — primer `<li>` del loop de productos (la imagen LCP en categoría)
- `templates/catalog/product.tpl` — imagen `bigpic` (LCP en producto)
- Template de novedades en homepage (el banner/imagen hero o primera portada visible)

#### R2 — Diferir JavaScript no crítico con `defer`

**Métricas afectadas:** FCP, Speed Index  
**Ahorro estimado:** 1,220 ms desktop / 5,550–5,740 ms mobile  
**Esfuerzo:** Medio — verificar dependencias antes de diferir  
**Page types:** Todos

Scripts que pueden diferirse sin romper funcionalidad de render:
- `15-jquery.uniform-modified.js` — estética de formularios
- `blocknewsletter.js`, `ajax-wishlist.js`
- `GoogleAnalyticActionLib.js`
- `newsletterpro/newsletter.js`, `init.js`, `my_account.js`
- `hoverIntent.js`, `superfish-modified.js`, `blocktopmenu.js`
- `jquery.bxslider.js`, `jquery.scrollTo.js`, `jquery.serialScroll.js`

Scripts que **no deben diferirse** sin un rediseño más profundo:
- `jquery-1.11.0.min.js` — dependencia de todo lo demás
- `ajax-cart.js` — inicializa el carrito AJAX referenciado en el HTML
- `global.js` — inicialización del tema

---

### 🟠 Prioridad 2 — Impacto alto / Esfuerzo bajo

#### R3 — Añadir `font-display: swap` y `preconnect` a Google Fonts

**Métricas afectadas:** FCP (−340–970 ms), CLS  
**Esfuerzo:** Bajo — un parámetro en la URL + dos `<link>` en el `<head>`

```html
<!-- Añadir preconnect ANTES de las llamadas a Google Fonts -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<!-- Añadir &display=swap a las URLs de Google Fonts -->
<link href="//fonts.googleapis.com/css?family=Lora:400,700&display=swap" rel="stylesheet" />
<link href="//fonts.googleapis.com/css?family=Open+Sans:300,600&subset=latin,latin-ext&display=swap" rel="stylesheet" />
```

#### R4 — Configurar `Cache-Control` para imágenes de portadas

**Métricas afectadas:** Network payload en visitas recurrentes (−19–22 MB)  
**Esfuerzo:** Bajo — configuración de servidor

```apache
<LocationMatch "^/covers/">
    Header set Cache-Control "max-age=31536000, immutable"
</LocationMatch>
```

Las portadas de libros son contenido estático que no cambia. Un año de caché (`max-age=31536000`) es apropiado.

#### R5 — Fijar dimensiones CSS del logo para eliminar CLS

**Métricas afectadas:** CLS en categoría (0.101 → objetivo < 0.1)  
**Esfuerzo:** Bajo — añadir dos líneas de CSS

```css
/* En CSS del tema */
#header_logo img.logo {
    width: 160px;
    height: 188px;
}
```

Esto evita que Bootstrap `img-responsive` invalide las dimensiones declaradas en el HTML antes de que el CSS del tema las reafirme, eliminando el reflow.

#### R6 — Activar caché de página completa

**Métricas afectadas:** TTFB en usuarios reales (objetivo: de 1.5 s → < 0.8 s)  
**Esfuerzo:** Bajo — activación en Back Office

Back Office → Parámetros Avanzados → Rendimiento → Caché → activar `ps_pagecache`. Excluir: páginas de carrito, checkout, mi cuenta, y páginas con sesión de usuario activa.

---

### 🟡 Prioridad 3 — Impacto medio / Esfuerzo medio

#### R7 — Convertir portadas a WebP

**Métricas afectadas:** LCP, network payload (−9 MB estimados en páginas de categoría)  
**Esfuerzo:** Medio

Opciones: (a) módulo PrestaShop de optimización de imágenes que genere WebP automáticamente, (b) configuración de servidor con `mod_rewrite` para servir WebP cuando el browser lo soporte, (c) Cloudflare Polish (si se activa CDN).

#### R8 — No descargar imagen secundaria del producto sin interacción

**Métricas afectadas:** Network payload en producto (−imagen `covers/124008_2.jpg`)  
**Esfuerzo:** Bajo — añadir `loading="lazy"` a thumbnails tras implementar R1

Una vez las imágenes sean `<img src>` estático, los thumbnails adicionales de producto se marcan con `loading="lazy"`.

#### R9 — Implementar CDN para assets estáticos

**Métricas afectadas:** TTFB, velocidad de descarga de CSS/JS/imágenes  
**Esfuerzo:** Medio — configuración de Cloudflare (plan gratuito suficiente para este caso)

#### R10 — Consolidar y minificar CSS/JS (CCC de PrestaShop)

**Métricas afectadas:** FCP, número de peticiones HTTP  
**Esfuerzo:** Medio — activar CCC en Back Office y verificar que no rompe módulos

Back Office → Parámetros Avanzados → Rendimiento → CCC. Reduce los 27 CSS a 1–2 archivos combinados.

> ⚠️ El CCC de PrestaShop 1.6 a veces genera conflictos con módulos. Probar siempre en staging.

---

### 🟢 Prioridad 4 — Alto esfuerzo o impacto secundario en el contexto actual

#### R11 — Actualizar jQuery 1.11 a versión moderna

**Esfuerzo:** Muy alto — puede romper módulos. jQuery 1.11.0 (2014) es ~96 KB minificado; jQuery 3.x es ~30% más ligero y notablemente más rápido. Actualizar en PrestaShop 1.6 requiere verificar compatibilidad de todos los módulos activos.

#### R12 — Añadir `width` y `height` a `payment-logo.png`

**Esfuerzo:** Mínimo — una línea en el template del módulo `productpaymentlogos`.

---

## 7. Consideraciones específicas de PrestaShop

### 7.1 La técnica `replace-2x` (R1 — crítico)

El patrón `src="/img/px.gif"` con `background: url(cover.jpg)` es específico del tema personalizado `llibresdelmirall` (no es comportamiento estándar de PrestaShop). Probablemente fue implementado para un efecto visual de imagen contenida o para soporte de pantallas Retina antiguo.

Archivos Smarty a localizar y modificar:
- Buscar `replace-2x` o `px.gif` en `/themes/llibresdelmirall/templates/`
- Las plantillas afectadas son principalmente `catalog/listing/product-list.tpl` y `catalog/product.tpl`
- El efecto visual de `background-size: contain` se puede replicar con `object-fit: contain` en un `<img>` estándar

### 7.2 `defer` en PrestaShop 1.6 (R2)

```php
// En el .php del módulo, en hookHeader() o hookDisplayHeader()
$this->context->controller->registerJavascript(
    'module-blocknewsletter-front',
    'themes/mitheme/js/modules/blocknewsletter/blocknewsletter.js',
    ['position' => 'bottom', 'defer' => 'defer']
);
```

Para scripts del tema (no módulos), modificar directamente `header.tpl` o el controlador del tema.

### 7.3 Google Fonts self-hosted (alternativa a R3)

Para eliminar la petición de terceros a `fonts.googleapis.com` y ganar ~100–200 ms adicionales:

```html
<link rel="preload" href="/themes/llibresdelmirall/font/lora-400.woff2" as="font" type="font/woff2" crossorigin>
<style>
@font-face {
  font-family: 'Lora';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('/themes/llibresdelmirall/font/lora-400.woff2') format('woff2');
}
</style>
```

Los archivos WOFF2 se descargan de [Google Fonts Helper](https://gwfh.mranftl.com/).

### 7.4 Caché FPC: exclusiones recomendadas (R6)

```
Excluir de caché:
- /es/carrito
- /es/pago*
- /es/mi-cuenta*
- /es/identificarse*
- Cualquier URL con parámetro ?token=
- Requests con cookie de sesión activa (customer_id)
```

---

## 8. Limitaciones del análisis

- **Sin acceso al Back Office ni al servidor.** No se ha verificado la versión exacta de PHP, configuración de Apache/Nginx, ni qué módulos están activos.
- **Datos de campo a nivel de origen.** No hay CrUX por URL individual.
- **Una sola ejecución de laboratorio** (12/05/2026). Los valores de LCP especialmente pueden variar según el estado de caché del servidor en el momento del test.
- **La técnica `replace-2x` puede tener dependencias JavaScript** no identificadas. Antes de eliminarla, verificar si algún script la usa para zoom, galería u otras funcionalidades.
- **Universal Analytics (UA-59958784-1) detectado** — discontinuado por Google. Fuera del scope CWV, pero los datos de conversión pueden no estar registrándose correctamente.
- **Auditoría basada en muestra de 3 URLs.** Para una cobertura global del sitio, complementar con el informe CWV de Google Search Console.

---

## 9. Referencias

- [Core Web Vitals — web.dev](https://web.dev/articles/vitals/)
- [Largest Contentful Paint — web.dev](https://web.dev/lcp/)
- [¿Qué elementos se consideran para LCP? — web.dev](https://web.dev/lcp/#what-elements-are-considered)
- [Optimize LCP — web.dev](https://web.dev/optimize-lcp/)
- [fetchpriority attribute — web.dev](https://web.dev/priority-hints/)
- [font-display — MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/font-display)
- [Cumulative Layout Shift — web.dev](https://web.dev/cls/)
- [Chrome User Experience Report — developer.chrome.com](https://developer.chrome.com/docs/crux)
- [PageSpeed Insights API — developers.google.com](https://developers.google.com/speed/docs/insights/v5/about)
- [PrestaShop Performance — devdocs.prestashop-project.org](https://devdocs.prestashop-project.org/)
