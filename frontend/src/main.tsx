import '@fontsource/bowlby-one-sc/400.css'
import '@fontsource/sofia-sans/400.css'
import '@fontsource/sofia-sans/600.css'
import '@fontsource/sofia-sans/700.css'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import { AuthProvider } from './context/AuthProvider'
import './index.css'
import { createCookieAuthService } from './services/cookieAuthService'
import { setAuthHeadersProvider } from './services/httpClient'

// Raíz de composición: único punto donde se eligen implementaciones concretas.
const authService = createCookieAuthService()

setAuthHeadersProvider(() => authService.getAuthHeaders())

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider service={authService}>
      <App />
    </AuthProvider>
  </StrictMode>,
)
