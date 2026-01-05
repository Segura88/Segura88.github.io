import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { useSearchParams } from 'react-router-dom'
import Header from '../components/Header'

export default function Write(){
  const [params] = useSearchParams()
  const urlToken = params.get('token') || null
  const storedToken = typeof window !== 'undefined' ? localStorage.getItem('memories_token') : null
  const token = urlToken || storedToken
  const [author, setAuthor] = useState<string | null>(null)
  const [text, setText] = useState('')
  const [status, setStatus] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(()=>{
  if(!token) return
    setLoading(true)
    axios.get(`/token/${token}`).then(r=>{
      setAuthor(r.data.author)
    }).catch(e=>{
      console.error(e)
      setStatus('Token inválido o expirado')
    }).finally(()=>setLoading(false))
  }, [token])

  function submit(){
    if(!token) return
    if(!text.trim()) { setStatus('Escribe algo antes de enviar'); return }
    setLoading(true)
    axios.post('/weekly-memory', { text }, { headers: { Authorization: `Bearer ${token}` }})
      .then(()=> setStatus('Enviado'))
      .catch(e=> {
        console.error(e)
        setStatus('Error al enviar')
      })
      .finally(()=> setLoading(false))
  }

  if(!token) return <div className="min-h-screen bg-slate-50"><Header /><main className="max-w-4xl mx-auto p-4">No hay token en la URL</main></div>

  return (
    <div className="min-h-screen bg-base-200">
      <Header />
      <main className="max-w-4xl mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Escribir recuerdo</h1>
        {loading ? (
          <div className="italic">Validando token...</div>
        ) : (
          <>
            {author && <div className="mb-2">Escribes como <strong>{author}</strong></div>}

            <div className="form-control">
              <textarea className="textarea textarea-bordered h-40" rows={8} value={text} onChange={e=>setText(e.target.value)} />
            </div>

            <div className="mt-4 flex items-center gap-3">
              <button onClick={submit} disabled={loading} className="btn btn-primary">{loading ? 'Enviando...' : 'Enviar'}</button>
              {status && <div className="text-sm text-neutral">{status}</div>}
            </div>
          </>
        )}
      </main>
    </div>
  )
}
