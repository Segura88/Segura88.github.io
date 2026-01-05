import React from 'react'

type Props = { title?: string, children: React.ReactNode, onClose: ()=>void }

export default function Modal({ title, children, onClose }: Props){
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white rounded-md p-4 max-w-lg w-full">
        <div className="flex justify-between items-center">
          <div className="text-lg font-medium">{title}</div>
          <button className="btn btn-ghost" onClick={onClose}>Cerrar</button>
        </div>
        <div className="mt-3">{children}</div>
      </div>
    </div>
  )
}
