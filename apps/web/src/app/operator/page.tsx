import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";

export default function OperatorPage() {
  return (
    <div className="space-y-6">
      <p className="text-gray-400">Operator mode — layout shell. Screens to be wired in Phase 68.</p>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Link href="/operator/venues"><Card className="hover:border-nebula-cyan/50"><CardHeader><CardTitle>Venues Overview</CardTitle></CardHeader><CardContent>Binance, TradeStation</CardContent></Card></Link>
        <Link href="/operator/instruments"><Card className="hover:border-nebula-cyan/50"><CardHeader><CardTitle>Instruments Control</CardTitle></CardHeader><CardContent>Add / activate pairs</CardContent></Card></Link>
        <Link href="/operator/strategies"><Card className="hover:border-nebula-cyan/50"><CardHeader><CardTitle>Strategies Registry</CardTitle></CardHeader><CardContent>Lifecycle state</CardContent></Card></Link>
        <Link href="/operator/paper"><Card className="hover:border-nebula-cyan/50"><CardHeader><CardTitle>Paper Trading Monitor</CardTitle></CardHeader><CardContent>Paper sessions</CardContent></Card></Link>
        <Link href="/operator/live"><Card className="hover:border-nebula-cyan/50"><CardHeader><CardTitle>Live Trading Control</CardTitle></CardHeader><CardContent>Enable / kill switch</CardContent></Card></Link>
        <Link href="/operator/orders"><Card className="hover:border-nebula-cyan/50"><CardHeader><CardTitle>Orders &amp; Positions</CardTitle></CardHeader><CardContent>Reconciliation view</CardContent></Card></Link>
        <Link href="/operator/risk"><Card className="hover:border-nebula-cyan/50"><CardHeader><CardTitle>Risk Center</CardTitle></CardHeader><CardContent>Limits / guardrails</CardContent></Card></Link>
        <Link href="/operator/audit"><Card className="hover:border-nebula-cyan/50"><CardHeader><CardTitle>Audit &amp; Evidence Center</CardTitle></CardHeader><CardContent>Phase logs / artifacts</CardContent></Card></Link>
      </div>
    </div>
  );
}
