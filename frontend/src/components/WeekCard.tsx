import React from 'react'

type Memory = { author: string; text: string; created_at: string; updated_at: string }
type Props = {
  week_monday: string
  status: 'pending' | 'written'
  memories?: Memory[]
}

export default function WeekCard({ week_monday, status, memories }: Props){
  const date = new Date(week_monday)
  const label = date.toLocaleDateString()
  return (
    <div className="card bg-white shadow-sm hover:shadow-md transition">
      <div className="card-body p-4">
        <div className="flex items-start justify-between">
          <div>
            <div className="text-xs text-rose-500">Semana de</div>
            <div className="text-lg font-serif font-semibold text-rose-800">{label}</div>
          </div>
          <div>
            {status === 'written' ? (
              <div className="badge badge-primary">Escrito</div>
            ) : (
              <div className="badge badge-ghost">Pendiente</div>
            )}
          </div>
        </div>

        {status === 'written' && memories && memories.length > 0 && (
          <div className="mt-3 space-y-3">
            {memories.map((mem, idx) => (
              <div key={idx} className="text-sm text-neutral border-l-4 border-rose-200 pl-3">
                <div className="text-xs text-rose-500/80 font-semibold">{mem.author}</div>
                <div className="mt-1">{mem.text}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
