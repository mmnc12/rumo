import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import tseslint from 'typescript-eslint'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      tseslint.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      globals: globals.browser,
    },
    rules: {
      // Regra nova do react-hooks v7+ (React 19) que reclama de setState
      // síncrono dentro de useEffect. Nossos usos são padrões canônicos
      // (boot do AuthContext, sync com localStorage) — React 18/19 faz
      // batching e não há cascata real. Desabilitada pra evitar ruído.
      'react-hooks/set-state-in-effect': 'off',
    },
  },
])