"""Machine-readable design reference catalog for agent lookup.

Sources are public inspiration galleries — use for pattern study and
direction, never as a license to clone layouts pixel-for-pixel.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

CATALOG_VERSION = "2026.10.02"


@dataclass(slots=True)
class ReferenceSite:
    id: str
    category: str
    name: str
    url: str
    best_for: str
    tags: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# Primary categories requested + adjacent production references.
REFERENCES: list[ReferenceSite] = [
    # Navigation
    ReferenceSite("navbar-gallery", "navbars", "Navbar Gallery", "https://navbar.gallery",
                  "Real product navbars — density, mega-menus, mobile drawers", ["nav", "header", "menu"]),
    # Heroes
    ReferenceSite("supahero", "heroes", "Supahero", "https://supahero.io",
                  "Hero sections — headline hierarchy, media, CTAs", ["hero", "landing", "above-fold"]),
    ReferenceSite("hero-head", "heroes", "Hero Head", "https://hero.head.dev",
                  "Hero composition variants", ["hero"]),
    # Errors
    ReferenceSite("404s-design", "error-pages", "404s.design", "https://404s.design",
                  "404 / empty / error page patterns", ["404", "error", "empty-state"]),
    # Footers
    ReferenceSite("footer-design", "footers", "Footer.design", "https://footer.design",
                  "Footer IA, link tiers, legal rows", ["footer", "sitemap"]),
    # CTAs
    ReferenceSite("cta-gallery", "ctas", "CTA Gallery", "https://cta.gallery",
                  "Call-to-action blocks and button copy patterns", ["cta", "conversion", "buttons"]),
    # Sections
    ReferenceSite("unsection", "sections", "Unsection", "https://unsection.com",
                  "Page sections — features, pricing, social proof blocks", ["sections", "layout"]),
    # Motion
    ReferenceSite("60fps-design", "animation", "60fps.design", "https://60fps.design",
                  "Smooth web animation references (restrained motion)", ["animation", "motion", "scroll"]),
    ReferenceSite("designspells", "microinteractions", "Design Spells", "https://designspells.com",
                  "Microinteractions — hovers, toggles, feedback", ["microinteraction", "ux", "hover"]),
    # Bento
    ReferenceSite("bentogrids", "bento", "Bento Grids", "https://bentogrids.com",
                  "Bento / modular grid compositions", ["bento", "grid", "cards"]),
    # Brand
    ReferenceSite("rebrand-gallery", "rebrands", "Rebrand.gallery", "https://rebrand.gallery",
                  "Rebrand case studies — systems before screenshots", ["brand", "rebrand", "identity"]),
    # Grids
    ReferenceSite("gridddy", "grids", "Gridddy", "https://gridddy.framer.website",
                  "Grid layout systems", ["grid", "layout", "columns"]),
    # One-pagers
    ReferenceSite("onepagelove-og", "one-pagers", "One Page Love OG", "https://onepagelove.com/og",
                  "One-pager structures", ["onepager", "landing"]),
    # SaaS / landing
    ReferenceSite("saaspo", "saas-sites", "Saaspo", "https://saaspo.com",
                  "SaaS marketing sites by pattern", ["saas", "marketing"]),
    ReferenceSite("landing-love", "landing-pages", "Landing.love", "https://landing.love",
                  "Landing page breakdowns", ["landing", "hero", "pricing"]),
    ReferenceSite("saasframe", "saas-frames", "Saasframe", "https://saasframe.io",
                  "SaaS UI frames / marketing modules", ["saas", "ui", "frames"]),
    # Product UI
    ReferenceSite("refero-styles", "product-ui", "Refero Styles", "https://styles.refero.design",
                  "Product UI style extracts from real apps", ["product-ui", "dashboard", "app"]),
    ReferenceSite("refero", "product-ui", "Refero", "https://refero.design",
                  "Product screen library", ["product-ui", "flows"]),
    ReferenceSite("mobbin", "product-ui", "Mobbin", "https://mobbin.com",
                  "Mobile + web product UI flows", ["mobile", "product-ui", "flows"]),
    ReferenceSite("pageflows", "product-ui", "Page Flows", "https://pageflows.com",
                  "User flow recordings / UX patterns", ["ux", "flows", "onboarding"]),
    # Fresh / curated
    ReferenceSite("recent-design", "latest", "Recent.design", "https://recent.design",
                  "Latest shipped designs", ["recent", "trends"]),
    ReferenceSite("curated-design", "curated", "Curated.design", "https://curated.design",
                  "Curated site collections", ["curated", "gallery"]),
    ReferenceSite("webinspoo", "web-inspo", "Webinspoo", "https://webinspoo.com",
                  "Web inspiration feed", ["inspo", "web"]),
    ReferenceSite("godly", "web-inspo", "Godly", "https://godly.website",
                  "High-craft marketing sites", ["inspo", "marketing", "craft"]),
    ReferenceSite("awwwards", "web-inspo", "Awwwards", "https://awwwards.com",
                  "Awarded sites — study craft, not gimmicks", ["awwwards", "craft"]),
    ReferenceSite("lapa-ninja", "landing-pages", "Lapa Ninja", "https://www.lapa.ninja",
                  "Landing page gallery", ["landing", "gallery"]),
    ReferenceSite("land-book", "landing-pages", "Land-book", "https://land-book.com",
                  "Landing page catalog", ["landing"]),
    # Components
    ReferenceSite("vantaui", "ui-components", "Vanta UI", "https://vantaui.com",
                  "UI component gallery", ["components", "ui"]),
    ReferenceSite("simply-buttons", "buttons", "Simply Buttons", "https://simply-buttons.vercel.app",
                  "Button styles and states", ["buttons", "controls"]),
    ReferenceSite("mesh3d", "3d", "Mesh3D Gallery", "https://mesh3d.gallery",
                  "3D website references — use sparingly", ["3d", "webgl"]),
    # Adjacent high-signal
    ReferenceSite("dark-design", "themes", "Dark Design", "https://www.dark.design",
                  "Dark-mode UI references", ["dark", "theme"]),
    ReferenceSite("shiny-design", "themes", "Shiny Design", "https://www.shiny.design",
                  "Polished dark UI + motion", ["dark", "polish"]),
    ReferenceSite("pricing-page", "pricing", "Pricing Page", "https://pricing.page",
                  "Pricing tables and plan comparison", ["pricing", "saas"]),
    ReferenceSite("saas-interface", "saas-ui", "SaaS Interface", "https://www.saasinterface.com",
                  "SaaS interface patterns", ["saas", "ui"]),
    ReferenceSite("screenlane", "product-ui", "Screenlane", "https://screenlane.com",
                  "Mobile UI patterns", ["mobile", "ui"]),
    ReferenceSite("collectui", "ui-components", "Collect UI", "https://collectui.com",
                  "Daily UI challenges by category", ["ui", "components"]),
    ReferenceSite("ui-garage", "product-ui", "UI Garage", "https://uigarage.net",
                  "UI kit / screen samples", ["ui", "kits"]),
    ReferenceSite("httpster", "web-inspo", "Httpster", "https://httpster.net",
                  "Indie web design picks", ["web", "indie"]),
    ReferenceSite("minimal-gallery", "minimal", "Minimal Gallery", "https://minimal.gallery",
                  "Minimal site references", ["minimal", "editorial"]),
    ReferenceSite("whimsy", "illustration", "Whimsy", "https://whimsy.design",
                  "Playful illustration in product — only if brand allows", ["illustration"]),
    ReferenceSite("open-peeps", "illustration", "Open Peeps", "https://www.openpeeps.com",
                  "Hand-drawn people illustration library (CC0-ish check license)", ["illustration", "characters"]),
    ReferenceSite("undraw", "illustration", "unDraw", "https://undraw.co",
                  "Open illustrations — often overused; prefer custom when possible", ["illustration", "open"]),
    ReferenceSite("heroicons", "icons", "Heroicons", "https://heroicons.com",
                  "Icon set — consistent stroke system", ["icons"]),
    ReferenceSite("lucide", "icons", "Lucide", "https://lucide.dev",
                  "Open icon set", ["icons", "open"]),
    ReferenceSite("fonts-google", "type", "Google Fonts", "https://fonts.google.com",
                  "Type pairing research (check licenses for product use)", ["typography", "fonts"]),
    ReferenceSite("fontshare", "type", "Fontshare", "https://www.fontshare.com",
                  "Quality free fonts", ["typography", "fonts"]),
    ReferenceSite("type-scale", "type", "Typescale", "https://typescale.com",
                  "Type scale exploration", ["typography", "scale"]),
    ReferenceSite("realtime-colors", "color", "Realtime Colors", "https://www.realtimecolors.com",
                  "Palette + type on a live layout", ["color", "palette"]),
    ReferenceSite("coolors", "color", "Coolors", "https://coolors.co",
                  "Palette generation", ["color"]),
    ReferenceSite("shapefest", "texture", "Shapefest", "https://www.shapefest.com",
                  "Free 3D shapes for backgrounds — avoid AI-blob cliché overload", ["3d", "assets"]),
    ReferenceSite("lstore", "components", "LStore Components", "https://www.lstore.graphics",
                  "Production UI blocks", ["components"]),
    ReferenceSite("21stdev", "ui-components", "21st.dev", "https://21st.dev",
                  "Community React components", ["react", "components"]),
    ReferenceSite("tweakcn", "themes", "tweakcn", "https://tweakcn.com",
                  "shadcn/ui theme editor patterns", ["shadcn", "theme"]),
    ReferenceSite("shadcn-examples", "design-systems", "ui.shadcn.com examples", "https://ui.shadcn.com/examples",
                  "Component composition examples", ["shadcn", "components", "design-system"]),
    ReferenceSite("vercel-design", "design-systems", "Vercel Geist", "https://vercel.com/geist/introduction",
                  "Geist design system docs", ["design-system", "vercel"]),
    ReferenceSite("linear-method", "product-ui", "Linear", "https://linear.app",
                  "Product marketing + app density reference", ["product-ui", "saas", "craft"]),
    ReferenceSite("stripe-docs-ui", "product-ui", "Stripe", "https://stripe.com",
                  "Docs/marketing hierarchy reference", ["product-ui", "docs", "fintech"]),
    # Workspace design-references registry (added 2026-10-02) —
    # named aesthetic references from ~/workspace/skills/design-references/SKILL.md.
    # Component libraries
    ReferenceSite("balsa-ui", "ui-components", "Balsa UI", "https://balsa-ui.com",
                  "Minimal component set", ["components", "minimal"]),
    ReferenceSite("springs-studio", "ui-components", "Springs Studio", "https://springs.studio",
                  "Component studio", ["components", "studio"]),
    ReferenceSite("animos", "ui-components", "Animos", "https://animos.app",
                  "Animated components", ["components", "animated"]),
    ReferenceSite("tegaki", "ui-components", "Tegaki", "https://gkurt.com/tegaki",
                  "Hand-drawn UI style", ["components", "hand-drawn"]),
    ReferenceSite("meshfont", "ui-components", "Meshfont", "https://meshfont.com",
                  "Mesh-styled type UI", ["components", "type", "mesh"]),
    ReferenceSite("spectrum-ui", "ui-components", "Spectrum UI", "https://ui.spectrumhq.in",
                  "React component set", ["components", "react"]),
    ReferenceSite("shadcnblocks", "ui-components", "shadcnblocks", "https://shadcnblocks.com",
                  "Blocks built on shadcn", ["components", "shadcn", "blocks"]),
    ReferenceSite("react-bits", "ui-components", "React Bits", "https://reactbits.dev",
                  "React component patterns", ["components", "react", "patterns"]),
    ReferenceSite("8bitcn", "ui-components", "8bitcn", "https://8bitcn.com",
                  "Retro 8-bit styled shadcn", ["components", "shadcn", "retro"]),
    ReferenceSite("evil-charts", "ui-components", "Evil Charts", "https://evilcharts.com",
                  "Charts, deliberately unconventional", ["components", "charts"]),
    ReferenceSite("coss-ui", "ui-components", "Coss UI", "https://coss.com/ui",
                  "Component set", ["components"]),
    ReferenceSite("rare-ui", "ui-components", "Rare UI", "https://rareui.com",
                  "Rare or unusual components", ["components", "unusual"]),
    ReferenceSite("beui", "ui-components", "BeUI", "https://beui.dev",
                  "Component set", ["components"]),
    ReferenceSite("easy-ui", "ui-components", "Easy UI", "https://easyui.site",
                  "Component set", ["components"]),
    ReferenceSite("reui", "ui-components", "ReUI", "https://reui.io",
                  "React and Tailwind components", ["components", "react", "tailwind"]),
    ReferenceSite("aceternity-ui", "ui-components", "Aceternity UI", "https://ui.aceternity.com",
                  "Animated, showy components", ["components", "animated"]),
    ReferenceSite("magic-ui", "ui-components", "Magic UI", "https://magicui.design",
                  "Animated components", ["components", "animated"]),
    ReferenceSite("uiverse", "ui-components", "Uiverse", "https://uiverse.io",
                  "Community element library", ["components", "community"]),
    ReferenceSite("uiable", "ui-components", "UIAble", "https://uiable.com",
                  "Component set", ["components"]),
    ReferenceSite("microkit-ui", "ui-components", "MicroKit UI", "https://microkit.co",
                  "Micro components", ["components", "micro"]),
    ReferenceSite("mapcn", "ui-components", "mapcn", "https://mapcn.dev",
                  "Maps, markers, routes, popups", ["components", "maps"]),
    ReferenceSite("liquid-glass", "ui-components", "Liquid Glass", "https://glass.samasante.com",
                  "Glass and refraction components", ["components", "glass"]),
    # Design galleries
    ReferenceSite("kage", "web-inspo", "Kage", "https://kage.design",
                  "UI inspiration mapped to prompts", ["inspo", "prompts"]),
    ReferenceSite("component-gallery", "components", "Component Gallery", "https://component.gallery",
                  "2600+ component examples", ["components", "gallery"]),
    ReferenceSite("appshot-gallery", "product-ui", "AppShot Gallery", "https://appshot.gallery",
                  "Real mobile app screenshots", ["product-ui", "mobile", "screenshots"]),
    ReferenceSite("landdding", "landing-pages", "Landdding", "https://landdding.com",
                  "Real design references", ["landing", "gallery"]),
    ReferenceSite("open-design", "web-inspo", "Open Design", "https://open-design.ai",
                  "Design references", ["inspo", "gallery"]),
    ReferenceSite("designmd", "web-inspo", "DesignMD", "https://designmd.me",
                  "Design references", ["inspo"]),
    ReferenceSite("designmd-supply", "web-inspo", "DESIGNmd Supply", "https://designmd.supply",
                  "Design supply", ["inspo", "assets"]),
    ReferenceSite("designmd-hyperbrowser", "web-inspo", "DesignMD Hyperbrowser",
                  "https://design-md.hyperbrowser.ai",
                  "DesignMD hosted variant", ["inspo"]),
    ReferenceSite("designmd-ai", "design-systems", "DesignMD.ai", "https://designmd.ai",
                  "Design systems in Markdown for agents", ["design-system", "markdown", "agents"]),
    ReferenceSite("typeui", "type", "TypeUI", "https://typeui.sh",
                  "Typography-driven UI", ["typography", "type"]),
    ReferenceSite("vibeprompt", "product-ui", "VibePrompt", "https://vibeprompts.dev",
                  "Prompts for dashboards and landing pages", ["product-ui", "prompts", "dashboard"]),
    ReferenceSite("logotouse", "rebrands", "LogoToUse", "https://logotouse.com",
                  "Logo inspiration", ["logo", "brand"]),
    # Motion
    ReferenceSite("motion-primitives", "animation", "Motion Primitives", "https://motion-primitives.com",
                  "Motion-focused components", ["animation", "components", "motion"]),
    ReferenceSite("motionin", "animation", "MotionIn", "https://motionin.design",
                  "Animation inspiration", ["animation", "motion"]),
    ReferenceSite("scrolltide", "animation", "ScrollTide", "https://scrolltide.co",
                  "200+ build prompts for 3D and scroll-driven sites", ["animation", "scroll", "3d", "prompts"]),
    ReferenceSite("kinetics", "animation", "Kinetics", "https://kinetics.colorion.co",
                  "150+ motion effects with React code and prompts", ["animation", "react", "prompts"]),
    ReferenceSite("anime-js", "animation", "Anime.js", "https://animejs.com",
                  "Animation library, canonical docs", ["animation", "library", "docs"]),
    ReferenceSite("css-text-effects", "animation", "CSS Text Effects", "https://text-effects.colorion.co",
                  "Text effects", ["animation", "text"]),
    ReferenceSite("circle-loaders", "animation", "Circle Loaders", "https://circleloaders.dominikakissi.com",
                  "Loaders", ["animation", "loaders"]),
    ReferenceSite("gradient-buttons", "buttons", "Gradient Buttons", "https://gradientbuttons.colorion.co",
                  "Gradient buttons", ["buttons", "gradient"]),
    # Illustration + icons
    ReferenceSite("kitbitz", "illustration", "Kitbitz", "https://kitbitz.art",
                  "2000+ hand-drawn illustrations", ["illustration", "hand-drawn"]),
    ReferenceSite("3dicons", "icons", "3Dicons", "https://3dicons.co",
                  "3D icon set", ["icons", "3d"]),
    # Agent-oriented design systems
    ReferenceSite("shadcn-ui", "design-systems", "shadcn/ui", "https://ui.shadcn.com",
                  "Component docs — the baseline everyone copies", ["design-system", "shadcn", "docs"]),
    ReferenceSite("aura", "design-systems", "Aura", "https://aura.build",
                  "Agent-facing design system", ["design-system", "agents"]),
    ReferenceSite("neuform", "design-systems", "Neuform", "https://neuform.ai",
                  "Agent-facing design system", ["design-system", "agents"]),
]

CATEGORIES = sorted({r.category for r in REFERENCES})


def catalog_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "references"


_CATALOG_CACHE: list[dict[str, Any]] | None = None


def load_catalog() -> list[dict[str, Any]]:
    """Load catalog.json with in-process cache (refs search is hot-path)."""
    global _CATALOG_CACHE
    if _CATALOG_CACHE is not None:
        return _CATALOG_CACHE
    path = catalog_dir() / "catalog.json"
    items: list[dict[str, Any]] = []
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "references" in data:
                items = list(data["references"])
            elif isinstance(data, list):
                items = data
        except json.JSONDecodeError:
            items = []
    if not items:
        items = [r.to_dict() for r in REFERENCES]
    _CATALOG_CACHE = items
    return items


def write_catalog(path: Path | None = None) -> Path:
    global _CATALOG_CACHE
    out = path or (catalog_dir() / "catalog.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": CATALOG_VERSION,
        "count": len(REFERENCES),
        "categories": CATEGORIES,
        "usage": (
            "Study structure and hierarchy. Do not clone layouts pixel-for-pixel. "
            "Prefer on-brand adaptation via DESIGN.md tokens."
        ),
        "references": [r.to_dict() for r in REFERENCES],
    }
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _CATALOG_CACHE = None
    return out


def search_references(
    query: str = "",
    category: str | None = None,
    tag: str | None = None,
    limit: int = 12,
) -> list[dict[str, Any]]:
    items = load_catalog()
    q = (query or "").strip().lower()
    cat = (category or "").strip().lower() or None
    tg = (tag or "").strip().lower() or None
    out: list[dict[str, Any]] = []
    for item in items:
        if cat and str(item.get("category", "")).lower() != cat:
            continue
        if tg:
            tags = item.get("tags") or []
            if not any(str(t).lower() == tg for t in tags):
                continue
        if q:
            id_s = str(item.get("id", "")).lower()
            name = str(item.get("name", "")).lower()
            cat_s = str(item.get("category", "")).lower()
            best = str(item.get("best_for", "")).lower()
            tags_s = " ".join(str(t).lower() for t in item.get("tags") or [])
            if q not in id_s and q not in name and q not in cat_s and q not in best and q not in tags_s:
                continue
        out.append(item)
        if len(out) >= limit:
            break
    return out


def categories_index() -> dict[str, list[str]]:
    idx: dict[str, list[str]] = {}
    for item in load_catalog():
        idx.setdefault(item["category"], []).append(item["id"])
    return idx
