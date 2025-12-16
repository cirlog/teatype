# Teatype Dashboard (React)

Modern React + Vite frontend for the Modulo dashboard. It consumes the FastAPI `/status` endpoint and renders
live telemetry using SCSS-driven styling.

## Scripts

-   `pnpm dev` – Launch the Vite dev server on `http://localhost:5173`
-   `pnpm build` – Produce a production build under `dist/`
-   `pnpm preview` – Preview the production build locally.

The accompanying CLI scripts under `scripts/frontend/react-dashboard` wrap these commands and also take care of
installing Node + pnpm when required.
