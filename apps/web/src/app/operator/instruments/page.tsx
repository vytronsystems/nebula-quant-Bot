import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function InstrumentsControlPage() {
  return (
    <div>
      <Card>
        <CardHeader><CardTitle>Instruments Control</CardTitle></CardHeader>
        <CardContent>
          <p className="text-sm text-gray-400">Contract: docs/contracts/instrument_control_ui.md. Placeholder until GET /api/instruments wired.</p>
        </CardContent>
      </Card>
    </div>
  );
}
