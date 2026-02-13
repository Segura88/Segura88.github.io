import React, { useEffect, useState } from 'react'
import AdminLoginModal from './components/AdminLoginModal'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route, useLocation, useNavigate } from 'react-router-dom'
import './index.css'
import Weeks from './pages/Weeks'
import Write from './pages/Write'
import Goals from './pages/Goals'
import Unlinked from './pages/Unlinked'
import { useSearchParams } from 'react-router-dom'
import axios from 'axios'

const API_BASE = (import.meta.env.VITE_API_BASE as string) || 'http://127.0.0.1:8000'
axios.defaults.baseURL = API_BASE.replace(/\/$/, '')

function App(){
  return (
    <BrowserRouter>
      <TokenGate>
        <Routes>
          <Route path="/" element={<Weeks/>} />
          <Route path="/write" element={<Write/>} />
          <Route path="/goals" element={<Goals/>} />
          <Route path="/unlinked" element={<Unlinked/>} />
        </Routes>
      </TokenGate>
    </BrowserRouter>
  )
}

function TokenGate({ children }: { children: React.ReactNode }){
  const [params] = useSearchParams()
  const location = useLocation()
  const navigate = useNavigate()
  // Prefer token from URL param; fallback to localStorage so token persists across tabs
  const urlToken = params.get('token') || ''
  const pathMatch = location.pathname.match(/^\/token\/([^/]+)$/)
  const pathToken = pathMatch ? decodeURIComponent(pathMatch[1]) : ''
  const storedToken = typeof window !== 'undefined' ? localStorage.getItem('memories_token') : null
  const [tokenValid, setTokenValid] = useState<boolean | null>(null)
  const [activeToken, setActiveToken] = useState<string | null>(urlToken || pathToken || storedToken)
  const [showAdmin, setShowAdmin] = useState(false)

  useEffect(()=>{
    if (!urlToken && pathToken) {
      navigate(`/?token=${encodeURIComponent(pathToken)}`, { replace: true })
    }
    let tokenToCheck = urlToken || pathToken || storedToken
    console.debug('[TokenGate] tokenToCheck=', tokenToCheck)
    if(!tokenToCheck){ setTokenValid(false); return }
    let mounted = true
    axios.get(`/token/${tokenToCheck}`).then((res)=>{
      console.debug('[TokenGate] token validation success', res && res.data)
      if(!mounted) return
      setTokenValid(true)
      setActiveToken(tokenToCheck)
      try { localStorage.setItem('memories_token', tokenToCheck) } catch(e){}
    }).catch((err)=>{
      console.debug('[TokenGate] token validation error', err && (err.response ? err.response.data : err.message))
      if(!mounted) return
      setTokenValid(false)
      setActiveToken(null)
      try { localStorage.removeItem('memories_token') } catch(e){}
    })
    return ()=>{ mounted = false }
  }, [urlToken, pathToken, storedToken, navigate])

  // splash shown when token missing or invalid; while checking tokenValid===null show splash too
  if(!tokenValid){
    return (
      <div className="min-h-screen bg-rose-50 flex items-center justify-center">
        <div className="text-center">
          <div
            className="w-28 h-28 mx-auto rounded-md bg-gradient-to-br from-pink-400 to-rose-600 flex items-center justify-center text-white font-bold text-2xl"
            onDoubleClick={() => setShowAdmin(true)}
            title="Memories logo (double-click for admin)"
          >M</div>
          <h1 className="mt-4 text-3xl font-serif text-rose-800">Memories</h1>
          <p className="mt-2 text-neutral">Accede desde el enlace proporcionado en el email para ver el contenido de la web.</p>
        </div>
        {showAdmin && <AdminLoginModal onClose={() => setShowAdmin(false)} onLogin={(token) => {
          try { localStorage.setItem('memories_admin_token', token) } catch(e){}
          setShowAdmin(false)
        }} />}
      </div>
    )
  }

  return <>{children}</>
}

createRoot(document.getElementById('root')!).render(<App />)
