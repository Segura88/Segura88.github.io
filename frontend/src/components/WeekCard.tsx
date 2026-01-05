import React from 'react'

type Props = {
  week_monday: string
  status: 'pending' | 'written'
  author?: string
  text?: string
}

export default function WeekCard({ week_monday, status, author, text }: Props){
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

        {status === 'written' && (
          <div className="mt-3 text-sm text-neutral">
            <div className="text-xs text-rose-500/80">Por {author}</div>
            <div className="mt-1">{text}</div>
          </div>
        )}
      </div>
    </div>
  )
}
