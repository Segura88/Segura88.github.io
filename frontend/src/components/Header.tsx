import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'

export default function Header(){
  const [open, setOpen] = useState(false)
  const [recent, setRecent] = useState<Array<{week_monday:string; text?:string; status?:string}>>([])
  const [showHelp, setShowHelp] = useState(false)

  useEffect(()=>{
    axios.get('/weeks').then(r=> setRecent(r.data.filter((w:any)=> new Date(w.week_monday) <= new Date()).slice(0,10))).catch(()=>{})
  }, [])

  return (
    <>
      <header className="bg-gradient-to-r from-rose-50 via-amber-50 to-rose-50 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <button onClick={()=> setOpen(true)} className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-md bg-gradient-to-br from-pink-400 to-rose-600 flex items-center justify-center text-white font-bold text-lg">M</div>
            <div>
              <div className="text-xl font-serif text-rose-800">Gabriela & Jaime</div>
              <div className="text-sm text-rose-600">Recuerdos Año 2026</div>
            </div>
          </button>

          <nav>
            {/* empty */}
          </nav>
        </div>
      </header>

      {/* Sidebar */}
      <div className={`fixed inset-0 z-50 pointer-events-none ${open ? '' : 'hidden'}`}>
        <div className="absolute inset-0 bg-black/40" onClick={()=> setOpen(false)} />
        <aside className={`absolute left-0 top-0 bottom-0 w-80 bg-white shadow-xl p-4 overflow-auto pointer-events-auto`}>
            <div className="flex items-center justify-between">
              <Link to="/" className="text-xl font-serif hover:underline" onClick={()=> setOpen(false)}>Gabriela & Jaime</Link>
              <button className="btn btn-ghost" onClick={()=> { setOpen(false); setShowHelp(false) }}>Cerrar</button>
            </div>

          <nav className="mt-4 space-y-3">
            <div className="font-medium">Secciones</div>
            <Link to="/" className="block text-rose-600 hover:underline" onClick={()=> setOpen(false)}>Semanas</Link>
            <Link to="/goals" className="block text-rose-600 hover:underline" onClick={()=> setOpen(false)}>Objetivos</Link>
            <Link to="/unlinked" className="block text-rose-600 hover:underline" onClick={()=> setOpen(false)}>Recuerdos</Link>
            <button className="block text-left text-rose-600 hover:underline btn btn-ghost p-0" onClick={()=> setShowHelp(true)}>Ayuda</button>

            <div className="mt-4 font-medium">Recuerdos recientes</div>
            <div className="mt-2 space-y-2">
              {recent.map(r=> (
                <div key={r.week_monday} className="text-sm text-neutral">
                  <div className="text-rose-600">Semana de {new Date(r.week_monday).toLocaleDateString()}</div>
                  <div className="text-xs text-neutral truncate">{r.text || (r.status==='pending' ? 'Pendiente' : 'Sin texto')}</div>
                </div>
              ))}
            </div>

            {showHelp && (
              <div className="mt-4 p-3 bg-rose-50 rounded-md border border-rose-100 text-sm">
                <div className="font-medium mb-2">Ayuda rápida</div>
                <p>Instrucciones rápidas:</p>
                <ul className="list-disc ml-5 mt-2">
                  <li>Para escribir en una semana, abre el enlace que recibes por email con <code>?token=...</code>.</li>
                  <li>Los objetivos y recuerdos no fechados se guardan localmente en este navegador.</li>
                </ul>
                <div className="mt-3 text-right">
                  <button className="btn btn-sm btn-ghost" onClick={()=> setShowHelp(false)}>Cerrar ayuda</button>
                </div>
              </div>
            )}
          </nav>
        </aside>
      </div>
    </>
  )
}
