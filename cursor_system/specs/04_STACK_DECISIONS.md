# Stack Decisions

## Quant core
- Python (existing repo preserved)

## Control plane
- Java 21
- Spring Boot 3
- Drools

## Web
- Next.js
- React
- Tailwind CSS
- shadcn/ui
- TradingView Lightweight Charts for market views
- Recharts for executive KPI widgets

## Data and infra
- PostgreSQL
- Redis
- Docker Compose on Ubuntu for local deployment
- GitHub retained

## Principle
Do not rewrite Python quant logic into Java. Java is governance/control/API. Python remains quant engine core.
