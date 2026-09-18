# Playbook: Navbar

**When:** any multi-section page or site shell.  
**Refs:** `navbar-gallery` · `drafthouse refs search navbar`

## IA

```
[brand mark]     [primary links]     [auth or primary CTA]
mobile: hamburger → drawer with same links + CTA
```

## Do
- 1 primary CTA in chrome
- Focus-visible styles on links
- Sticky only if the page is long; otherwise static is calmer
- Mobile target ≥ 44px

## Don’t
- Mega-menu without real IA depth
- 8+ top-level links
- Icon soup in the bar

## Token hooks
nav background `--dt-ink` or `--dt-paper-2`, link color, border `--dt-rule`

## Structure checks
`has-nav`
