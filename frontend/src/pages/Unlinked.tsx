import React, { useEffect, useState } from 'react'
import Header from '../components/Header'
import axios from 'axios'
import { useSearchParams } from 'react-router-dom'

export default function Unlinked(){
  const [items, setItems] = useState<any[] | null>(null)
  const [newItem, setNewItem] = useState('')
  const [params] = useSearchParams()
  const urlToken = params.get('token') || ''
  const storedToken = typeof window !== 'undefined' ? localStorage.getItem('memories_token') || '' : ''
  const token = urlToken || storedToken
  const [tokenValid, setTokenValid] = useState(false)

  useEffect(()=>{
    if(!token) return
    axios.get(`/token/${token}`).then(async ()=>{
      setTokenValid(true)
      const r = await axios.get('/unlinked', { headers: { Authorization: `Bearer ${token}` } })
      setItems(r.data.map((u:any)=> u))
    }).catch(()=> setTokenValid(false))
  }, [token])

  useEffect(()=>{
    // no-op: backend persists
  }, [items, tokenValid])

  async function addItem(){
    if(!newItem.trim()) return
    const t = token
    try{
      const r = await axios.post('/unlinked', { text: newItem.trim() }, { headers: { Authorization: `Bearer ${t}` } })
      setItems(prev => prev ? [r.data, ...prev] : [r.data])
      setNewItem('')
    }catch(err){ console.error(err) }
  }

  async function removeItem(idx:number){
    if(!items) return
    const item = items[idx]
    if(!item) return
    const t = token
    try{
      await axios.delete(`/unlinked/${item.id}`, { headers: { Authorization: `Bearer ${t}` } })
      setItems(prev => prev ? prev.filter((_,i)=> i!==idx) : prev)
    }catch(err){ console.error(err) }
  }

  if(!tokenValid){
    return (
      <div className="min-h-screen bg-rose-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-28 h-28 mx-auto rounded-md bg-gradient-to-br from-pink-400 to-rose-600 flex items-center justify-center text-white font-bold text-2xl">M</div>
          <h1 className="mt-4 text-3xl font-serif text-rose-800">Memories</h1>
          <p className="mt-2 text-neutral">Accede desde el enlace proporcionado en el email para ver el contenido de la web.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-rose-50">
      <Header />
      <main className="max-w-4xl mx-auto p-4">
        <h1 className="text-3xl font-serif font-semibold text-rose-800 mb-4">Recuerdos no fechados</h1>

        <section className="mb-6">
          <div className="card bg-white shadow-md p-4">
            <div className="text-sm text-rose-600">Añadir recuerdo</div>
            <textarea className="textarea textarea-bordered w-full mt-2" rows={4} placeholder="Escribe un recuerdo que no está asociado a una semana" value={newItem} onChange={e=>setNewItem(e.target.value)} />
            <div className="mt-3 flex gap-2">
              <button className="btn btn-rose" onClick={addItem}>Añadir</button>
              <button className="btn btn-ghost" onClick={()=> setNewItem('')}>Cancelar</button>
            </div>
          </div>
        </section>

        <section>
          <h2 className="text-xl font-medium mb-3">Recuerdos guardados</h2>
          <div className="space-y-3">
            {items && items.map((u,i)=> (
              <div key={i} className="p-3 bg-white rounded-md shadow-sm flex justify-between items-start">
                <div className="whitespace-pre-wrap">{u}</div>
                <button className="btn btn-sm btn-ghost" onClick={()=>removeItem(i)}>Eliminar</button>
              </div>
            ))}
            {items && items.length === 0 && <div className="text-sm text-neutral">No hay recuerdos guardados todavía.</div>}
            {items === null && <div className="text-sm text-neutral">Cargando...</div>}
          </div>
        </section>
      </main>
    </div>
  )
}
