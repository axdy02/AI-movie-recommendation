import { Loader2 } from "lucide-react";

export default function LoadingState({ label = "Loading" }) {
  return (
    <div className="flex min-h-[320px] items-center justify-center text-slate-300">
      <div className="flex items-center gap-3 rounded-lg border border-white/10 bg-white/5 px-5 py-4">
        <Loader2 className="h-5 w-5 animate-spin text-signal" />
        <span>{label}</span>
      </div>
    </div>
  );
}
