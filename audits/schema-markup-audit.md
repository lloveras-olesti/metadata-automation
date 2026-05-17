# Auditoría de Schema Markup — llibresdelmirall.com

**Cliente:** Llibres del Mirall  
**Fecha de auditoría:** 13 de mayo de 2026  
**Plataforma:** PrestaShop 1.6.x (tema personalizado)  
**Auditor:** Blai Lloveras 
**Versión del documento:** 2.0

---

## Tabla de contenidos

1. [Resumen ejecutivo](#1-resumen-ejecutivo)
2. [Alcance y metodología](#2-alcance-y-metodología)
3. [Inventario de schema por page type](#3-inventario-de-schema-por-page-type)
4. [Hallazgos detallados](#4-hallazgos-detallados)
5. [Oportunidades de rich results no activadas](#5-oportunidades-de-rich-results-no-activadas)
6. [Recomendaciones priorizadas](#6-recomendaciones-priorizadas)
7. [Propuestas de implementación JSON-LD](#7-propuestas-de-implementación-json-ld)
8. [Consideraciones específicas de PrestaShop](#8-consideraciones-específicas-de-prestashop)
9. [Limitaciones del análisis](#9-limitaciones-del-análisis)
10. [Referencias](#10-referencias)

---

## 1. Resumen ejecutivo

La auditoría analiza el schema markup de tres page types representativos de `www.llibresdelmirall.com`: homepage, página de categoría y página de producto. La fuente de datos combina análisis directo del código fuente HTML y los resultados del Google Rich Results Test.

**Veredicto: Markup técnicamente válido pero estratégicamente incompleto.**

El Rich Results Test de Google devuelve **0 errores y 0 advertencias** en las tres páginas auditadas. Sin embargo, la ausencia de errores no equivale a un uso óptimo del schema. El markup actual pasa la validación porque implementa el mínimo requerido por Google para reconocer un elemento `Product`, pero deja sin activar la mayoría de las oportunidades reales de rich results.

Los tres problemas principales son:

**P-1 — Ausencia de `schema:Book` e `itemCondition` (oportunidad crítica perdida).** El sitio es una librería de segunda mano. El tipo correcto para las páginas de producto es `schema:Book`, subtipo de `schema:Product` con propiedades específicas para libros. Más importante aún: la propiedad `itemCondition` con el valor `UsedCondition` es exactamente lo que Google muestra en las SERPs para productos de segunda mano como rich result. Ninguna página la implementa.

**P-2 — Precio en formato inválido.** El `itemprop="price"` contiene `"50,00 €"` en lugar del valor numérico limpio `"50.00"` que exige Google. Aunque el Rich Results Test no lo penaliza actualmente, es técnicamente incorrecto y puede provocar errores de parseo en otros motores de búsqueda.

**P-3 — Homepage sin schema de organización ni sitelinks searchbox.** La homepage no implementa `Organization` (nombre, dirección, contacto, redes sociales) ni `WebSite` con `SearchAction`, perdiendo los dos rich results más accesibles para una homepage de ecommerce.

**P-4 — Formato Microdata en lugar de JSON-LD.** Google recomienda JSON-LD como formato preferido. El markup actual usa Microdata embebido en el HTML del tema, lo que lo hace difícil de mantener, actualizar y extender sin tocar las plantillas.

---

## 2. Alcance y metodología

### URLs analizadas

| # | Page type | URL |
|---|-----------|-----|
| 1 | Homepage | `https://www.llibresdelmirall.com/es/` |
| 2 | Categoría | `https://www.llibresdelmirall.com/es/229-poesia` |
| 3 | Producto | `https://www.llibresdelmirall.com/es/juvenil/124008-el-petit-princep-...html` |

### Herramientas utilizadas

- **Google Rich Results Test** (`search.google.com/test/rich-results`) — veredicto oficial de Google sobre validez y elegibilidad para rich results
- **Análisis de código fuente HTML** — inventario completo de tipos y propiedades implementadas, detección de datos presentes en el HTML pero ausentes del schema
- **schema.org** — referencia para propiedades obligatorias y recomendadas

### Tipos de datos y sus fuentes

El Rich Results Test valida si el markup es técnicamente correcto según las reglas de Google para mostrar rich results en las SERPs. No evalúa si el markup está incompleto o si se podrían añadir más propiedades. El análisis de código fuente cubre esa segunda dimensión.

---

## 3. Inventario de schema por page type

### 3.1 Resumen ejecutivo por página

| Page type | Formato | Tipos detectados | Errores (RRT) | Advertencias (RRT) | Estado |
|-----------|---------|-----------------|---------------|--------------------|--------|
| Homepage | Microdata | `schema:Product` (×8) | 0 | 0 | ⚠️ Válido, incompleto |
| Categoría | Microdata | `schema:Product` (×24) | 0 | 0 | ⚠️ Válido, incompleto |
| Producto | Microdata | `schema:Product` (×1) | 0 | 0 | ⚠️ Válido, incompleto |

### 3.2 Propiedades presentes vs. ausentes por page type

#### Homepage

| Propiedad | Estado | Notas |
|-----------|--------|-------|
| `schema:Product` | ✅ Presente | Tipo genérico, no `Book` |
| `name` | ✅ Presente | |
| `url` | ✅ Presente | Via `itemprop="url"` en el enlace |
| `image` | ✅ Presente | `<meta>` con URL **HTTP** (no HTTPS) |
| `description` | ⚠️ Vacío | El `<p itemprop="description">` está presente pero sin contenido en los productos del grid de novedades |
| `offers > price` | ✅ Presente | Formato `"90,00 €"` — incorrecto (debería ser `"90.00"`) |
| `offers > priceCurrency` | ✅ Presente | |
| `offers > availability` | ❌ Ausente | |
| `offers > itemCondition` | ❌ Ausente | Crítico para segunda mano |
| Autor (visible en HTML) | ❌ No en schema | Visible como `<p style="font-size:15px;">ZUSH (Evru...)</p>` pero sin `itemprop` |
| `schema:Organization` | ❌ Ausente | No implementado en ninguna página |
| `schema:WebSite` con `SearchAction` | ❌ Ausente | |
| `schema:BreadcrumbList` | ❌ Ausente | Breadcrumb visual presente en HTML pero sin markup |

#### Categoría (Poesia)

| Propiedad | Estado | Notas |
|-----------|--------|-------|
| `schema:Product` | ✅ Presente | ×24 items (12 lista + 12 grid mobile = duplicados) |
| `name` | ✅ Presente | |
| `url` | ✅ Presente | |
| `image` | ✅ Presente | URL **HTTP** (no HTTPS) |
| `description` | ✅/⚠️ Variable | Presente en la vista lista desktop; vacío en la vista grid mobile |
| `offers > price` | ✅ Presente | Formato `"15,00 €"` — incorrecto |
| `offers > priceCurrency` | ✅ Presente | |
| `offers > availability` | ❌ Ausente | |
| `offers > itemCondition` | ❌ Ausente | |
| Autor (`<span class="autor">`) | ❌ No en schema | Visible en HTML pero sin `itemprop` |
| `schema:BreadcrumbList` | ❌ Ausente | |
| Entidades `schema:Product` duplicadas | ⚠️ Issue | Cada producto aparece dos veces en el HTML (lista + grid) generando 24 entidades en lugar de 12 |

#### Producto (El Petit Príncep)

| Propiedad | Estado | Notas |
|-----------|--------|-------|
| `schema:Product` | ✅ Presente | Tipo genérico, no `schema:Book` |
| `name` | ✅ Presente | |
| `image` | ✅ Presente | `<meta>` con URL **HTTP** (no HTTPS) |
| `description` | ✅ Presente | Descripción bibliográfica completa |
| `offers > price` | ✅ Presente | `"50,00 €"` — formato incorrecto |
| `offers > priceCurrency` | ✅ Presente | |
| `offers > availability` | ✅ Presente | `http://schema.org/InStock` — única página que lo implementa (y el valor usa HTTP, no HTTPS) |
| `offers > itemCondition` | ❌ Ausente | Crítico — es un libro de segunda mano |
| Autor (`SAINT-EXUPÉRY`) | ❌ No en schema | Presente en "Ficha técnica" del HTML, sin `itemprop` |
| `sku` / `productID` | ❌ Ausente | Referencia `124008` visible en tabla, sin markup |
| `schema:Book` | ❌ Ausente | Usa `schema:Product` genérico |
| `schema:AggregateRating` | ❌ Ausente | Módulo `productcomments` activo, pero sin schema |
| `schema:BreadcrumbList` | ❌ Ausente | |

---

## 4. Hallazgos detallados

### H-1 — Precio en formato inválido (afecta a todas las páginas)

**Severidad:** Alta  
**Afecta:** Homepage, Categoría, Producto

El valor de `itemprop="price"` en todas las páginas contiene el precio con formato europeo y símbolo de moneda incluido:

```html
<!-- Actual — INCORRECTO -->
<span itemprop="price" class="price product-price">50,00 €</span>
```

La especificación de Google para `schema:Offer` exige que el valor de `price` sea un número decimal usando punto (`.`) como separador decimal, sin símbolo de moneda. La moneda se indica por separado en `priceCurrency`. El formato correcto es:

```html
<!-- Correcto -->
<span itemprop="price" content="50.00">50,00 €</span>
<meta itemprop="priceCurrency" content="EUR" />
```

Nótese el uso del atributo `content` para proporcionar el valor numérico limpio, mientras el texto visible mantiene el formato local con coma y símbolo de euro. Aunque Google actualmente no penaliza este issue en el Rich Results Test, es un error de implementación documentado en la documentación oficial.

### H-2 — URLs de imágenes en HTTP en lugar de HTTPS (afecta a todas las páginas)

**Severidad:** Media  
**Afecta:** Homepage, Categoría, Producto

El atributo `itemprop="image"` en todos los `<meta>` de imagen apunta a URLs con protocolo HTTP:

```html
<meta itemprop="image" content="http://www.llibresdelmirall.com/covers/129619_1.jpg" />
```

El dominio sirve el sitio en HTTPS, por lo que las imágenes deberían referenciarse con `https://`. Google puede ignorar o desconfiar de imágenes referenciadas con HTTP en páginas HTTPS. La corrección es reemplazar el protocolo en las plantillas Smarty que generan estas URLs.

### H-3 — Entidades `Product` duplicadas en páginas de categoría

**Severidad:** Media  
**Afecta:** Categoría

El HTML de la página de categoría renderiza dos listas de productos: una lista para desktop/tablet (`hidden-xs`) y un grid para mobile (`hidden-sm hidden-md hidden-lg`). Cada lista contiene las mismas 12 referencias de productos, pero ambas están marcadas con `itemscope itemtype="http://schema.org/Product"`. El resultado es que Google encuentra 24 entidades `Product` distintas en la misma página cuando en realidad solo hay 12 productos únicos.

Esto no genera errores en el Rich Results Test, pero es ruido semántico que reduce la calidad del markup. La solución es eliminar el `itemscope`/`itemprop` del bloque duplicado (el grid mobile) y mantenerlo solo en la lista principal.

### H-4 — Disponibilidad del producto solo en la página de producto, y con protocolo HTTP

**Severidad:** Media  
**Afecta:** Homepage, Categoría

Solo la página de producto implementa `offers > availability`. Las páginas de categoría y homepage muestran productos con botón "Añadir al carrito" (claramente en stock), pero el schema no lo indica. Además, la página de producto usa:

```html
<link itemprop="availability" href="http://schema.org/InStock"/>
```

El valor debería referenciar `https://schema.org/InStock`, aunque en la práctica ambas URIs son equivalentes para Google.

### H-5 — Autores presentes en el HTML pero ausentes del schema (todas las páginas)

**Severidad:** Alta para la página de producto; Media para categoría

En la página de producto, el autor `SAINT-EXUPÉRY, Antoine` aparece en la tabla "Ficha técnica" como texto plano sin ningún `itemprop`. En las páginas de categoría y homepage, el autor aparece en `<span class="autor">` o `<p style="font-size:15px;">`, igualmente sin markup semántico.

Esto es una oportunidad perdida especialmente relevante para una librería: el autor es uno de los datos más valiosos para los buscadores, y en `schema:Book` existe la propiedad `author` (que acepta `schema:Person`) para marcarlo explícitamente.

### H-6 — Ausencia total de schema en la homepage más allá de los productos

**Severidad:** Alta

La homepage no implementa ninguno de los tipos de schema relevantes para una página principal de ecommerce: `schema:Organization`, `schema:WebSite` ni `schema:BreadcrumbList`. El footer contiene toda la información de contacto de la tienda (dirección, teléfono, email) visible en HTML, pero sin markup semántico.

---

## 5. Oportunidades de rich results no activadas

Esta sección identifica los rich results que Google podría mostrar para el sitio si se implementara el schema adecuado, ordenados por impacto estimado.

### 5.1 Product rich result con condición de segunda mano (ALTA PRIORIDAD)

**Páginas afectadas:** Producto (y potencialmente categoría)  
**Requisito:** `schema:Product` con `schema:Offer` que incluya `itemCondition: UsedCondition`

Google puede mostrar en las SERPs una etiqueta visual indicando "Segunda mano" o "Usado" junto al precio cuando `itemCondition` está marcado como `https://schema.org/UsedCondition`. Esto es directamente relevante para una librería anticuaria y diferencia los resultados de este sitio en las SERPs respecto a librerías que venden libros nuevos.

### 5.2 Sitelinks searchbox (homepage)

**Páginas afectadas:** Homepage  
**Requisito:** `schema:WebSite` con `potentialAction` de tipo `SearchAction`

Google puede mostrar un cuadro de búsqueda directamente en el resultado de la homepage en las SERPs (cuando el usuario busca el nombre de la marca). El sitio tiene una barra de búsqueda funcional (`/es/buscar`) pero no la señaliza con schema.

### 5.3 BreadcrumbList (categoría y producto)

**Páginas afectadas:** Categoría, Producto  
**Requisito:** `schema:BreadcrumbList` con sus `ListItem`

El breadcrumb visual ya está en el HTML de ambas páginas (`Literatura > Española > Poesía`). Añadir el markup semántico haría que Google lo mostrara en la URL del resultado en las SERPs en lugar de la URL completa, mejorando el CTR.

### 5.4 Product review snippet (producto)

**Páginas afectadas:** Producto  
**Requisito:** `schema:AggregateRating` dentro del `schema:Product`

El módulo `productcomments` está activo en la tienda. Si los productos tienen valoraciones, implementar `AggregateRating` con `ratingValue` y `reviewCount` activaría las estrellas en las SERPs, uno de los rich results con mayor impacto en CTR.

### 5.5 Organization knowledge panel

**Páginas afectadas:** Homepage  
**Requisito:** `schema:Organization` (o `schema:LocalBusiness`) con nombre, dirección, contacto y redes sociales

Implementar `Organization` con la dirección física, teléfono, email y URLs de redes sociales del footer puede contribuir a que Google muestre el panel de conocimiento de la tienda cuando los usuarios buscan directamente la marca.

---

## 6. Recomendaciones priorizadas

### 🔴 Prioridad 1 — Impacto directo en rich results

#### R1 — Añadir `itemCondition: UsedCondition` a todas las páginas de producto

**Afecta:** Producto, Categoría, Homepage (productos del grid)  
**Esfuerzo:** Bajo — valor fijo hardcodeado en la plantilla Smarty del Offer (todos los libros son de segunda mano)  
**Rich result desbloqueado:** Etiqueta "Usado" / "Segunda mano" en SERPs

```html
<!-- Añadir dentro del bloque itemprop="offers" -->
<link itemprop="itemCondition" href="https://schema.org/UsedCondition" />
```

#### R2 — Corregir formato del precio en `itemprop="price"`

**Afecta:** Todas las páginas  
**Esfuerzo:** Bajo — cambio en plantilla Smarty

```html
<!-- Corrección: añadir atributo content con valor numérico limpio -->
<span itemprop="price" content="{$product.price|string_format:"%.2f"}">
    {$product.price} €
</span>
```

#### R3 — Implementar `schema:Organization` en la homepage

**Afecta:** Homepage  
**Esfuerzo:** Bajo — añadir bloque JSON-LD en el `<head>` de la homepage. Todos los datos necesarios (dirección, teléfono, email, redes sociales) están ya en el footer del HTML.  
**Rich result potencial:** Knowledge panel, datos de empresa en SERPs

Ver propuesta completa en la sección 7.

#### R4 — Implementar `schema:WebSite` con `SearchAction` en la homepage

**Afecta:** Homepage  
**Esfuerzo:** Bajo — añadir bloque JSON-LD en el `<head>`  
**Rich result desbloqueado:** Sitelinks searchbox

Ver propuesta completa en la sección 7.

---

### 🟠 Prioridad 2 — Mejora de calidad del markup existente

#### R5 — Migrar de Microdata a JSON-LD para los tipos de schema nuevos

**Afecta:** Nuevas implementaciones (no requiere reescribir el Microdata existente)  
**Esfuerzo:** Bajo — añadir bloques `<script type="application/ld+json">` sin tocar el HTML del tema

Google acepta que una misma página mezcle Microdata (heredado) y JSON-LD (nuevo). La recomendación práctica es no reescribir el Microdata existente del tema (que funciona y no tiene errores), sino añadir los nuevos tipos (Organization, WebSite, BreadcrumbList, Book) directamente como JSON-LD.

#### R6 — Corregir URLs de imagen a HTTPS

**Afecta:** Todas las páginas  
**Esfuerzo:** Bajo — cambio de `http://` a `https://` en los `<meta itemprop="image">` de las plantillas Smarty

#### R7 — Añadir `offers > availability` en páginas de categoría y homepage

**Afecta:** Categoría, Homepage  
**Esfuerzo:** Bajo — añadir una línea en la plantilla del Offer

```html
<link itemprop="availability" href="https://schema.org/InStock" />
```

#### R8 — Implementar `schema:BreadcrumbList` en categoría y producto

**Afecta:** Categoría, Producto  
**Esfuerzo:** Medio — requiere extraer la ruta del breadcrumb visual a JSON-LD. La estructura de categorías ya está en el HTML; es cuestión de recorrerla en el hook.  
**Rich result desbloqueado:** Breadcrumbs visibles en la URL de los resultados de búsqueda

---

### 🟡 Prioridad 3 — Oportunidades de enriquecimiento semántico

#### R9 — Migrar `schema:Product` a `schema:Book` con los campos disponibles

**Afecta:** Producto  
**Esfuerzo:** Medio — cambio de tipo en la plantilla `product.tpl` e inyección de JSON-LD via hook

`schema:Book` es un subtipo de `schema:Product`. La migración es implementable con los datos que ya existen como campos estructurados en la base de datos: título (campo `name`), autor (campo `author`, separado), URL, imagen, descripción y precio. La propuesta JSON-LD de la sección 7 refleja exactamente este subconjunto implementable. Las propiedades que requieren extraer datos del campo de descripción libre (editorial, número de páginas, formato de encuadernación) quedan documentadas en la sección de no implementar.

#### R10 — Marcar el autor con `schema:author`

**Afecta:** Producto, Categoría  
**Esfuerzo:** Bajo — el campo autor existe como campo independiente en PrestaShop; se puede mapear directamente a `itemprop="author"` en el `<span class="autor">` existente, o incluirlo en el JSON-LD de Book (R9)

#### R11 — Eliminar entidades Product duplicadas en páginas de categoría

**Afecta:** Categoría  
**Esfuerzo:** Bajo — eliminar `itemscope`/`itemprop` del bloque del grid mobile, que es el duplicado. El bloque de lista desktop es el que tiene la descripción completa y debe conservarse.

#### R12 — Implementar `schema:AggregateRating` si hay valoraciones activas

**Afecta:** Producto  
**Esfuerzo:** Medio — requiere verificar si algún producto tiene valoraciones en el módulo `productcomments` y, si las hay, leer `ratingValue` y `reviewCount` desde la base de datos para incluirlos en el JSON-LD  
**Rich result desbloqueado:** Estrellas de valoración en las SERPs

---

### ⛔ Descartado — Propiedades no implementables sin rediseño del proceso de entrada de datos

El proceso actual de creación de fichas de producto utiliza un formulario en Microsoft Office 2003 cuya salida se importa como CSV a PrestaShop. Los campos exportados son: ID, autor, título, descripción (texto libre), campos de gestión de stock y etiquetas temáticas. La descripción es un campo de texto libre único que concentra, sin separación estructurada, datos como la editorial, la ciudad de publicación, el año, el número de páginas, el tipo de encuadernación y el estado del ejemplar.

Esto implica que cualquier propiedad de schema que requiera extraer uno de esos valores de forma automática no es implementable sin modificar el sistema de fichas y, con ello, el proceso de alta de productos, el formato del CSV y probablemente el diseño de las páginas de producto en la web. El coste de ese cambio es desproporcionado respecto al beneficio SEO incremental que aportarían estas propiedades de forma aislada, especialmente cuando las mejoras de prioridad 1 y 2 ya cubren los rich results con mayor impacto visible en las SERPs.

Estas propiedades quedan documentadas como deuda técnica, a revisar si en el futuro se moderniza el sistema de gestión de fichas.

#### R13 — `schema:publisher` en páginas de producto

La editorial está embebida en el campo de descripción libre (ej. `"Barcelona, Emecé Editores, 1999..."`). No existe como campo separado en la base de datos. Extraerla de forma fiable requeriría un parser de texto o separar la editorial como campo propio en el sistema de fichas.

#### R14 — `schema:numberOfPages` en páginas de producto

El número de páginas aparece en la descripción libre en formato variable (ej. `"91 p."`, `"267 p."`, `"s/p."`). No existe como campo numérico independiente. Su extracción automática no es fiable dado el formato no normalizado.

#### R15 — `schema:bookFormat` en páginas de producto

El tipo de encuadernación (rústica, cartoné, tela editorial...) aparece únicamente en la descripción libre. No hay ningún campo separado que lo contemple en el sistema actual.

---

## 7. Propuestas de implementación JSON-LD

Los bloques siguientes recogen únicamente las propuestas implementables con los datos disponibles en el sistema actual. Deben añadirse como `<script type="application/ld+json">` en el `<head>` de la página correspondiente, preferiblemente via el hook `hookDisplayHeader()` de un módulo PrestaShop (ver sección 8).

### 7.1 Homepage — Organization

```json
{
  "@context": "https://schema.org",
  "@type": "BookStore",
  "name": "Llibres del Mirall",
  "description": "Librería anticuaria especializada en primeras ediciones de arte y literatura modernos. Fundada en 1995 en Barcelona.",
  "url": "https://www.llibresdelmirall.com/es/",
  "logo": "https://www.llibresdelmirall.com/img/llibres-del-mirall-1418842022.jpg",
  "image": "https://www.llibresdelmirall.com/img/llibres-del-mirall-1418842022.jpg",
  "telephone": "+34934765411",
  "email": "contacte@llibresdelmirall.com",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "C/ Bailèn, 168, local 2",
    "addressLocality": "Barcelona",
    "postalCode": "08037",
    "addressCountry": "ES"
  },
  "sameAs": [
    "https://www.facebook.com/pages/Llibres-del-Mirall/823385327732488",
    "https://twitter.com/LlibresMirall",
    "http://www.pinterest.com/delmirall/"
  ]
}
```

### 7.2 Homepage — WebSite con SearchAction

```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "Llibres del Mirall",
  "url": "https://www.llibresdelmirall.com/es/",
  "potentialAction": {
    "@type": "SearchAction",
    "target": {
      "@type": "EntryPoint",
      "urlTemplate": "https://www.llibresdelmirall.com/es/buscar?search_query={search_term_string}"
    },
    "query-input": "required name=search_term_string"
  }
}
```

> ⚠️ Verificar el formato exacto de la URL de búsqueda antes de implementar. El parámetro puede variar según la configuración del módulo de búsqueda.

### 7.3 Producto — Book con campos disponibles

Este bloque implementa `schema:Book` con el subconjunto de propiedades que existen como campos estructurados en PrestaShop: título, autor, imagen, descripción, URL y datos del Offer. Las propiedades que requerirían extraer datos del campo de descripción libre (editorial, páginas, formato) han sido excluidas deliberadamente y se documentan en R13–R15.

```json
{
  "@context": "https://schema.org",
  "@type": "Book",
  "name": "EL PETIT PRÍNCEP - Barcelona 1999 - Il·lustrat - 1a edició de la traducció",
  "image": "https://www.llibresdelmirall.com/covers/124008_1.jpg",
  "description": "Barcelona, Emecé Editores, 1999. Amb il·lustracions a color de l'autor. 91 p. 4t menor. Tela editorial amb sobrecoberta il·lustrada. Desgast a la sobrecoberta. Interior en perfecte estat. Molt bon exemplar.",
  "author": {
    "@type": "Person",
    "name": "Antoine de Saint-Exupéry"
  },
  "url": "https://www.llibresdelmirall.com/es/juvenil/124008-el-petit-princep-barcelona-1999-illustrat-1a-edicio-de-la-traduccio.html",
  "offers": {
    "@type": "Offer",
    "price": "50.00",
    "priceCurrency": "EUR",
    "availability": "https://schema.org/InStock",
    "itemCondition": "https://schema.org/UsedCondition",
    "seller": {
      "@type": "Organization",
      "name": "Llibres del Mirall"
    }
  }
}
```

### 7.4 Categoría / Producto — BreadcrumbList

Ejemplo para la página de categoría Poesía (Literatura > Española > Poesía):

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Inicio",
      "item": "https://www.llibresdelmirall.com/es/"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Literatura",
      "item": "https://www.llibresdelmirall.com/es/4-literatura"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "Española",
      "item": "https://www.llibresdelmirall.com/es/38-espanola"
    },
    {
      "@type": "ListItem",
      "position": 4,
      "name": "Poesía",
      "item": "https://www.llibresdelmirall.com/es/229-poesia"
    }
  ]
}
```

---

## 8. Consideraciones específicas de PrestaShop

### 8.1 Dónde está el Microdata actual

El markup de `schema:Product` actual está embebido en los archivos `.tpl` del tema:

- **Grid de novedades (homepage):** `themes/llibresdelmirall/templates/` — template del módulo que renderiza los productos en la homepage (probablemente en el módulo `llibresdelmirall` custom)
- **Categoría:** `themes/llibresdelmirall/templates/catalog/listing/product-list.tpl`
- **Producto:** `themes/llibresdelmirall/templates/catalog/product.tpl` — wrapper `<div itemscope itemtype="http://schema.org/Product">`

### 8.2 Cómo añadir JSON-LD en PrestaShop 1.6

La forma más limpia de añadir bloques JSON-LD sin modificar las plantillas de contenido es usar el hook `hookDisplayHeader()` de un módulo. Esto permite inyectar el `<script>` en el `<head>` de forma controlada:

```php
// En el módulo o en un módulo nuevo
public function hookDisplayHeader($params)
{
    if ($this->context->controller->php_self === 'index') {
        // Inyectar JSON-LD de Organization y WebSite solo en homepage
        return '<script type="application/ld+json">' . json_encode($this->getOrganizationSchema()) . '</script>';
    }
    if ($this->context->controller->php_self === 'product') {
        // Inyectar JSON-LD de Book en páginas de producto
        $product = $this->context->controller->product;
        return '<script type="application/ld+json">' . json_encode($this->getBookSchema($product)) . '</script>';
    }
}
```

### 8.3 Corrección del precio en Smarty

En las plantillas `.tpl`, el precio se puede formatear correctamente para el atributo `content`:

```smarty
<span itemprop="price" content="{$product.price|string_format:"%.2f"}">
    {displayPrice price=$product.price}
</span>
```

---

## 9. Limitaciones del análisis

- **El Rich Results Test valida, no optimiza.** Un resultado de 0 errores/0 advertencias no significa schema completo. Significa que el markup existente no viola ninguna regla de Google, pero no indica qué oportunidades están desaprovechadas.
- **Auditoría basada en muestra de 3 URLs.** El sitio tiene más de 7.000 páginas. Los hallazgos son representativos del template, no de todos los productos individuales.
- **`schema:AggregateRating` no evaluable sin datos.** Se identificó el módulo `productcomments` como activo, pero no se pudo verificar si algún producto tiene valoraciones reales para implementar el schema de rating.
- **La URL de búsqueda del `SearchAction` requiere verificación.** La URL exacta del buscador puede variar según la configuración del módulo de búsqueda.

---

## 10. Referencias

- [Google — Structured data product documentation](https://developers.google.com/search/docs/appearance/structured-data/product)
- [Google — Sitelinks searchbox](https://developers.google.com/search/docs/appearance/structured-data/sitelinks-searchbox)
- [Google — Breadcrumbs](https://developers.google.com/search/docs/appearance/structured-data/breadcrumb)
- [schema.org/Book](https://schema.org/Book)
- [schema.org/Offer — itemCondition](https://schema.org/itemCondition)
- [schema.org/OfferItemCondition](https://schema.org/OfferItemCondition)
- [Google Rich Results Test](https://search.google.com/test/rich-results)
- [Schema.org Validator](https://validator.schema.org)
- [Google — JSON-LD vs Microdata](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data#structured-data-format)