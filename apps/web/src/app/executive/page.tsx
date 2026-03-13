import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";

export default function ExecutivePage() {
  return (
    <div className="space-y-6">
      <p className="text-gray-400">Executive mode — layout shell. Widgets to be wired when backend ready.</p>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Link href="/executive/pnl"><Card className="hover:border-nebula-violet/50"><CardHeader><CardTitle>PnL Overview</CardTitle></CardHeader><CardContent>High-level PnL</CardContent></Card></Link>
        <Link href="/executive/venues"><Card className="hover:border-nebula-violet/50"><CardHeader><CardTitle>Venue Summaries</CardTitle></CardHeader><CardContent>By venue</CardContent></Card></Link>
        <Link href="/executive/targets"><Card className="hover:border-nebula-violet/50"><CardHeader><CardTitle>Weekly Targets</CardTitle></CardHeader><CardContent>Target tracking</CardContent></Card></Link>
        <Link href="/executive/strategies"><Card className="hover:border-nebula-violet/50"><CardHeader><CardTitle>Strategy Health</CardTitle></CardHeader><CardContent>Health cards</CardContent></Card></Link>
        <Link href="/executive/capital"><Card className="hover:border-nebula-violet/50"><CardHeader><CardTitle>Capital Allocation</CardTitle></CardHeader><CardContent>Per-venue capital</CardContent></Card></Link>
        <Link href="/executive/incidents"><Card className="hover:border-nebula-violet/50"><CardHeader><CardTitle>Incidents</CardTitle></CardHeader><CardContent>Incident summary</CardContent></Card></Link>
      </div>
    </div>
  );
}
