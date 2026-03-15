"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

type NavButtonsProps = {
  backLabel?: string;
  forwardLabel?: string;
  forwardHref: string;
  accent?: "cyan" | "violet";
};

export function NavButtons({
  backLabel = "Atrás",
  forwardLabel,
  forwardHref,
  accent = "cyan",
}: NavButtonsProps) {
  const router = useRouter();
  const border = accent === "violet" ? "border-nebula-violet/50" : "border-nebula-cyan/50";
  const bg = accent === "violet" ? "bg-nebula-violet/20 hover:bg-nebula-violet/30" : "bg-nebula-cyan/20 hover:bg-nebula-cyan/30";

  return (
    <nav className="flex items-center gap-2 flex-wrap">
      <button
        type="button"
        onClick={() => router.back()}
        className={`rounded border px-3 py-1.5 text-sm ${border} ${bg} transition-colors`}
      >
        ← {backLabel}
      </button>
      <Link
        href={forwardHref}
        className={`rounded border px-3 py-1.5 text-sm ${border} ${bg} transition-colors`}
      >
        {forwardLabel ?? "Adelante"} →
      </Link>
    </nav>
  );
}
