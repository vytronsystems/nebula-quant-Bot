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

const DEFAULT_VENUES = ["Binance", "TradeStation"];

const ASSET_TYPES = ["spot", "futures", "options", "cfd"];

function assetTypeForVenue(venue: string): string {
  if (venue === "Binance") return "futures";
  if (venue === "TradeStation") return "options";
  return "spot";
}

export default function InstrumentsControlPage() {
  const [instruments, setInstruments] = useState<InstrumentRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [venues, setVenues] = useState<string[]>(DEFAULT_VENUES);
  const [addVenue, setAddVenue] = useState("");
  const [addSymbol, setAddSymbol] = useState("");
  const [addBusy, setAddBusy] = useState(false);
  const [toggleBusy, setToggleBusy] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editSymbol, setEditSymbol] = useState("");
  const [editAssetType, setEditAssetType] = useState("");
  const [editBusy, setEditBusy] = useState(false);
  const [deleteBusy, setDeleteBusy] = useState<string | null>(null);

  useEffect(() => {
    fetch("/venues.json")
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (Array.isArray(data) && data.length > 0) setVenues(data);
      })
      .catch(() => {});
  }, []);

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
        body: JSON.stringify({
          venue: addVenue.trim(),
          symbol: addSymbol.trim(),
          assetType: assetTypeForVenue(addVenue.trim()),
          active: true,
        }),
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

  function startEdit(row: InstrumentRecord) {
    const id = instrumentId(row);
    if (!row.id) return;
    setEditingId(id);
    setEditSymbol(row.symbol);
    setEditAssetType(row.assetType || "spot");
  }

  function cancelEdit() {
    setEditingId(null);
    setEditSymbol("");
    setEditAssetType("");
  }

  async function saveEdit() {
    if (!editingId || !editSymbol.trim()) return;
    setEditBusy(true);
    try {
      const res = await fetch(`${CONTROL_PLANE_URL}/api/instruments/${editingId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol: editSymbol.trim(), assetType: editAssetType || "spot" }),
      });
      if (res.ok) {
        cancelEdit();
        await refetch();
      }
    } finally {
      setEditBusy(false);
    }
  }

  async function deleteInstrument(row: InstrumentRecord) {
    const id = row.id;
    if (!id) return;
    if (!confirm(`¿Eliminar instrumento ${row.venue} / ${row.symbol}?`)) return;
    setDeleteBusy(id);
    try {
      const res = await fetch(`${CONTROL_PLANE_URL}/api/instruments/${id}`, { method: "DELETE" });
      if (res.ok || res.status === 204) {
        if (editingId === id) cancelEdit();
        setInstruments((prev) => prev.filter((instr) => (instr.id ?? instrumentId(instr)) !== id));
        refetch().catch(() => {});
      }
    } finally {
      setDeleteBusy(null);
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
    <div className="min-w-0 w-full max-w-full space-y-4 p-2 sm:p-4">
      <Card className="min-w-0 overflow-hidden">
        <CardHeader className="p-3 sm:p-6">
          <CardTitle className="text-base sm:text-lg">Instruments Control</CardTitle>
        </CardHeader>
        <CardContent className="p-3 sm:p-6 pt-0">
          <div className="flex flex-wrap items-center gap-2 sm:gap-3 mb-4">
            <select
              value={addVenue}
              onChange={(e) => setAddVenue(e.target.value)}
              className="rounded border border-nebula-cyan/30 bg-background px-2 py-1.5 text-sm min-w-0 w-full sm:w-auto sm:min-w-[140px]"
            >
              <option value="">Seleccionar venue</option>
              {venues.map((v) => (
                <option key={v} value={v}>{v}</option>
              ))}
            </select>
            <input
              type="text"
              placeholder="Symbol"
              value={addSymbol}
              onChange={(e) => setAddSymbol(e.target.value)}
              className="rounded border border-nebula-cyan/30 bg-background px-2 py-1.5 text-sm min-w-0 w-full sm:w-28 flex-1 sm:flex-none"
            />
            <button
              type="button"
              disabled={addBusy || !addVenue.trim() || !addSymbol.trim()}
              onClick={addInstrument}
              className="rounded bg-nebula-cyan/20 px-3 py-1.5 text-sm hover:bg-nebula-cyan/30 disabled:opacity-50 shrink-0"
            >
              Añadir instrumento
            </button>
          </div>
          <p className="text-xs text-gray-400 mb-3">Binance: futures. TradeStation: options.</p>
          {instruments.length === 0 ? (
            <p className="text-sm text-gray-400">No hay instrumentos. Añade alguno arriba o vía API.</p>
          ) : (
            <div className="min-w-0 overflow-x-auto -mx-1 sm:mx-0">
              <table className="w-full min-w-[640px] text-sm border-collapse border border-nebula-cyan/30">
                <thead>
                  <tr className="bg-nebula-cyan/10">
                    <th className="border border-nebula-cyan/30 px-2 sm:px-3 py-2 text-left">Venue</th>
                    <th className="border border-nebula-cyan/30 px-2 sm:px-3 py-2 text-left">Symbol</th>
                    <th className="border border-nebula-cyan/30 px-2 sm:px-3 py-2 text-left">Asset type</th>
                    <th className="border border-nebula-cyan/30 px-2 sm:px-3 py-2 text-left">Active</th>
                    <th className="border border-nebula-cyan/30 px-2 sm:px-3 py-2 text-left hidden sm:table-cell">Updated</th>
                    <th className="border border-nebula-cyan/30 px-2 sm:px-3 py-2 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {instruments.map((row) => {
                    const id = instrumentId(row);
                    const isEditing = editingId === id;
                    return (
                      <tr key={id} className="border-b border-nebula-cyan/20">
                        <td className="border border-nebula-cyan/20 px-2 sm:px-3 py-2">{row.venue}</td>
                        {isEditing ? (
                          <>
                            <td className="border border-nebula-cyan/20 px-2 sm:px-3 py-2">
                              <input
                                type="text"
                                value={editSymbol}
                                onChange={(e) => setEditSymbol(e.target.value)}
                                className="rounded border border-nebula-cyan/30 bg-background px-2 py-1 text-sm w-full min-w-0 font-mono"
                              />
                            </td>
                            <td className="border border-nebula-cyan/20 px-2 sm:px-3 py-2">
                              <select
                                value={editAssetType}
                                onChange={(e) => setEditAssetType(e.target.value)}
                                className="rounded border border-nebula-cyan/30 bg-background px-2 py-1 text-sm w-full min-w-0"
                              >
                                {ASSET_TYPES.map((t) => (
                                  <option key={t} value={t}>{t}</option>
                                ))}
                              </select>
                            </td>
                          </>
                        ) : (
                          <>
                            <td className="border border-nebula-cyan/20 px-2 sm:px-3 py-2 font-mono">{row.symbol}</td>
                            <td className="border border-nebula-cyan/20 px-2 sm:px-3 py-2">{row.assetType}</td>
                          </>
                        )}
                        <td className="border border-nebula-cyan/20 px-2 sm:px-3 py-2">{row.active ? "Sí" : "No"}</td>
                        <td className="border border-nebula-cyan/20 px-2 sm:px-3 py-2 text-gray-400 hidden sm:table-cell">{row.updatedAt ?? "—"}</td>
                        <td className="border border-nebula-cyan/20 px-2 sm:px-3 py-2">
                          <div className="flex flex-wrap gap-1">
                            {isEditing ? (
                              <>
                                <button
                                  type="button"
                                  disabled={editBusy}
                                  onClick={saveEdit}
                                  className="rounded bg-nebula-cyan/20 px-2 py-1 text-xs hover:bg-nebula-cyan/30 disabled:opacity-50"
                                >
                                  Guardar
                                </button>
                                <button
                                  type="button"
                                  disabled={editBusy}
                                  onClick={cancelEdit}
                                  className="rounded border border-nebula-cyan/30 px-2 py-1 text-xs hover:bg-nebula-cyan/10 disabled:opacity-50"
                                >
                                  Cancelar
                                </button>
                              </>
                            ) : (
                              <>
                                {row.id && (
                                  <>
                                    <button
                                      type="button"
                                      onClick={() => startEdit(row)}
                                      className="rounded border border-nebula-cyan/30 px-2 py-1 text-xs hover:bg-nebula-cyan/10"
                                    >
                                      Editar
                                    </button>
                                    <button
                                      type="button"
                                      disabled={toggleBusy === row.id}
                                      onClick={() => toggleActive(row.id!, !row.active)}
                                      className="rounded bg-nebula-cyan/20 px-2 py-1 text-xs hover:bg-nebula-cyan/30 disabled:opacity-50"
                                    >
                                      {row.active ? "Desactivar" : "Activar"}
                                    </button>
                                    <button
                                      type="button"
                                      disabled={deleteBusy === row.id}
                                      onClick={() => deleteInstrument(row)}
                                      className="rounded bg-red-500/20 px-2 py-1 text-xs hover:bg-red-500/30 text-red-300 disabled:opacity-50"
                                    >
                                      Borrar
                                    </button>
                                  </>
                                )}
                              </>
                            )}
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
