export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <h1 className="text-3xl font-bold text-nebula-cyan">NEBULA-QUANT</h1>
      <p className="mt-2 text-nebula-violet">Institutional futuristic quant cockpit</p>
      <nav className="mt-8 flex gap-4">
        <a href="/operator" className="rounded bg-nebula-cyan/20 px-4 py-2 text-nebula-cyan hover:bg-nebula-cyan/30">
          Operator
        </a>
        <a href="/executive" className="rounded bg-nebula-violet/20 px-4 py-2 text-nebula-violet hover:bg-nebula-violet/30">
          Executive
        </a>
      </nav>
    </main>
  );
}
