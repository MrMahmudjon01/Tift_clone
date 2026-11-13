import DOMPurify from 'dompurify'
import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'

/** CKEditor'dan kelgan HTML — XSS'dan tozalab chiqariladi (CKEditor 4 eskirgan). */
export function Html({ html, className = '' }: { html: string; className?: string }) {
  return <div className={`prose-content ${className}`} dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(html) }} />
}

export const Spinner = () => (
  <div className="flex justify-center py-16" role="status" aria-label="Yuklanmoqda">
    <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-200 border-t-brand-600" />
  </div>
)

export function ErrorBox({ error, children }: { error?: Error | null; children?: ReactNode }) {
  return (
    <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
      {children ?? error?.message ?? "Ma'lumotlarni yuklab bo'lmadi. Keyinroq urinib ko'ring."}
    </div>
  )
}

export const Empty = ({ children }: { children: ReactNode }) => (
  <div className="rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center text-slate-500">{children}</div>
)

export function Badge({ children, tone = 'brand' }: { children: ReactNode; tone?: 'brand' | 'green' | 'red' | 'amber' | 'slate' }) {
  const tones = {
    brand: 'bg-brand-50 text-brand-700 ring-brand-200', green: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
    red: 'bg-red-50 text-red-700 ring-red-200', amber: 'bg-amber-50 text-amber-700 ring-amber-200',
    slate: 'bg-slate-100 text-slate-700 ring-slate-200',
  }
  return <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${tones[tone]}`}>{children}</span>
}

export function PageHeader({ title, subtitle, crumbs }: { title: string; subtitle?: string; crumbs?: { to: string; label: string }[] }) {
  return (
    <div className="bg-gradient-to-br from-brand-900 to-brand-700 text-white">
      <div className="container-page py-12">
        {crumbs && (
          <nav className="mb-3 flex gap-2 text-sm text-brand-200" aria-label="breadcrumb">
            {crumbs.map((c) => (
              <span key={c.to} className="flex gap-2"><Link className="hover:text-white" to={c.to}>{c.label}</Link><span>/</span></span>
            ))}
          </nav>
        )}
        <h1 className="text-3xl font-bold tracking-tight md:text-4xl">{title}</h1>
        {subtitle && <p className="mt-2 max-w-2xl text-brand-100">{subtitle}</p>}
      </div>
    </div>
  )
}

export function Field({ label, error, children, hint }: { label: string; error?: string; hint?: string; children: ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-slate-700">{label}</span>
      {children}
      {error ? <span className="mt-1 block text-xs text-red-600">{error}</span>
        : hint && <span className="mt-1 block text-xs text-slate-500">{hint}</span>}
    </label>
  )
}
