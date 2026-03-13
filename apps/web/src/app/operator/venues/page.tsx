import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function VenuesOverviewPage() {
  return (
    <div>
      <Card>
        <CardHeader><CardTitle>Venues Overview</CardTitle></CardHeader>
        <CardContent>
          <p className="text-sm text-gray-400">Backend: dashboard aggregation contract (nq_cross_venue). Placeholder until control plane API wired.</p>
        </CardContent>
      </Card>
    </div>
  );
}
