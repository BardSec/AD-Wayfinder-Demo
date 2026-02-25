import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
} from 'reactflow'
import 'reactflow/dist/style.css'
import dagre from 'dagre'
import { api } from '../api/adApi'
import DomainNode from './nodes/DomainNode'
import OUNode from './nodes/OUNode'
import GroupNode from './nodes/GroupNode'
import { Loader2, Info } from 'lucide-react'

// ── Node type registry (must be stable — defined outside component) ───────────
const nodeTypes = {
  domainNode: DomainNode,
  ouNode: OUNode,
  groupNode: GroupNode,
}

// ── Layout helpers ────────────────────────────────────────────────────────────
const NODE_W = 220
const NODE_H = 70

function layoutGraph(nodes, edges) {
  const g = new dagre.graphlib.Graph()
  g.setDefaultEdgeLabel(() => ({}))
  g.setGraph({ rankdir: 'TB', ranksep: 70, nodesep: 50 })
  nodes.forEach((n) => g.setNode(n.id, { width: NODE_W, height: NODE_H }))
  edges.forEach((e) => g.setEdge(e.source, e.target))
  dagre.layout(g)
  return nodes.map((n) => {
    const { x, y } = g.node(n.id)
    return { ...n, position: { x: x - NODE_W / 2, y: y - NODE_H / 2 } }
  })
}

function nodeId(type, dn) {
  return `${type}::${dn}`
}

function edgeId(srcDn, tgtDn) {
  return `edge::${srcDn}::${tgtDn}`
}

// ── Component ─────────────────────────────────────────────────────────────────
export default function TopologyMap({ onNodeSelect, selectedDn }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const expandedRef = useRef(new Set())   // tracks expanded OU DNs
  const childrenRef = useRef({})          // parentDn → [childNodeIds]

  // ── Load initial tree ───────────────────────────────────────────────────────
  useEffect(() => {
    api.getTree()
      .then(({ domain, children }) => {
        const initNodes = []
        const initEdges = []

        // Domain node
        initNodes.push({
          id: nodeId('domain', domain.dn),
          type: 'domainNode',
          data: { name: domain.name, dn: domain.dn, type: 'domain' },
          position: { x: 0, y: 0 },
        })

        // Top-level OU nodes
        children.forEach((ou) => {
          const id = nodeId('ou', ou.dn)
          initNodes.push({
            id,
            type: 'ouNode',
            data: { name: ou.name, dn: ou.dn, type: 'ou', hasChildren: true, expanded: false, alertCount: 0 },
            position: { x: 0, y: 0 },
          })
          initEdges.push({
            id: edgeId(domain.dn, ou.dn),
            source: nodeId('domain', domain.dn),
            target: id,
            animated: false,
          })
        })

        const laid = layoutGraph(initNodes, initEdges)
        setNodes(laid)
        setEdges(initEdges)
        setLoading(false)
      })
      .catch((e) => { setError(e.message); setLoading(false) })
  }, [])

  // ── Highlight selected node ─────────────────────────────────────────────────
  useEffect(() => {
    setNodes((nds) =>
      nds.map((n) => ({
        ...n,
        selected: n.data?.dn === selectedDn,
      }))
    )
  }, [selectedDn])

  // ── Expand / collapse an OU ─────────────────────────────────────────────────
  const toggleOU = useCallback(async (ouData) => {
    const { dn } = ouData
    const expanded = expandedRef.current

    if (expanded.has(dn)) {
      // ── Collapse ──────────────────────────────────────────────────────────
      // Recursively collect all descendant node IDs
      const toRemove = new Set()
      const queue = [dn]
      while (queue.length) {
        const parent = queue.shift()
        const kids = childrenRef.current[parent] || []
        kids.forEach((kid) => {
          toRemove.add(kid)
          queue.push(kid.replace(/^(ou|group)::/, ''))
        })
        expanded.delete(parent)
      }
      expanded.delete(dn)

      setNodes((nds) =>
        nds
          .filter((n) => !toRemove.has(n.id))
          .map((n) =>
            n.data?.dn === dn
              ? { ...n, data: { ...n.data, expanded: false } }
              : n
          )
      )
      setEdges((eds) =>
        eds.filter((e) => !toRemove.has(e.target))
      )
      delete childrenRef.current[dn]
    } else {
      // ── Expand ────────────────────────────────────────────────────────────
      const contents = await api.getOU(dn)
      const newNodes = []
      const newEdges = []
      const childIds = []

      contents.child_ous.forEach((ou) => {
        const id = nodeId('ou', ou.dn)
        childIds.push(id)
        newNodes.push({
          id,
          type: 'ouNode',
          data: { name: ou.name, dn: ou.dn, type: 'ou', hasChildren: true, expanded: false, alertCount: 0 },
          position: { x: 0, y: 0 },
        })
        newEdges.push({
          id: edgeId(dn, ou.dn),
          source: nodeId('ou', dn),
          target: id,
        })
      })

      contents.groups.forEach((g) => {
        const id = nodeId('group', g.dn)
        childIds.push(id)
        newNodes.push({
          id,
          type: 'groupNode',
          data: { name: g.name, dn: g.dn, type: 'group', memberCount: g.member_count },
          position: { x: 0, y: 0 },
        })
        newEdges.push({
          id: edgeId(dn, g.dn),
          source: nodeId('ou', dn),
          target: id,
        })
      })

      childrenRef.current[dn] = childIds
      expanded.add(dn)

      setNodes((prev) => {
        const updated = prev.map((n) =>
          n.data?.dn === dn ? { ...n, data: { ...n.data, expanded: true } } : n
        )
        const all = [...updated, ...newNodes]
        setEdges((prevEdges) => {
          const allEdges = [...prevEdges, ...newEdges]
          const laid = layoutGraph(all, allEdges)
          // Use setTimeout to allow edges state to sync before setting nodes
          setTimeout(() => setNodes(laid), 0)
          return allEdges
        })
        return all
      })
    }
  }, [])

  // ── Handle node click ───────────────────────────────────────────────────────
  const onNodeClick = useCallback((_, node) => {
    const { data } = node
    if (data.type === 'ou') {
      toggleOU(data)
    }
    onNodeSelect(data)
  }, [toggleOU, onNodeSelect])

  // ── Minimap node colour ─────────────────────────────────────────────────────
  const minimapColor = useCallback((node) => {
    if (node.type === 'domainNode') return '#4f46e5'
    if (node.type === 'ouNode') return '#d97706'
    if (node.type === 'groupNode') return '#059669'
    return '#94a3b8'
  }, [])

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-3 text-slate-500">
          <Loader2 size={32} className="animate-spin text-indigo-500" />
          <span className="text-sm">Loading Active Directory tree…</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-full flex items-center justify-center bg-slate-50">
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 max-w-md text-center">
          <p className="text-red-700 font-semibold mb-1">Failed to load AD tree</p>
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full w-full relative">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        onNodeClick={onNodeClick}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.1}
        maxZoom={2}
        defaultEdgeOptions={{ type: 'smoothstep', style: { stroke: '#cbd5e1', strokeWidth: 2 } }}
      >
        <Background color="#e2e8f0" gap={20} />
        <Controls className="!bottom-4 !left-4" />
        <MiniMap
          nodeColor={minimapColor}
          className="!bottom-4 !right-4"
          maskColor="rgba(241,245,249,0.8)"
        />
      </ReactFlow>

      {/* Legend */}
      <div className="absolute top-3 left-3 bg-white/90 backdrop-blur-sm rounded-lg border border-slate-200 px-3 py-2 shadow-sm flex items-center gap-4 text-xs text-slate-600">
        <LegendDot color="bg-indigo-500" label="Domain" />
        <LegendDot color="bg-amber-400" label="OU (click to expand)" />
        <LegendDot color="bg-emerald-500" label="Group" />
      </div>

      {nodes.length <= 1 && !loading && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="bg-white/80 backdrop-blur border border-slate-200 rounded-xl p-5 text-slate-500 flex items-center gap-2 shadow">
            <Info size={16} />
            <span className="text-sm">Click the domain or an OU node to explore the tree</span>
          </div>
        </div>
      )}
    </div>
  )
}

function LegendDot({ color, label }) {
  return (
    <span className="flex items-center gap-1.5">
      <span className={`w-2.5 h-2.5 rounded-full ${color} flex-shrink-0`} />
      {label}
    </span>
  )
}
