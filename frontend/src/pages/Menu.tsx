import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Header from '../components/Header'

export default function Menu(){
  const [tab, setTab] = useState<'goals'|'unlinked'|'help'>('goals')

  // Objectives and unlinked memories stored in localStorage for now
  const [goals, setGoals] = useState<string[]>(() => JSON.parse(localStorage.getItem('memories_goals')||'[]'))
  const [unlinked, setUnlinked] = useState<string[]>(() => JSON.parse(localStorage.getItem('memories_unlinked')||'[]'))
  const [newGoal, setNewGoal] = useState('')
  const [newUnlinked, setNewUnlinked] = useState('')

  useEffect(()=>{
    const h = window.location.hash.replace('#','')
    if(h === 'goals' || h === 'unlinked' || h === 'help') setTab(h as any)
  }, [])

  useEffect(()=> localStorage.setItem('memories_goals', JSON.stringify(goals)), [goals])
  useEffect(()=> localStorage.setItem('memories_unlinked', JSON.stringify(unlinked)), [unlinked])

  function addGoal(){ if(!newGoal.trim()) return; setGoals([newGoal.trim(), ...goals]); setNewGoal('') }
  function removeGoal(i:number){ setGoals(goals.filter((_,idx)=> idx!==i)) }
  function addUnlinked(){ if(!newUnlinked.trim()) return; setUnlinked([newUnlinked.trim(), ...unlinked]); setNewUnlinked('') }
  function removeUnlinked(i:number){ setUnlinked(unlinked.filter((_,idx)=> idx!==i)) }

  return (
    <div className="min-h-screen bg-rose-50">
      <Header />
      <main className="max-w-4xl mx-auto p-4">
        <h1 className="text-3xl font-serif"><Link to="/" className="hover:underline">Gabriela & Jaime — Menú</Link></h1>

        <div className="mt-4">
          <div className="tabs">
            <button className={`tab ${tab==='goals' ? 'tab-active' : ''}`} onClick={()=>setTab('goals')}>Objetivos</button>
            <button className={`tab ${tab==='unlinked' ? 'tab-active' : ''}`} onClick={()=>setTab('unlinked')}>Recuerdos</button>
            <button className={`tab ${tab==='help' ? 'tab-active' : ''}`} onClick={()=>setTab('help')}>Ayuda</button>
          </div>

          <div className="mt-6">
            {tab === 'goals' && (
              <div>
                <div className="mb-3">
                  <input className="input input-bordered w-full" placeholder="Añadir objetivo" value={newGoal} onChange={e=>setNewGoal(e.target.value)} />
                  <div className="mt-2 flex gap-2">
                    <button className="btn btn-primary" onClick={addGoal}>Añadir</button>
                    <button className="btn btn-ghost" onClick={()=>{ setNewGoal('') }}>Cancelar</button>
                  </div>
                </div>
                <div className="space-y-2">
                  {goals.map((g,i)=> (
                    <div key={i} className="p-3 bg-white rounded-md shadow-sm flex justify-between items-start">
                      <div>{g}</div>
                      <button className="btn btn-sm btn-ghost" onClick={()=>removeGoal(i)}>Eliminar</button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {tab === 'unlinked' && (
              <div>
                <div className="mb-3">
                  <textarea className="textarea textarea-bordered w-full" rows={3} placeholder="Añadir recuerdo no fechado" value={newUnlinked} onChange={e=>setNewUnlinked(e.target.value)} />
                  <div className="mt-2 flex gap-2">
                    <button className="btn btn-primary" onClick={addUnlinked}>Añadir</button>
                    <button className="btn btn-ghost" onClick={()=> setNewUnlinked('') }>Cancelar</button>
                  </div>
                </div>
                <div className="space-y-2">
                  {unlinked.map((u,i)=> (
                    <div key={i} className="p-3 bg-white rounded-md shadow-sm flex justify-between items-start">
                      <div className="whitespace-pre-wrap">{u}</div>
                      <button className="btn btn-sm btn-ghost" onClick={()=>removeUnlinked(i)}>Eliminar</button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {tab === 'help' && (
              <div className="p-3 bg-white rounded-md shadow-sm text-sm">
                <p>Instrucciones rápidas:</p>
                <ul className="list-disc ml-5 mt-2">
                  <li>Para escribir en una semana, abre el enlace que recibes por email con <code>?token=...</code>.</li>
                  <li>Los objetivos y recuerdos no fechados se guardan localmente en este navegador (puedes exportarlos manualmente si lo deseas).</li>
                </ul>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
