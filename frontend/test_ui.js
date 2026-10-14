/** Local source-level smoke checks; browser interaction is covered separately. */
const fs = require('node:fs')
const path = require('node:path')

const root = __dirname
const read = relative => fs.readFileSync(path.join(root, relative), 'utf8')
const exists = relative => fs.existsSync(path.join(root, relative))
const checks = [
  ['scan route exists', () => exists('src/app/scan/page.tsx') && exists('src/app/scan/ScanClient.tsx')],
  ['login and signup routes exist', () => exists('src/app/login/LoginClient.tsx') && exists('src/app/signup/SignupClient.tsx')],
  ['authentication API functions are wired', () => {
    const api = read('src/lib/api.ts')
    return ['registerOperator', 'loginOperator', 'logoutOperator', 'getCurrentOperator'].every(name => api.includes('function ' + name))
  }],
  ['scan pipeline API functions are wired', () => {
    const api = read('src/lib/api.ts')
    return ['analyzeImage', 'searchMatches', 'dispatchTakedown', 'generateDossier'].every(name => api.includes('function ' + name))
  }],
  ['legal notice requires confirmation', () => read('src/components/ActionPanel.tsx').includes('I reviewed the draft — send notice') && read('src/components/ActionPanel.tsx').includes('Load recipient and notice preview')],
  ['notice and dossier API calls attach operator authorization', () => {
    const api = read('src/lib/api.ts')
    return api.includes('authHeaders') && api.includes('/api/takedown/email') && api.includes('/api/dossier')
  }],
  ['old authentication stubs are removed', () => {
    const login = read('src/app/login/LoginClient.tsx')
    const signup = read('src/app/signup/SignupClient.tsx')
    return !login.includes('Authentication stub') && !signup.includes('Account creation stub')
  }],
  ['backend auth endpoints exist', () => {
    const backend = read('../backend/main.py')
    return backend.includes('/api/auth/register') && backend.includes('/api/auth/login') && backend.includes('/api/auth/logout')
  }],
]

let failed = 0
for (const [label, run] of checks) {
  let passed = false
  try { passed = Boolean(run()) } catch (error) { console.error(error) }
  console.log((passed ? 'PASS' : 'FAIL') + '  ' + label)
  if (!passed) failed += 1
}
console.log('\n' + (checks.length - failed) + '/' + checks.length + ' smoke checks passed.')
if (failed) process.exit(1)
