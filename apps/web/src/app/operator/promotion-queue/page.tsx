"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useEffect, useState } from "react";

type DeploymentRecord = {
  id: string;
  strategyName: string;
  strategyVersion: string;
  instrument: string;
  venue: string;
  stage: string;
  environment: string;
  enabled: boolean;
  meta?: Record<string, unknown> | null;
};

const CONTROL_PLANE_URL = process.env.NEXT_PUBLIC_CONTROL_PLANE_URL || "http://localhost:8081";

function metricFromMeta(meta: Record<string, unknown> | null | undefined, key: string): string {
  if (!meta || typeof meta[key] !== "number") return "—";
  return String(meta[key]);
}

export default function PromotionQueuePage() {
  const [deployments, setDeployments] = useState<DeploymentRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionBusy, setActionBusy] = useState<string | null>(null);

  async function fetchDeployments() {
    try {
      const res = await fetch(`${CONTROL_PLANE_URL}/api/deployments`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setDeployments(Array.isArray(data) ? data : []);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load deployments");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let cancelled = false;
    (async () => {
      await fetchDeployments();
    })();
    return () => { cancelled = true; };
  }, []);

  async function promote(deploymentId: string, fromStage: string, toStage: string) {
    setActionBusy(deploymentId);
    try {
      const patchRes = await fetch(`${CONTROL_PLANE_URL}/api/deployments/${deploymentId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ stage: toStage }),
      });
      if (!patchRes.ok) throw new Error(`PATCH failed: ${patchRes.status}`);
      await fetch(`${CONTROL_PLANE_URL}/api/promotion-review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          strategyId: deploymentId,
          fromStage,
          toStage,
          decision: "approved",
        }),
      });
      await fetchDeployments();
    } catch (e) {
      console.error(e);
    } finally {
      setActionBusy(null);
    }
  }

  if (loading) {
    return (
      <div>
        <Card>
          <CardHeader><CardTitle>Promotion Queue</CardTitle></CardHeader>
          <CardContent><p className="text-sm text-gray-400">Loading deployments…</p></CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <Card>
          <CardHeader><CardTitle>Promotion Queue</CardTitle></CardHeader>
          <CardContent>
            <p className="text-sm text-nebula-red">Error: {error}</p>
            <p className="mt-2 text-xs text-gray-400">Ensure the control plane is running (port 8081).</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader><CardTitle>Promotion Queue</CardTitle></CardHeader>
        <CardContent>
          <p className="text-sm text-gray-400 mb-4">Approve promotion of strategies. Actions are logged to the audit trail.</p>
          {deployments.length === 0 ? (
            <p className="text-sm text-gray-400">No deployments in the registry. Add strategies via the deployments API.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm border-collapse border border-nebula-cyan/30">
                <thead>
                  <tr className="bg-nebula-cyan/10">
                    <th className="border border-nebula-cyan/30 px-3 py-2 text-left">Strategy</th>
                    <th className="border border-nebula-cyan/30 px-3 py-2 text-left">Instrument</th>
                    <th className="border border-nebula-cyan/30 px-3 py-2 text-left">Venue</th>
                    <th className="border border-nebula-cyan/30 px-3 py-2 text-left">Stage</th>
                    <th className="border border-nebula-cyan/30 px-3 py-2 text-right">WinRate</th>
                    <th className="border border-nebula-cyan/30 px-3 py-2 text-right">PnL</th>
                    <th className="border border-nebula-cyan/30 px-3 py-2 text-right">Trades</th>
                    <th className="border border-nebula-cyan/30 px-3 py-2 text-right">Days</th>
                    <th className="border border-nebula-cyan/30 px-3 py-2 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {deployments.map((row) => (
                    <tr key={row.id} className="border-b border-nebula-cyan/20">
                      <td className="border border-nebula-cyan/20 px-3 py-2 font-mono">{row.strategyName}@{row.strategyVersion}</td>
                      <td className="border border-nebula-cyan/20 px-3 py-2">{row.instrument}</td>
                      <td className="border border-nebula-cyan/20 px-3 py-2">{row.venue}</td>
                      <td className="border border-nebula-cyan/20 px-3 py-2">{row.stage}</td>
                      <td className="border border-nebula-cyan/20 px-3 py-2 text-right">{metricFromMeta(row.meta, "winRate")}</td>
                      <td className="border border-nebula-cyan/20 px-3 py-2 text-right">{metricFromMeta(row.meta, "pnl")}</td>
                      <td className="border border-nebula-cyan/20 px-3 py-2 text-right">{metricFromMeta(row.meta, "trades")}</td>
                      <td className="border border-nebula-cyan/20 px-3 py-2 text-right">{metricFromMeta(row.meta, "days")}</td>
                      <td className="border border-nebula-cyan/20 px-3 py-2">
                        <span className="flex flex-wrap gap-1">
                          <button
                            type="button"
                            disabled={actionBusy === row.id || row.stage === "live"}
                            onClick={() => promote(row.id, row.stage, "live")}
                            className="rounded bg-nebula-cyan/20 px-2 py-1 text-xs hover:bg-nebula-cyan/30 disabled:opacity-50"
                          >
                            Promote to Live
                          </button>
                          <button
                            type="button"
                            disabled={actionBusy === row.id || row.stage === "paper"}
                            onClick={() => promote(row.id, row.stage, "paper")}
                            className="rounded bg-nebula-cyan/20 px-2 py-1 text-xs hover:bg-nebula-cyan/30 disabled:opacity-50"
                          >
                            Move to Paper
                          </button>
                          <button
                            type="button"
                            disabled={actionBusy === row.id || row.stage === "backtest"}
                            onClick={() => promote(row.id, row.stage, "backtest")}
                            className="rounded bg-nebula-cyan/20 px-2 py-1 text-xs hover:bg-nebula-cyan/30 disabled:opacity-50"
                          >
                            Move to Backtest
                          </button>
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
