import React  from 'react'
import { createRoot } from 'react-dom/client'
import App from './components/App.jsx'
import AuthForm from './components/AuthForm.jsx'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'


createRoot(document.getElementById('root')).render(
  <React.StrictMode>
   <BrowserRouter>
      <Routes>
      <Route path="/" element={<Navigate to="/login" />}/>
        <Route path="/signup" element={<AuthForm />} />
        <Route path="/login" element={<AuthForm />} />
        <Route path="/app" element={<App />} />
        <Route path="/logout" element={<App />} />
      </Routes>
    </BrowserRouter>
</React.StrictMode>
)
