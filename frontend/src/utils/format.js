export const riskTone=(level='LOW')=>({LOW:'text-emerald-300 border-emerald-400/30 bg-emerald-400/10',MEDIUM:'text-amber-300 border-amber-400/30 bg-amber-400/10',HIGH:'text-orange-300 border-orange-400/30 bg-orange-400/10',CRITICAL:'text-red-300 border-red-400/30 bg-red-400/10'}[level]||'text-cyan-300 border-cyan-400/30 bg-cyan-400/10')
export const pct=(v)=>`${Math.round(Number(v)||0)}%`
export const time=(v)=>v?new Date(v).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit',second:'2-digit'}):'—'
export const dateTime=(v)=>v?new Date(v).toLocaleString(): '—'
export const titleCase=(s='')=>s.toLowerCase().split('_').map(x=>x.charAt(0).toUpperCase()+x.slice(1)).join(' ')
