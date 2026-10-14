# DeepShield frontend

This is the Next.js 14 frontend for DeepShield.

For the complete Windows/macOS/Linux setup, backend environment variables, API endpoint list, test commands and current limitations, see the repository-root README.md.

## Local development

~~~bash
npm ci
# Create a local config only if one does not already exist.
test -f .env.local || cp .env.example .env.local
npm run dev
~~~

On Windows PowerShell, preserve any existing configuration with: `if (-not (Test-Path .env.local)) { Copy-Item .env.example .env.local }`

The default backend URL is http://localhost:8000 and can be changed with NEXT_PUBLIC_API_URL in .env.local.

## Checks

~~~bash
npm test
npm run lint
npm run build
~~~
