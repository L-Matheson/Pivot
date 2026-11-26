// Thin wrapper: ensures .env, adds the `db` profile once Alembic is set up, runs docker compose.
import { existsSync } from 'node:fs'
import { spawnSync } from 'node:child_process'

if (!existsSync('.env')) {
  const { copyFileSync } = await import('node:fs')
  copyFileSync('.env.example', '.env')
  console.log('Created .env from .env.example')
}
const profile = existsSync('backend/alembic.ini') ? ['--profile', 'db'] : []
const r = spawnSync('docker', ['compose', ...profile, ...process.argv.slice(2)], {
  stdio: 'inherit',
  shell: false,
})
process.exit(r.status ?? 1)
