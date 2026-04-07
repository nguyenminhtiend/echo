'use client';

import { useEffect, useRef } from 'react';

interface GraphNode {
  id: string;
  label: string;
  type: string;
}

interface GraphEdge {
  source: string;
  target: string;
  relation: string;
}

interface Props {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export function KnowledgeGraph({ nodes, edges }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || nodes.length === 0) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Simple force-directed layout placeholder
    // In production, replace with d3-force or react-force-graph
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#888';
    ctx.font = '14px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(
      `${nodes.length} nodes, ${edges.length} edges`,
      canvas.width / 2,
      canvas.height / 2,
    );
  }, [nodes, edges]);

  if (nodes.length === 0) {
    return (
      <div className="flex h-96 items-center justify-center text-muted-foreground">
        No graph data. Run <code>mise run index</code> to index the codebase.
      </div>
    );
  }

  return <canvas ref={canvasRef} width={800} height={600} className="w-full rounded border" />;
}
