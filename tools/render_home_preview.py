#!/usr/bin/env python3
"""
Renderiza una vista previa estática de la homepage del tema (Liquid) para poder
revisarla en el navegador sin una tienda Shopify conectada.

- Lee theme/templates/index.json y renderiza cada sección con python-liquid.
- Usa datos simulados de la tienda y del producto (precio 19,99 €).
- La cabecera y el pie son una simulación del tema Horizon (solo para la preview).
- Copia los assets del tema a preview/assets.

Uso: python3 tools/render_home_preview.py
"""
from __future__ import annotations

import json
import os
import re
import shutil
from pathlib import Path

import liquid
from liquid import Environment, FileSystemLoader
from markupsafe import Markup

ROOT = Path(__file__).resolve().parent.parent
THEME = Path(os.environ.get("SS_THEME_DIR") or (ROOT / "theme"))
PREVIEW = ROOT / "preview"
PRODUCT_HANDLE = (
    "drink-spike-test-nail-stickers-discreet-drink-test-strips-for-night-out-party-"
    "safety-heart-shape-nail-art-detection-stickers-10"
)

SECTION_SCHEMA_RE = re.compile(r"{%-?\s*schema\s*-?%}(.*?){%-?\s*endschema\s*-?%}", re.S)


def money(value) -> str:
    try:
        amount = float(value) / 100
    except (TypeError, ValueError):
        return ""
    formatted = f"{amount:,.2f}".replace(",", "\u00a0").replace(".", ",")
    return f"{formatted}\u00a0€"


def asset_url(name: str) -> str:
    return f"assets/{name}"


def stylesheet_tag(name: str) -> Markup:
    return Markup(f'<link rel="stylesheet" href="assets/{name}">')


def script_tag(name: str) -> Markup:
    return Markup(f'<script src="assets/{name}" defer></script>')


class Loader(FileSystemLoader):
    def get_source(self, env, name, **kwargs):
        for candidate in (THEME / "snippets" / f"{name}.liquid", THEME / "snippets" / name):
            if candidate.exists():
                return candidate.read_text(encoding="utf-8"), str(candidate), lambda: True, {}
        raise liquid.exceptions.FileSystemError(f"snippet not found: {name}")


def build_env() -> Environment:
    env = Environment(tolerance=liquid.Mode.STRICT)
    env.loader = Loader([str(THEME / "snippets")])
    env.filters["money"] = money
    env.filters["asset_url"] = asset_url
    env.filters["asset_img_url"] = lambda name, size=None: asset_url(name)
    env.filters["image_url"] = lambda image, **kwargs: ""
    env.filters["stylesheet_tag"] = stylesheet_tag
    env.filters["script_tag"] = script_tag
    env.filters["t"] = lambda key: key
    env.filters["within"] = lambda value, collection: value in (collection or [])
    env.filters["standard_event_data"] = lambda value: value
    return env


def mock_product() -> dict:
    return {
        "title": "Pegatinas Detectoras para Bebidas",
        "handle": PRODUCT_HANDLE,
        "url": f"/products/{PRODUCT_HANDLE}",
        "price": 1999,
        "compare_at_price": "",
        "available": True,
        "variants": [{"id": 48000000000000, "price": 1999, "available": True, "title": "Default Title"}],
        "selected_or_first_available_variant": {"id": 48000000000000, "price": 1999, "available": True},
        "featured_image": "",
        "images": [],
        "description": "",
        "type": "Pegatinas",
        "vendor": "MiniRueda",
    }


def shop_globals(product: dict) -> dict:
    return {
        "shop": {
            "name": "MiniRueda",
            "email": "tienda@minirueda.com",
            "currency": "EUR",
            "money_format": "{{amount_with_comma_separator}} €",
            "url": "/",
            "domain": "minirueda.com",
            "permanent_domain": "minirueda.com",
            "enabled_payment_types": [],
            "refund_policy": {"url": "/policies/refund-policy", "title": "Política de reembolso"},
            "shipping_policy": {"url": "/policies/shipping-policy", "title": "Política de envío"},
            "privacy_policy": {"url": "/policies/privacy-policy", "title": "Política de privacidad"},
            "terms_of_service": {"url": "/policies/terms-of-service", "title": "Términos del servicio"},
            "legal_notice": {"url": "/policies/legal-notice", "title": "Aviso legal"},
        },
        "settings": {
            "color_palette": {
                "background": "#ffffff",
                "foreground": "#000000",
                "color1": "#333333",
                "color2": "#dfdfdf",
            },
            "logo": "",
            "logo_height": 36,
        },
        "routes": {
            "root_url": "/",
            "cart_url": "/cart",
            "cart_add_url": "/cart/add",
            "search_url": "/search",
            "account_url": "/account",
            "collections_url": "/collections",
            "all_products_collection_url": "/collections/all",
        },
        "request": {"design_mode": False, "locale": {"iso_code": "es"}, "path": "/"},
        "template": {"name": "index", "suffix": None},
        "product": product,
        "all_products": {PRODUCT_HANDLE: product},
        "canonical_url": "/",
        "page_title": "MiniRueda · Pegatinas detectoras para bebidas",
        "page_description": "",
        "content_for_header": "",
        "content_for_layout": "",
        "linklists": {"main-menu": {"title": "Menú principal", "links": []}},
        "collections": {},
        "cart": {"item_count": 0, "total_price": 0, "items": [], "empty?": True},
        "customer": None,
        "localization": {"country": {"iso_code": "ES"}, "language": {"iso_code": "es"}},
    }


EMPTY_TYPES = {"url", "text", "textarea", "richtext", "html", "image_picker", "product", "collection"}


def schema_defaults(schema: dict, values: dict) -> dict:
    """Aplica los valores por defecto del schema (como hace Shopify)."""
    merged = {}
    for setting in schema.get("settings", []) or []:
        if "id" not in setting:
            continue
        if "default" in setting:
            merged[setting["id"]] = setting["default"]
        elif setting.get("type") in EMPTY_TYPES:
            # Shopify trata como vacío un ajuste sin definir; python-liquid no.
            merged[setting["id"]] = ""
    merged.update(values or {})
    return merged


def block_defaults(schema: dict, block_type: str, values: dict) -> dict:
    for definition in schema.get("blocks", []) or []:
        if definition.get("type") == block_type:
            return schema_defaults(definition, values)
    return dict(values or {})


def section_context(section_id: str, raw: dict, product: dict, globals_: dict, schema: dict) -> dict:
    settings = schema_defaults(schema, raw.get("settings", {}) or {})
    if isinstance(settings.get("product"), str):
        settings = dict(settings)
        settings["product"] = product if settings["product"] == PRODUCT_HANDLE else None

    blocks = []
    order = raw.get("block_order") or list((raw.get("blocks") or {}).keys())
    for block_id in order:
        block_raw = (raw.get("blocks") or {}).get(block_id)
        if not block_raw:
            continue
        blocks.append(
            {
                "id": block_id,
                "type": block_raw.get("type"),
                "settings": block_defaults(schema, block_raw.get("type"), block_raw.get("settings", {}) or {}),
                "shopify_attributes": "",
            }
        )

    section = {
        "id": section_id,
        "type": raw.get("type"),
        "settings": settings,
        "blocks": blocks,
        "block_order": order,
    }
    ctx = dict(globals_)
    ctx["section"] = section
    return ctx


def render_sections() -> str:
    env = build_env()
    product = mock_product()
    g = shop_globals(product)
    template = json.loads((THEME / "templates" / "index.json").read_text(encoding="utf-8"))
    order = template["order"]
    parts: list[str] = []
    for section_id in order:
        raw = template["sections"][section_id]
        section_type = raw["type"]
        path = THEME / "sections" / f"{section_type}.liquid"
        if not path.exists():
            raise SystemExit(f"Sección no encontrada: {path}")
        file_source = path.read_text(encoding="utf-8")
        match = SECTION_SCHEMA_RE.search(file_source)
        schema = json.loads(match.group(1)) if match else {}
        source = SECTION_SCHEMA_RE.sub("", file_source)
        tpl = env.from_string(source)
        ctx = section_context(section_id, raw, product, g, schema)
        rendered = tpl.render(**ctx)
        if section_id != "sticky":
            rendered = f'<div id="shopify-section-{section_id}" class="shopify-section">' + rendered + "</div>"
        parts.append(rendered)
    return "\n".join(parts)


HEADER = """
<header class="pv-header">
  <div class="pv-announce">
    <span>Envío a todo el mundo</span>
    <span aria-hidden="true">·</span>
    <span>Gratis en 2+ packs</span>
  </div>
  <div class="pv-header__bar">
    <nav class="pv-nav pv-nav--left" aria-label="Menú principal">
      <a href="/">Inicio</a>
      <a href="#como-funciona">Cómo funciona</a>
      <a href="#comprar">Comprar</a>
      <a href="#preguntas">Preguntas</a>
    </nav>
    <a class="pv-logo" href="/" aria-label="MiniRueda, inicio">
      <span class="pv-logo__mark" aria-hidden="true">
        <svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M16 3c3.4 3.2 7 4.6 10 4.9v6.6c0 6.3-4.3 11.3-10 14.5C10.3 25.8 6 20.8 6 14.5V7.9c3-.3 6.6-1.7 10-4.9z"/><path d="M16 11.6c1.3-1.9 4.4-1.2 4.4 1.3 0 2.1-2.6 3.8-4.4 5.1-1.8-1.3-4.4-3-4.4-5.1 0-2.5 3.1-3.2 4.4-1.3z"/></svg>
      </span>
      <span class="pv-logo__type">MiniRueda</span>
    </a>
    <div class="pv-actions">
      <button type="button" aria-label="Buscar">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="11" cy="11" r="7"/><path d="M16.5 16.5L21 21"/></svg>
      </button>
      <button type="button" aria-label="Cuenta">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="12" cy="8.5" r="3.8"/><path d="M4.5 21c.7-3.9 3.6-6 7.5-6s6.8 2.1 7.5 6"/></svg>
      </button>
      <button type="button" aria-label="Carrito, 0 artículos">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M5 8h14l-1.3 12.2a1.4 1.4 0 0 1-1.4 1.3H7.7a1.4 1.4 0 0 1-1.4-1.3L5 8z"/><path d="M9 8V5.8a3 3 0 0 1 6 0V8"/></svg>
        <span class="pv-cart-count">0</span>
      </button>
    </div>
  </div>
</header>
"""

FOOTER = """
<footer class="pv-footer">
  <div class="pv-wrap pv-footer__news">
    <div>
      <h2>Salir con más tranquilidad</h2>
      <p>Reposiciones, novedades y avisos útiles. Sin spam.</p>
    </div>
    <form class="pv-newsletter" onsubmit="return false">
      <label for="pv-email" class="pv-visually-hidden">Correo electrónico</label>
      <input id="pv-email" type="email" placeholder="tu@correo.com" autocomplete="email">
      <button type="submit">Apuntarme</button>
    </form>
  </div>
  <div class="pv-wrap pv-footer__cols">
    <div>
      <p class="pv-footer__brand">MiniRueda</p>
      <p class="pv-footer__tag">Pegatinas detectoras para bebidas · Envíos a toda España</p>
      <p class="pv-footer__tag"><a href="mailto:tienda@minirueda.com">tienda@minirueda.com</a></p>
    </div>
    <div>
      <p class="pv-footer__title">Tienda</p>
      <ul>
        <li><a href="#comprar">Pegatinas detectoras</a></li>
        <li><a href="#como-funciona">Cómo funciona</a></li>
        <li><a href="#preguntas">Preguntas frecuentes</a></li>
      </ul>
    </div>
    <div>
      <p class="pv-footer__title">Ayuda</p>
      <ul>
        <li><a href="/policies/shipping-policy">Envíos</a></li>
        <li><a href="/policies/refund-policy">Devoluciones</a></li>
        <li><a href="/policies/contact-information">Contacto</a></li>
      </ul>
    </div>
    <div>
      <p class="pv-footer__title">Legal</p>
      <ul>
        <li><a href="/policies/legal-notice">Aviso legal</a></li>
        <li><a href="/policies/privacy-policy">Privacidad</a></li>
        <li><a href="/policies/terms-of-service">Condiciones de compra</a></li>
      </ul>
    </div>
  </div>
  <div class="pv-wrap pv-footer__bottom">
    <span>© 2026 MiniRueda</span>
    <span>Creado con Shopify</span>
  </div>
</footer>
"""

SHELL_CSS = """
:root { --burgundy:#6D303F; --berry:#AF636F; --ink:#2A314B; --ink-soft:#5E6275; --rose:#E7D1D3; }
* { box-sizing: border-box; }
body.pv-body { margin: 0; background:#FFFCFB; color:var(--ink); font-family:'Plus Jakarta Sans', Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; -webkit-font-smoothing: antialiased; }
.pv-visually-hidden { position:absolute!important; width:1px; height:1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; }
.pv-wrap { max-width:1180px; margin:0 auto; padding:0 16px; }
@media (min-width:750px){ .pv-wrap { padding:0 24px; } }
.preview-note { position:fixed; left:12px; bottom:12px; z-index:200; max-width:270px; background:rgba(42,49,75,.94); color:#fff; font-size:11.5px; line-height:1.45; padding:10px 12px; border-radius:10px; box-shadow:0 10px 30px rgba(0,0,0,.25); }
.preview-note b { display:block; font-size:12px; margin-bottom:2px; }
@media (max-width:749px){ .preview-note { display:none; } }

.pv-header { position:sticky; top:0; z-index:80; background:rgba(255,255,255,.96); backdrop-filter:blur(8px); border-bottom:1px solid rgba(109,48,63,.1); }
.pv-announce { background:var(--burgundy); color:#fff; display:flex; flex-wrap:wrap; justify-content:center; gap:8px; padding:10px 14px; font-size:10.5px; font-weight:700; letter-spacing:.05em; text-transform:uppercase; }
.pv-announce span[aria-hidden] { opacity:.55; }
.pv-header__bar { display:grid; grid-template-columns:1fr auto 1fr; align-items:center; gap:16px; max-width:1180px; margin:0 auto; padding:12px 16px; }
@media (min-width:750px){ .pv-header__bar { padding:16px 24px; } }
.pv-nav { display:none; gap:18px; font-size:13px; font-weight:600; }
.pv-nav a { color:var(--ink-soft); text-decoration:none; }
.pv-nav a:hover { color:var(--burgundy); }
@media (min-width:990px){ .pv-nav { display:flex; } }
.pv-logo { display:inline-flex; align-items:center; gap:8px; text-decoration:none; color:var(--burgundy); justify-self:center; }
.pv-logo__mark { width:28px; height:28px; display:inline-flex; color:var(--berry); }
.pv-logo__mark svg { width:100%; height:100%; }
.pv-logo__type { font-family:'Instrument Serif', Georgia, serif; font-size:24px; letter-spacing:.01em; color:var(--burgundy); }
.pv-actions { display:flex; gap:6px; justify-self:end; align-items:center; }
.pv-actions button { position:relative; width:38px; height:38px; border-radius:50%; border:0; background:transparent; color:var(--ink); display:grid; place-items:center; cursor:pointer; }
.pv-actions button:hover { background:#FBF1F2; }
.pv-actions svg { width:20px; height:20px; }
.pv-cart-count { position:absolute; top:2px; right:0; background:var(--burgundy); color:#fff; font-size:9px; font-weight:800; border-radius:999px; min-width:15px; height:15px; display:grid; place-items:center; padding:0 3px; }

.pv-footer { background:#fff; border-top:1px solid rgba(109,48,63,.1); margin-top:0; }
.pv-footer__news { display:grid; gap:18px; padding-top:44px; padding-bottom:32px; border-bottom:1px solid rgba(109,48,63,.08); }
@media (min-width:750px){ .pv-footer__news { grid-template-columns:1fr auto; align-items:center; } }
.pv-footer__news h2 { margin:0; font-size:22px; letter-spacing:-.02em; }
.pv-footer__news p { margin:6px 0 0; color:var(--ink-soft); font-size:13.5px; }
.pv-newsletter { display:flex; gap:8px; }
.pv-newsletter input { min-width:0; width:100%; padding:12px 14px; border-radius:10px; border:1px solid var(--rose); font:inherit; font-size:13.5px; background:#fff; }
.pv-newsletter button { background:var(--burgundy); color:#fff; border:0; border-radius:10px; padding:12px 18px; font-weight:800; font-size:13px; cursor:pointer; }
.pv-footer__cols { display:grid; gap:26px; padding-top:32px; padding-bottom:32px; }
@media (min-width:750px){ .pv-footer__cols { grid-template-columns:1.4fr 1fr 1fr 1fr; gap:32px; } }
.pv-footer__brand { font-family:'Instrument Serif', Georgia, serif; font-size:22px; color:var(--burgundy); margin:0; }
.pv-footer__tag { font-size:12.5px; color:var(--ink-soft); margin:8px 0 0; line-height:1.5; }
.pv-footer__tag a { color:var(--burgundy); }
.pv-footer__title { font-size:11px; font-weight:800; letter-spacing:.12em; text-transform:uppercase; color:var(--berry); margin:0 0 10px; }
.pv-footer ul { list-style:none; margin:0; padding:0; display:grid; gap:8px; }
.pv-footer ul a { font-size:13px; color:var(--ink-soft); text-decoration:none; }
.pv-footer ul a:hover { color:var(--burgundy); }
.pv-footer__bottom { display:flex; flex-wrap:wrap; justify-content:space-between; gap:8px; padding-top:18px; padding-bottom:40px; border-top:1px solid rgba(109,48,63,.08); font-size:11.5px; color:var(--ink-soft); }
"""


def build_page(section_html: str) -> str:
    return f"""<!doctype html>
<html lang="es" dir="ltr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>MiniRueda · Pegatinas detectoras para bebidas</title>
  <meta name="description" content="Pegatinas que parecen nail art y comprueban tu bebida: GHB y ketamina, resultado en unos 10 segundos. Envíos a España.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&amp;family=Instrument+Serif:ital@0;1&amp;display=swap">
  <link rel="stylesheet" href="assets/ss-pdp.css">
  <link rel="stylesheet" href="assets/ss-home.css">
  <style>{SHELL_CSS}</style>
</head>
<body class="pv-body ss-home-page">
  {HEADER}
  <main id="MainContent">
    {section_html}
  </main>
  {FOOTER}
  <div class="preview-note"><b>Vista previa del tema</b>Cabecera y pie simulados. El contenido es el HTML generado por las secciones Liquid.</div>
  <script src="assets/ss-pdp.js" type="module"></script>
  <script src="assets/ss-home.js" defer></script>
</body>
</html>
"""


def copy_assets() -> None:
    target = PREVIEW / "assets"
    target.mkdir(parents=True, exist_ok=True)
    for name in ("ss-pdp.css", "ss-home.css", "ss-pdp.js", "ss-home.js"):
        shutil.copy2(THEME / "assets" / name, target / name)
    for image in (THEME / "assets").glob("pdp-ss-*"):
        shutil.copy2(image, target / image.name)


def main() -> None:
    PREVIEW.mkdir(exist_ok=True)
    copy_assets()
    html = build_page(render_sections())
    (PREVIEW / "index.html").write_text(html, encoding="utf-8")
    print(f"OK · preview/index.html ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
