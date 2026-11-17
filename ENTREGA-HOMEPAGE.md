# Homepage MiniRueda — Horizon 4.3.0

Implementación real de la homepage sobre el tema exportado de la tienda
`minirueda.com` (Horizon 4.3.0, España, EUR, español de España).

- **Tema de trabajo:** `theme/` (506 archivos originales + secciones y assets nuevos)
- **ZIP instalable:** `dist/minirueda-home-horizon-4.3.0.zip`
- **Vista previa navegable:** `preview/index.html` (servida en el puerto 8000 de este entorno)
- **Generador de la preview:** `tools/render_home_preview.py`

> La homepage sustituye el antiguo `ss-home-redirect`, que enviaba la portada
> directamente a la ficha de producto. El producto sigue siendo el
> protagonista, pero ahora la portada explica, resuelve dudas y vende.

---

## 1. Qué se ha construido

### Secciones (en el orden de la plantilla `templates/index.json`)

| # | Sección | Archivo | Función comercial |
|---|---------|---------|-------------------|
| 1 | Hero | `sections/ss-home-hero.liquid` | Qué es, para qué sirve, precio real y CTA a la compra |
| 2 | Franja de confianza | `sections/ss-home-trust.liquid` | Envío, plazos, devoluciones y pago, en una línea |
| 3 | Beneficios | `sections/ss-home-benefits.liquid` | Discreción, rapidez, formato y un solo uso |
| 4 | Cómo funciona | `sections/ss-home-how.liquid` | 3 pasos con imagen + aviso de uso |
| 5 | Resultado y límites | `sections/ss-home-result.liquid` | Comparador blanco/azul y advertencias reales |
| 6 | Contexto | `sections/ss-home-lifestyle.liquid` | Momento de uso (salir, festival, bar) |
| 7 | Comparativa | `sections/ss-compare.liquid` (reutilizada) | Pegatinas frente a tiras reactivas |
| 8 | Producto | `sections/ss-home-product.liquid` | Precio dinámico, packs y contenido del pedido |
| 9 | FAQ | `sections/ss-faq.liquid` (reutilizada) | Objeciones: uso, sustancias, bebidas, envíos, devoluciones |
| 10 | Confianza de tienda | `sections/ss-home-service.liquid` | Envío, devolución, soporte y checkout |
| 11 | CTA fijo móvil | `sections/ss-home-sticky.liquid` | Compra a mano en móvil, se oculta en el pie |
| 12 | CTA final | `sections/ss-home-final.liquid` | Cierre del recorrido |

Todas las secciones tienen `presets`, ajustes en español y bloques editables
desde el editor visual (textos, iconos, imágenes, enlaces, orden de bloques).

### Archivos nuevos

```
assets/ss-home.css                     Estilos de la homepage (scope .ss-home)
assets/ss-home.js                      CTA fijo móvil (IntersectionObserver/scroll)
sections/ss-home-*.liquid              9 secciones nuevas
templates/index.json                   Homepage completa (12 secciones)
snippets/ss-icon.liquid                + icono "sparkles"
tools/render_home_preview.py           Render de la preview sin Shopify
preview/                               Preview estática generada
```

### Archivos modificados

```
layout/theme.liquid          Carga ss-pdp.css/js y las fuentes también en el index,
                             añade ss-home.css/js y la clase de body ss-home-page.
assets/ss-pdp.css            Estilos del carrito y del drawer aplicados también en la
                             homepage (misma identidad en el flujo de compra).
sections/ss-faq.liquid       Ajuste "Ancla de la sección" (por defecto "preguntas").
sections/ss-compare.liquid   Textos por defecto sin marca ajena.
sections/ss-brand-footer.liquid  Marca por defecto del pie de la PDP.
templates/product.ss-pdp.json    Sustituidas 3 menciones a "SippSister" por MiniRueda.
sections/header-group.json   Barra de anuncio con la oferta real.
sections/footer-group.json   Copy del pie (titular y newsletter) en español.
```

---

## 2. Integración con Shopify

- **Precio:** se lee de `product.price | money` (nunca escrito a mano). En la
  vista previa local aparece 19,99 € porque es el precio simulado.
- **Producto:** el ajuste `product` de cada sección está relleno con el handle
  real; si se vacía, se usa el producto de pegatinas de la tienda.
- **Compra:** el CTA principal lleva a la ficha de producto (`ss-pdp`), donde
  están los packs, los descuentos automáticos y el carrito nativo. No se
  duplica el formulario ni el carrito, así que no hay riesgo de precios o
  descuentos inconsistentes.
- **Packs:** se muestran las tres opciones (1, 2 y 3 packs) con la etiqueta
  comercial que ya comunica la tienda; los importes finales se calculan en la
  PDP y en el carrito.
- **Imágenes:** `image_picker` en cada sección, con imágenes del tema como
  reserva. En la sección de producto se usa la imagen del producto
  (`images[1]`, la lámina) y, si no existe, `featured_image`.
- **Políticas:** enlaces a `/policies/shipping-policy` y
  `/policies/refund-policy` (publicadas). El pie nativo de Horizon solo muestra
  las políticas que estén publicadas.
- **Carrito y checkout:** intactos. Solo se ha ampliado el CSS del drawer para
  que la homepage comparta la paleta de la PDP.

---

## 3. Copy y responsabilidad

- Tono en español de España, frases cortas, sin mayúsculas gritadas ni emojis.
- **Sin reseñas inventadas en la homepage.** En lugar de un muro de testimonios
  se ha construido confianza verificable (envíos, devoluciones, soporte) y una
  FAQ completa.
- Se explican los **límites**: “blanco no significa seguro”, bebidas que
  dificultan la lectura, falsos positivos/negativos y el recordatorio de no
  bajar la guardia. No se promete detección universal ni seguridad.
- El comparador usa imágenes del propio tema, con leyenda explícita de que
  representan el cambio de color.
- **Marca:** la PDP usaba “SippSister” en el pie, en el bloque de problema y en
  un aviso de seguridad. Se ha cambiado a MiniRueda (la marca real de la
  tienda, según `shop.name`, el logo y la política de contacto) porque el
  briefing prohíbe usar la identidad de la tienda de referencia. Es un cambio
  de 3 cadenas, reversible y no afecta a la estructura de la PDP.

---

## 4. Responsive, accesibilidad y rendimiento

- Diseño mobile-first probado por cálculo en 320/360/375/390/430/768/1024/1440.
- Un solo `H1`; jerarquía H2/H3 coherente; `aria-label` en comparador y
  controles; foco visible; acordeones con `aria-expanded`; comparador
  navegable con flechas; `prefers-reduced-motion` respetado.
- El CTA fijo móvil se oculta cerca del pie, queda por debajo del cajón del
  carrito (`z-index: 15` frente a `18` del tema) y no atrapa el foco cuando
  está oculto (`tabindex="-1"` + `aria-hidden`).
- Imágenes con `srcset`/`sizes`; hero en `eager` + `fetchpriority="high"`;
  resto `lazy`. CSS y JS se cargan solo en las plantillas que los usan.
- El comparador usa `touch-action: pan-y` en la home para no bloquear el scroll
  vertical en móvil.

---

## 5. Pruebas realizadas

| Comprobación | Resultado |
|---|---|
| `shopify theme check` (CLI 3.86, local) | **0 incidencias nuevas** (158 preexistentes en archivos originales del tema) |
| JSON de plantillas y esquemas | Válidos (526 archivos en el ZIP) |
| Render de las 12 secciones con datos simulados | Correcto: 3 pasos, 2 columnas de comparativa, 4 tarjetas, 3 packs, 4 inclusiones, 8 FAQ, CTA final y barra móvil |
| Enlaces y anclas | `#como-funciona`, `#resultado`, `#comprar`, `#preguntas`, producto y políticas |
| Precio dinámico | Sí, desde `product.price` |
| Vista previa | Servida y navegable (escritorio y móvil) |

**No comprobado** (limitaciones reales del entorno):

- Instalación del ZIP en Shopify y previsualización dentro del editor.
- Añadir al carrito, descuentos automáticos y checkout (requiere sesión de
  tienda y no se han creado pedidos).
- Capturas de pantalla automáticas: el entorno no dispone de un navegador
  headless con librerías NSS y no hay acceso a la API de Shopify.
- Métricas reales de LCP/CLS/INP.

---

## 6. Pendiente / requiere tu intervención

1. **Instalar el ZIP** como tema *no publicado* y revisar en el editor.
2. **Imágenes:** subir las definitivas si quieres sustituir las del tema
   (todas las secciones tienen selector de imagen).
3. **SEO:** definir meta título y meta descripción de la portada en
   Shopify (Preferencias de la tienda → SEO). El tema no puede fijarlos por
   plantilla en el index.
4. **Oferta:** confirmar que el descuento “2.º pack al 50 %” y el envío gratis
   en 2+ packs siguen activos. La home enlaza a la PDP, donde ya se aplican.
5. **Plazos:** la política de envío habla de 1 día laborable de preparación y
   la PDP de 24–72 h. La home mantiene 24–72 h; unifica el dato si procede.
6. **Reseñas de la PDP:** las valoraciones y testimonios existentes no se han
   tocado ni se han replicado en la home. Conviene validar su origen antes de
   mantenerlos publicados.
7. **Páginas legales:** aviso legal, cookies y condiciones deben existir y estar
   publicadas para que el pie las enlace automáticamente.

---

## 7. Instalación

1. Descarga `dist/minirueda-home-horizon-4.3.0.zip`.
2. Shopify Admin → **Tienda online → Temas → Añadir tema → Subir archivo ZIP**.
3. Abre la vista previa del tema y revisa la portada en escritorio y móvil.
4. Publica cuando quieras; el ZIP no publica nada por sí solo.

Para regenerar la vista previa local:

```bash
python3 tools/render_home_preview.py
python3 -m http.server 8000 --directory preview --bind 0.0.0.0
```
