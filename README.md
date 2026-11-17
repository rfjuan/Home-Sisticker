# Home-Sisticker

Trabajo sobre el tema **Horizon 4.3.0** de la tienda **MiniRueda**
(`minirueda.com`): landing de producto premium (`product.ss-pdp`) y nueva
homepage.

```
theme/     Tema Shopify de trabajo (Liquid, JSON templates, assets)
dist/      ZIP instalable del tema
preview/   Vista previa estática de la homepage (HTML generado)
tools/     Generador de la vista previa
theme_export__*.zip   Export original recibido (sin modificar)
```

- **Entrega de la homepage:** [`ENTREGA-HOMEPAGE.md`](ENTREGA-HOMEPAGE.md)
- **Instalación:** Shopify Admin → Tienda online → Temas → Añadir tema → Subir
  el ZIP de `dist/`.
- **Vista previa local:**

```bash
python3 tools/render_home_preview.py
python3 -m http.server 8000 --directory preview --bind 0.0.0.0
```

La preview reproduce el HTML que generan las secciones Liquid con datos
simulados (precio 19,99 €, producto real de la tienda). La cabecera y el pie son
una simulación del tema Horizon para poder revisar la página sin Shopify.
