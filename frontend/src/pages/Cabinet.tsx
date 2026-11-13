import { useState } from 'react'
import { Link, Navigate, useLocation } from 'react-router-dom'
import { api, type MyApplication } from '../lib/api'
import { useAuth } from '../lib/auth'
import { formatDate, useFetch, useTitle } from '../lib/hooks'
import { Badge, ErrorBox, PageHeader, Spinner } from '../components/ui'

const STATUS_TONE = { pending: 'amber', accepted: 'green', rejected: 'red' } as const

function ApplicationCard({ a }: { a: MyApplication }) {
  const [downloading, setDownloading] = useState(false)
  const [error, setError] = useState('')
  const rows: [string, string][] = [
    ['Familiya, ism', `${a.last_name} ${a.first_name}`],
    ['Pasport', a.passport],
    ["Tug'ilgan sana", formatDate(a.birth_date)],
    ['Jinsi', a.gender],
    ['Fakultet', a.direction?.faculty ?? '—'],
    ["Yo'nalish", a.direction?.title ?? '—'],
    ['Tuman', a.district?.title ?? '—'],
    ['Topshirilgan', formatDate(a.created)],
  ]
  async function download() {
    setDownloading(true); setError('')
    try { await api.downloadContract(a.id) } catch { setError("Shartnomani yuklab bo'lmadi.") } finally { setDownloading(false) }
  }
  return (
    <div className="card overflow-hidden">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 p-6">
        <div>
          <p className="text-sm text-slate-500">Ariza № {a.id}</p>
          <h2 className="text-lg font-semibold text-slate-900">{a.direction?.title ?? 'Ariza'}</h2>
        </div>
        <Badge tone={STATUS_TONE[a.status_code]}>{a.status}</Badge>
      </div>
      <dl className="grid gap-x-8 gap-y-3 p-6 sm:grid-cols-2">
        {rows.map(([k, v]) => (
          <div key={k}><dt className="text-xs uppercase tracking-wide text-slate-400">{k}</dt><dd className="font-medium text-slate-800">{v}</dd></div>
        ))}
      </dl>
      <div className="border-t border-slate-100 bg-slate-50 p-6">
        {a.status_code === 'accepted' ? (
          a.has_contract ? (
            <div className="flex flex-wrap items-center gap-3">
              <button onClick={download} disabled={downloading} className="btn-primary">{downloading ? 'Yuklanmoqda...' : 'Shartnomani yuklab olish (PDF)'}</button>
              {error && <span className="text-sm text-red-600">{error}</span>}
            </div>
          ) : <p className="text-sm text-slate-600">Tabriklaymiz! Arizangiz qabul qilindi. Shartnoma tayyorlanmoqda.</p>
        ) : a.status_code === 'rejected' ? (
          <p className="text-sm text-slate-600">Afsuski, arizangiz rad etildi. Savollar bo'lsa, qabul komissiyasiga murojaat qiling.</p>
        ) : (
          <p className="text-sm text-slate-600">Arizangiz qabul komissiyasi tomonidan ko'rib chiqilmoqda. Natija shu sahifada ko'rinadi.</p>
        )}
      </div>
    </div>
  )
}

export default function Cabinet() {
  useTitle('Shaxsiy kabinet')
  const { user, loading } = useAuth()
  const location = useLocation()
  const apps = useFetch(() => (user ? api.myApplications() : Promise.resolve(null)), [user?.id])

  if (!loading && !user) return <Navigate to="/ariza" replace />
  return (
    <>
      <PageHeader title="Shaxsiy kabinet" subtitle={user ? `Xush kelibsiz, ${user.first_name || user.username}` : undefined} />
      <div className="container-page max-w-3xl space-y-6 py-10">
        {(location.state as { submitted?: boolean } | null)?.submitted && (
          <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">✅ Arizangiz muvaffaqiyatli yuborildi!</div>
        )}
        {loading || apps.loading ? <Spinner /> : apps.error ? <ErrorBox error={apps.error} /> : apps.data?.results.length ? (
          apps.data.results.map((a) => <ApplicationCard key={a.id} a={a} />)
        ) : (
          <div className="card p-10 text-center">
            <h2 className="text-lg font-semibold text-slate-900">Sizda hali ariza yo'q</h2>
            <p className="mt-1 text-slate-500">Qabul arizasini bir necha daqiqada topshiring.</p>
            <Link to="/ariza" className="btn-primary mt-6">Ariza topshirish</Link>
          </div>
        )}
      </div>
    </>
  )
}
