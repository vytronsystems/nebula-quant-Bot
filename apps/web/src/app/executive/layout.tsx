import { LanguageProvider } from "@/contexts/language-context";
import { NavButtons } from "@/components/nav-buttons";

export default function ExecutiveLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <LanguageProvider>
      <div className="min-h-screen border-l-4 border-nebula-violet">
        <header className="border-b border-nebula-violet/30 px-4 py-2 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
          <div>
            <h1 className="text-xl font-semibold text-nebula-violet">Executive Dashboard</h1>
            <p className="text-sm text-gray-400">NEBULA-QUANT</p>
          </div>
          <NavButtons forwardHref="/executive" forwardLabel="Adelante" accent="violet" />
        </header>
        <main className="p-4">{children}</main>
      </div>
    </LanguageProvider>
  );
}
