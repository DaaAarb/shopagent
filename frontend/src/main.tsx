import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import { AuthProvider } from './context/AuthProvider'
import './index.css'
import { createDemoAuthService } from './services/demoAuthService'
import { setAuthHeadersProvider } from './services/httpClient'

// Composición: el ÚNICO sitio que elige implementaciones concretas y las conecta.
// Para un login real, se cambia esta línea por otra implementación de AuthService.
const authService = createDemoAuthService()

// El cliente HTTP pide las cabeceras de auth en cada petición, sin conocer al servicio.
setAuthHeadersProvider(() => authService.getAuthHeaders())

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider service={authService}>
      <App />
    </AuthProvider>
  </StrictMode>,
)
