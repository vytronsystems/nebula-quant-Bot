import { LanguageProvider } from "@/contexts/language-context";
import { NavButtons } from "@/components/nav-buttons";

export default function OperatorLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <LanguageProvider>
      <div className="min-h-screen border-l-4 border-nebula-cyan">
        <header className="border-b border-nebula-cyan/30 px-4 py-2 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
          <div>
            <h1 className="text-xl font-semibold text-nebula-cyan">Operator Cockpit</h1>
            <p className="text-sm text-gray-400">NEBULA-QUANT</p>
          </div>
          <NavButtons forwardHref="/operator" forwardLabel="Adelante" accent="cyan" />
        </header>
        <main className="p-4">{children}</main>
      </div>
    </LanguageProvider>
  );
}
