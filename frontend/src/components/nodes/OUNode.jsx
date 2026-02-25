import { Handle, Position } from 'reactflow'
import { Folder, FolderOpen, ChevronRight, AlertTriangle } from 'lucide-react'

export default function OUNode({ data, selected }) {
  const FolderIcon = data.expanded ? FolderOpen : Folder

  return (
    <div
      className={`
        flex items-center gap-2.5 px-3 py-2.5 rounded-xl cursor-pointer
        border-2 shadow-md min-w-[180px] max-w-[220px]
        transition-all duration-150
        ${selected
          ? 'bg-amber-50 border-amber-500 shadow-amber-200/60 shadow-lg'
          : 'bg-white border-amber-300 hover:border-amber-500 hover:shadow-lg'}
      `}
    >
      <Handle type="target" position={Position.Top} className="!bg-amber-400" />

      <FolderIcon
        size={18}
        className={`flex-shrink-0 ${data.expanded ? 'text-amber-500' : 'text-amber-400'}`}
      />

      <div className="flex-1 min-w-0">
        <div className="font-semibold text-sm text-slate-800 truncate leading-tight">
          {data.name}
        </div>
        {(data.hasChildren) && (
          <div className="text-xs text-slate-400 leading-tight mt-0.5">
            {data.expanded ? 'Click to collapse' : 'Click to expand'}
          </div>
        )}
      </div>

      {data.alertCount > 0 && (
        <span className="flex items-center gap-0.5 bg-red-100 text-red-600 text-xs font-bold px-1.5 py-0.5 rounded-full flex-shrink-0">
          <AlertTriangle size={10} />
          {data.alertCount}
        </span>
      )}

      {data.hasChildren && (
        <ChevronRight
          size={14}
          className={`flex-shrink-0 text-amber-400 transition-transform ${data.expanded ? 'rotate-90' : ''}`}
        />
      )}

      <Handle type="source" position={Position.Bottom} className="!bg-amber-400" />
    </div>
  )
}
