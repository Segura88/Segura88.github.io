import React, { useState } from 'react'
import axios from 'axios'

export default function AdminLoginModal({ onClose, onLogin }: { onClose: () => void, onLogin: (token: string) => void }){
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function submit(){
    setError(null)
    setLoading(true)
    try{
  const API_BASE = (import.meta.env.VITE_API_BASE as string) || 'http://127.0.0.1:8000'
  const res = await axios.post(`${API_BASE.replace(/\/$/, '')}/admin/login`, { username, password })
      if(res.data && res.data.token){
        onLogin(res.data.token)
      } else {
        setError('Login failed')
      }
    }catch(e:any){
      setError(e?.response?.data?.detail || e.message || 'Error')
    }finally{
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center">
      <div className="bg-white p-6 rounded shadow w-80">
        <h3 className="text-lg font-semibold mb-4">Admin login</h3>
        <label className="block mb-2">
          <span className="text-sm text-gray-600">Usuario</span>
          <input className="w-full border rounded px-2 py-1" value={username} onChange={e=>setUsername(e.target.value)} />
        </label>
        <label className="block mb-4">
          <span className="text-sm text-gray-600">Contraseña</span>
          <input type="password" className="w-full border rounded px-2 py-1" value={password} onChange={e=>setPassword(e.target.value)} />
        </label>
        {error && <div className="text-red-600 mb-2">{error}</div>}
        <div className="flex justify-end gap-2">
          <button className="px-3 py-1" onClick={onClose}>Cerrar</button>
          <button className="px-3 py-1 bg-rose-500 text-white rounded" onClick={submit} disabled={loading}>{loading ? '...' : 'Entrar'}</button>
        </div>
      </div>
    </div>
  )
}
