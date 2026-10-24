import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './app/App'
import AppProviders from './app/providers'
import { RouterProvider } from './app/router'
import './index.css'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AppProviders>
      <RouterProvider>
        <App />
      </RouterProvider>
    </AppProviders>
  </StrictMode>
)
