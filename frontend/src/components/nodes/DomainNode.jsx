import { Handle, Position } from 'reactflow'
import { Globe } from 'lucide-react'

export default function DomainNode({ data, selected }) {
  return (
    <div
      className={`
        flex items-center gap-2.5 px-4 py-3 rounded-xl cursor-pointer
        bg-indigo-600 text-white border-2 shadow-lg min-w-[160px]
        transition-all duration-150
        ${selected ? 'border-indigo-300 shadow-indigo-300/50 shadow-xl' : 'border-indigo-500 hover:border-indigo-300'}
      `}
    >
      <Globe size={18} className="flex-shrink-0 text-indigo-200" />
      <div className="min-w-0">
        <div className="font-bold text-sm truncate leading-tight">{data.name}</div>
        <div className="text-indigo-200 text-xs leading-tight">Domain Root</div>
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-indigo-300" />
    </div>
  )
}
