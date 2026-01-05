import React, { useEffect, useMemo, useState } from 'react'
import axios from 'axios'
import Header from '../components/Header'
import WeekCard from '../components/WeekCard'
import { useSearchParams } from 'react-router-dom'

type Week = { week_monday: string; status: 'pending' | 'written'; author?: string; text?: string }

function todayMondayIso(){
  const now = new Date()
  // find the Monday of current week
  const day = now.getDay() || 7
  const diff = day - 1
  const monday = new Date(now)
  monday.setDate(now.getDate() - diff)
  monday.setHours(0,0,0,0)
  return monday.toISOString()
}

export default function Weeks(){
  const [weeks, setWeeks] = useState<Week[]>([])
  const [currentText, setCurrentText] = useState('')
  const [status, setStatus] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [editingWeek, setEditingWeek] = useState<string | null>(null)
  const [params] = useSearchParams()
  const urlToken = params.get('token') || ''
  const storedToken = typeof window !== 'undefined' ? localStorage.getItem('memories_token') || '' : ''
  const token = urlToken || storedToken
  const [author, setAuthor] = useState<string | null>(null)
  const [tokenValid, setTokenValid] = useState(false)
  const [toast, setToast] = useState<string | null>(null)

  useEffect(()=>{
    axios.get('/weeks').then(r=>setWeeks(r.data)).catch(console.error)
  }, [])

  useEffect(()=>{
    if(!token) return
    axios.get(`/token/${token}`).then(r=>{
      setAuthor(r.data.author)
      setTokenValid(true)
    }).catch(()=>{
      setAuthor(null)
      setTokenValid(false)
    })
  }, [token])

  const mondayIso = useMemo(()=> todayMondayIso(), [])

  const pastWeeks = useMemo(()=> weeks.filter(w => new Date(w.week_monday) <= new Date(mondayIso)).sort((a,b)=> +new Date(b.week_monday) - +new Date(a.week_monday)), [weeks, mondayIso])

  async function submitCurrent(){
    if(!tokenValid) { setStatus('Token inválido o ausente: abre el enlace desde tu email.'); return }
    if(!currentText.trim()) { setStatus('Escribe algo antes de confirmar'); return }
    if(currentText.length > 1000) { setStatus('Demasiado largo (máx 1000 caracteres)'); return }
    setLoading(true); setStatus(null)
    try{
      await axios.post('/weekly-memory', { text: currentText }, { headers: { Authorization: `Bearer ${token}` }})
      setStatus('Enviado ✅')
      setToast('Recuerdo guardado')
      setTimeout(()=> setToast(null), 3000)
      // refetch weeks
      const r = await axios.get('/weeks')
      setWeeks(r.data)
      setCurrentText('')
    }catch(e:any){
      console.error(e)
      setStatus(e?.response?.data?.detail || 'Error al enviar')
    }finally{ setLoading(false) }
  }

  return (
    <div className="min-h-screen bg-rose-50">
      <Header />
      <main className="max-w-4xl mx-auto p-4">
        <h1 className="text-3xl font-serif font-semibold text-rose-800 mb-4">Recuerdos 2026</h1>

        <section className="mb-6">
          <div className="card bg-white shadow-md p-4">
            <div className="text-sm text-rose-600">Semana actual</div>
            <div className="text-lg font-serif font-semibold text-rose-800">{new Date(mondayIso).toLocaleDateString()}</div>

            {tokenValid ? (
              <>
                {author && <div className="mb-2">Escribes como <strong>{author}</strong></div>}
                <div className="mt-3">
                  <textarea rows={6} className="textarea textarea-bordered w-full" value={currentText} onChange={e=>setCurrentText(e.target.value)} placeholder="Escribe aquí vuestro recuerdo de la semana..." />
                  <div className="text-xs text-neutral mt-1">{currentText.length} / 1000</div>
                </div>

                <div className="mt-3 flex items-center gap-3">
                  <button className="btn btn-rose" onClick={submitCurrent} disabled={loading}>{loading ? 'Enviando...' : 'Confirmar'}</button>
                  {status && <div className="text-sm text-neutral">{status}</div>}
                </div>
              </>
            ) : (
              <div className="italic text-sm text-rose-600">Abre este enlace desde el email para escribir (token en la URL). Si ya abriste el enlace y ves este mensaje, el token pudo expirar.</div>
            )}
            {status && <div className="mt-2 text-sm text-neutral">{status}</div>}
          </div>
        </section>

        <section>
          <h2 className="text-xl font-medium mb-3">Recuerdos pasados</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {pastWeeks.map(w=> (
              <div key={w.week_monday}>
                {editingWeek === w.week_monday ? (
                  <div className="card bg-white p-4 shadow-md">
                    <div className="text-sm text-rose-600">Semana de {new Date(w.week_monday).toLocaleDateString()}</div>
                    <textarea rows={5} className="textarea textarea-bordered w-full mt-2" value={currentText} onChange={e=>setCurrentText(e.target.value)} placeholder="Escribe aquí el recuerdo..." />
                    <div className="mt-2 flex gap-2">
                      <button className="btn btn-rose" onClick={()=> { submitCurrent(); setEditingWeek(null) }} disabled={loading}>{loading ? 'Enviando...' : 'Confirmar'}</button>
                      <button className="btn btn-ghost" onClick={()=> { setEditingWeek(null); setCurrentText('') }}>Cancelar</button>
                    </div>
                    {status && <div className="mt-2 text-sm text-neutral">{status}</div>}
                  </div>
                  ) : (
                  <div onClick={()=> { if(w.status === 'pending') { if(tokenValid){ setEditingWeek(w.week_monday); setCurrentText('') } else { setStatus('Para escribir en semanas pasadas abre el enlace recibido por email (token en la URL)') } } }} className={`cursor-pointer ${w.status === 'pending' ? 'hover:shadow-lg' : ''}`}>
                    <WeekCard week_monday={w.week_monday} status={w.status} author={w.author} text={w.text} />
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  )
}
