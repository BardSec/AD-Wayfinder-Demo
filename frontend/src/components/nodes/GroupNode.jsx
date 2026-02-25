import { Handle, Position } from 'reactflow'
import { Users } from 'lucide-react'

export default function GroupNode({ data, selected }) {
  return (
    <div
      className={`
        flex items-center gap-2.5 px-3 py-2.5 rounded-xl cursor-pointer
        border-2 shadow-md min-w-[160px] max-w-[210px]
        transition-all duration-150
        ${selected
          ? 'bg-emerald-50 border-emerald-500 shadow-emerald-200/60 shadow-lg'
          : 'bg-white border-emerald-300 hover:border-emerald-500 hover:shadow-lg'}
      `}
    >
      <Handle type="target" position={Position.Top} className="!bg-emerald-400" />

      <Users size={16} className="flex-shrink-0 text-emerald-500" />

      <div className="flex-1 min-w-0">
        <div className="font-semibold text-sm text-slate-800 truncate leading-tight">
          {data.name}
        </div>
        {data.memberCount !== undefined && (
          <div className="text-xs text-slate-400 leading-tight mt-0.5">
            {data.memberCount} member{data.memberCount !== 1 ? 's' : ''}
          </div>
        )}
      </div>

      <Handle type="source" position={Position.Bottom} className="!bg-emerald-400" />
    </div>
  )
}
