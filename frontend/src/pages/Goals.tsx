import React, { useEffect, useState } from 'react'
import Header from '../components/Header'
import axios from 'axios'
import { useSearchParams } from 'react-router-dom'

export default function Goals(){
  // Do NOT touch localStorage until token is validated. Use null to indicate "not loaded yet".
  const [goals, setGoals] = useState<any[] | null>(null)
  const [newGoal, setNewGoal] = useState('')
  const [params] = useSearchParams()
  const urlToken = params.get('token') || ''
  const storedToken = typeof window !== 'undefined' ? localStorage.getItem('memories_token') || '' : ''
  const token = urlToken || storedToken
  const [tokenValid, setTokenValid] = useState(false)

  useEffect(()=>{
    // token validation and load from backend
    if(!token) return
    const t = token
    axios.get(`/token/${t}`).then(async ()=>{
      setTokenValid(true)
      const auth = { headers: { Authorization: `Bearer ${t}` } }
      const r = await axios.get('/goals', auth)
      setGoals(r.data.map((g:any)=> g))
    }).catch(()=> setTokenValid(false))
  }, [token])

  async function addGoal(){
    if(!newGoal.trim()) return
    const t = token
    try{
      const auth = { headers: { Authorization: `Bearer ${t}` } }
      const r = await axios.post('/goals', { text: newGoal.trim() }, auth)
      setGoals(prev => prev ? [r.data, ...prev] : [r.data])
      setNewGoal('')
    }catch(err){ console.error(err) }
  }

  async function removeGoal(idx:number){
    if(!goals) return
    const item = goals[idx]
    if(!item) return
    const t = token
    try{
  await axios.delete(`/goals/${item.id}`, { headers: { Authorization: `Bearer ${t}` } })
  setGoals(prev => prev ? prev.filter((_,i)=> i!==idx) : prev)
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
        <h1 className="text-3xl font-serif font-semibold text-rose-800 mb-4">Objetivos</h1>

        <section className="mb-6">
          <div className="card bg-white shadow-md p-4">
            <div className="text-sm text-rose-600">Añadir objetivo</div>
            <input className="input input-bordered w-full mt-2" placeholder="Describe un objetivo" value={newGoal} onChange={e=>setNewGoal(e.target.value)} />
            <div className="mt-3 flex gap-2">
              <button className="btn btn-rose" onClick={addGoal}>Añadir</button>
              <button className="btn btn-ghost" onClick={()=> setNewGoal('')}>Cancelar</button>
            </div>
          </div>
        </section>

        <section>
          <h2 className="text-xl font-medium mb-3">Objetivos guardados</h2>
          <div className="space-y-3">
            {goals && goals.map((g:any,i)=> (
              <div key={g.id} className="p-3 bg-white rounded-md shadow-sm flex justify-between items-start">
                <div className="whitespace-pre-wrap">{g.text}</div>
                <button className="btn btn-sm btn-ghost" onClick={()=>removeGoal(i)}>Eliminar</button>
              </div>
            ))}
            {goals && goals.length === 0 && <div className="text-sm text-neutral">No hay objetivos todavía.</div>}
            {goals === null && <div className="text-sm text-neutral">Cargando...</div>}
          </div>
        </section>
      </main>
    </div>
  )
}
