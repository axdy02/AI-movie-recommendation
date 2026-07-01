export default function StatCard({ label, value, helper, icon: Icon }) {
  return (
    <div className="rounded-lg border border-white/10 bg-white/[0.04] p-5 shadow-glow">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm text-slate-400">{label}</p>
          <p className="mt-2 text-3xl font-semibold text-white">{value}</p>
        </div>
        {Icon ? (
          <div className="rounded-lg border border-white/10 bg-white/5 p-2 text-signal">
            <Icon className="h-5 w-5" />
          </div>
        ) : null}
      </div>
      {helper ? <p className="mt-3 text-xs text-slate-500">{helper}</p> : null}
    </div>
  );
}
