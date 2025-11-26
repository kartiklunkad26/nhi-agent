# Frontend Overview

This directory contains the React/Vite frontend for the NHI Agent demo experience.

## Tech Stack
- React + TypeScript
- Vite
- Tailwind CSS + shadcn/ui

## Running the UI
```bash
# From the repository root
cd ui
npm install
npm run dev
```

By default the dev server runs on http://localhost:8080. Update `VITE_API_URL` in `ui/.env` if your API server is running elsewhere.

## Key Concepts
- **User Selector** emulates different IAM identities.
- **Security Mode Toggle** switches between admin-wide visibility and least-privilege secure mode.
- **Audit Log** tracks recent queries per mode for demonstrations.

For backend setup, troubleshooting tips, and quickstarts, refer to the documentation in `../docs/`.
