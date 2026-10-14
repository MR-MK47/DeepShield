/** Local source-level smoke checks; browser interaction is covered separately. */
const fs = require('node:fs')
const path = require('node:path')

const root = __dirname
const read = relative => fs.readFileSync(path.join(root, relative), 'utf8')
const exists = relative => fs.existsSync(path.join(root, relative))
const checks = [
  ['scan route exists', () => exists('src/app/scan/page.tsx') && exists('src/app/scan/ScanClient.tsx')],
  ['scan history route exists', () => exists('src/app/history/page.tsx') && exists('src/app/history/HistoryClient.tsx')],
  ['login and signup routes exist', () => exists('src/app/login/LoginClient.tsx') && exists('src/app/signup/SignupClient.tsx')],
  ['authentication API functions are wired', () => {
    const api = read('src/lib/api.ts')
    return ['registerOperator', 'loginOperator', 'logoutOperator', 'getCurrentOperator'].every(name => api.includes('function ' + name))
  }],
  ['scan pipeline API functions are wired', () => {
    const api = read('src/lib/api.ts')
    return ['analyzeImage', 'searchMatches', 'dispatchTakedown', 'generateDossier'].every(name => api.includes('function ' + name))
  }],
  ['legal notice requires preview and explicit confirmation', () => read('src/components/ActionPanel.tsx').includes('I reviewed the draft — send email') && read('src/components/ActionPanel.tsx').includes('Load recipient and notice preview')],
  ['website contact discovery, editable recipient, and portal modal are wired', () => {
    const panel = read('src/components/ActionPanel.tsx')
    const api = read('src/lib/api.ts')
    return panel.includes('id="notice-recipient"') && panel.includes('createPortal') && panel.includes('Search public contacts again') && api.includes('discoverContactEmails') && !panel.includes('<option value="Meta">')
  }],
  ['real SMTP test email is available to signed-in operators', () => {
    const scan = read('src/app/scan/ScanClient.tsx')
    const api = read('src/lib/api.ts')
    const backend = read('../backend/main.py')
    const service = read('../backend/services/legal_email.py')
    return scan.includes('Send test email') && scan.includes('sendTestEmail') && api.includes('/api/email/test') && backend.includes('/api/email/test') && service.includes('SMTP_SSL') && service.includes('starttls')
  }],
  ['notice and dossier API calls attach operator authorization', () => {
    const api = read('src/lib/api.ts')
    return api.includes('authHeaders') && api.includes('/api/takedown/email') && api.includes('/api/dossier')
  }],
  ['old authentication stubs are removed', () => {
    const login = read('src/app/login/LoginClient.tsx')
    const signup = read('src/app/signup/SignupClient.tsx')
    return !login.includes('Authentication stub') && !signup.includes('Account creation stub')
  }],
  ['history is opt-in and deletable', () => {
    const uploader = read('src/components/ImageUploader.tsx')
    const api = read('src/lib/api.ts')
    return uploader.includes('Save these results to my account history') && api.includes('fetchScanHistory') && api.includes('deleteScanHistory')
  }],
  ['backend auth and scan endpoints exist', () => {
    const backend = read('../backend/main.py')
    return backend.includes('/api/auth/register') && backend.includes('/api/auth/login') && backend.includes('/api/auth/logout') && backend.includes('/api/scan') && backend.includes('/api/matches')
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
