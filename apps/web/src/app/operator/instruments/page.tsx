"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useEffect, useState } from "react";

type InstrumentRecord = {
  id?: string;
  venue: string;
  symbol: string;
  assetType: string;
  active: boolean;
  createdAt: string | null;
  updatedAt: string | null;
  meta?: Record<string, unknown> | null;
};

const CONTROL_PLANE_URL = process.env.NEXT_PUBLIC_CONTROL_PLANE_URL || "http://localhost:8081";

export default function InstrumentsControlPage() {
  const [instruments, setInstruments] = useState<InstrumentRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [addVenue, setAddVenue] = useState("");
  const [addSymbol, setAddSymbol] = useState("");
  const [addBusy, setAddBusy] = useState(false);
  const [toggleBusy, setToggleBusy] = useState<string | null>(null);

  async function refetch() {
    try {
      const res = await fetch(`${CONTROL_PLANE_URL}/api/instruments?activeOnly=false`);
      if (res.ok) {
        const data = await res.json();
        setInstruments(Array.isArray(data) ? data : []);
      }
    } catch (_) {}
  }

  async function addInstrument() {
    if (!addVenue.trim() || !addSymbol.trim()) return;
    setAddBusy(true);
    try {
      const res = await fetch(`${CONTROL_PLANE_URL}/api/instruments`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ venue: addVenue.trim(), symbol: addSymbol.trim(), assetType: "spot", active: true }),
      });
      if (res.ok) {
        setAddVenue("");
        setAddSymbol("");
        await refetch();
      }
    } finally {
      setAddBusy(false);
    }
  }

  async function toggleActive(id: string, active: boolean) {
    setToggleBusy(id);
    try {
      const res = await fetch(`${CONTROL_PLANE_URL}/api/instruments/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ active }),
      });
      if (res.ok) await refetch();
    } finally {
      setToggleBusy(null);
    }
  }

  useEffect(() => {
    let cancelled = false;
    async function fetchInstruments() {
      try {
        const res = await fetch(`${CONTROL_PLANE_URL}/api/instruments?activeOnly=false`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (!cancelled) setInstruments(Array.isArray(data) ? data : []);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load instruments");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    fetchInstruments();
    return () => { cancelled = true; };
  }, []);

  function instrumentId(row: InstrumentRecord): string {
    return (row as { id?: string }).id ?? `${row.venue}-${row.symbol}`;
  }

  if (loading) {
    return (
      <div>
        <Card>
          <CardHeader><CardTitle>Instruments Control</CardTitle></CardHeader>
          <CardContent><p className="text-sm text-gray-400">Loading instruments…</p></CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <Card>
          <CardHeader><CardTitle>Instruments Control</CardTitle></CardHeader>
          <CardContent>
            <p className="text-sm text-nebula-red">Error: {error}</p>
            <p className="mt-2 text-xs text-gray-400">Ensure the control plane is running (e.g. port 8081) and CORS allows this origin.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader><CardTitle>Instruments Control</CardTitle></CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2 mb-4">
            <input
              type="text"
              placeholder="Venue"
              value={addVenue}
              onChange={(e) => setAddVenue(e.target.value)}
              className="rounded border border-nebula-cyan/30 bg-background px-2 py-1 text-sm w-24"
            />
            <input
              type="text"
              placeholder="Symbol"
              value={addSymbol}
              onChange={(e) => setAddSymbol(e.target.value)}
              className="rounded border border-nebula-cyan/30 bg-background px-2 py-1 text-sm w-28"
            />
            <button
              type="button"
              disabled={addBusy || !addVenue.trim() || !addSymbol.trim()}
              onClick={addInstrument}
              className="rounded bg-nebula-cyan/20 px-3 py-1 text-sm hover:bg-nebula-cyan/30 disabled:opacity-50"
            >
              Add instrument
            </button>
          </div>
          {instruments.length === 0 ? (
            <p className="text-sm text-gray-400">No instruments in the registry. Add them above or via the API.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm border-collapse border border-nebula-cyan/30">
                <thead>
                  <tr className="bg-nebula-cyan/10">
                    <th className="border border-nebula-cyan/30 px-3 py-2 text-left">Venue</th>
                    <th className="border border-nebula-cyan/30 px-3 py-2 text-left">Symbol</th>
                    <th className="border border-nebula-cyan/30 px-3 py-2 text-left">Asset type</th>
                    <th className="border border-nebula-cyan/30 px-3 py-2 text-left">Active</th>
                    <th className="border border-nebula-cyan/30 px-3 py-2 text-left">Updated</th>
                    <th className="border border-nebula-cyan/30 px-3 py-2 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {instruments.map((row, i) => (
                    <tr key={instrumentId(row)} className="border-b border-nebula-cyan/20">
                      <td className="border border-nebula-cyan/20 px-3 py-2">{row.venue}</td>
                      <td className="border border-nebula-cyan/20 px-3 py-2 font-mono">{row.symbol}</td>
                      <td className="border border-nebula-cyan/20 px-3 py-2">{row.assetType}</td>
                      <td className="border border-nebula-cyan/20 px-3 py-2">{row.active ? "Yes" : "No"}</td>
                      <td className="border border-nebula-cyan/20 px-3 py-2 text-gray-400">{row.updatedAt ?? "—"}</td>
                      <td className="border border-nebula-cyan/20 px-3 py-2">
                        {row.id && (
                          <button
                            type="button"
                            disabled={toggleBusy === row.id}
                            onClick={() => toggleActive(row.id!, !row.active)}
                            className="rounded bg-nebula-cyan/20 px-2 py-1 text-xs hover:bg-nebula-cyan/30 disabled:opacity-50"
                          >
                            {row.active ? "Deactivate" : "Activate"}
                          </button>
                        )}
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
