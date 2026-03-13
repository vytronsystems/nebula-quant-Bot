# NEBULA-QUANT Web

Next.js + React + Tailwind + shadcn-style UI. Futuristic institutional quant cockpit (Operator and Executive modes).

## Setup

- Node 18+. `npm install` then `npm run dev`.
- Theme: dual theme (dark default); palette: nebula-cyan, nebula-violet, nebula-green, nebula-amber, nebula-red (see globals.css and tailwind.config).
- Language: LanguageProvider in operator/executive layouts; switch foundation only.

## Structure

- `src/app`: layout, page, operator/layout+page, executive/layout+page.
- `src/components`: theme-provider, ui/card (shared component library start).
- `src/contexts`: language-context.
- Recharts available for executive KPI widgets; TradingView Lightweight Charts to be added for market views.
