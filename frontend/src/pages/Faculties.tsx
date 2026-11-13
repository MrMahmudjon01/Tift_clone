import { Link, useSearchParams } from 'react-router-dom'
import { api } from '../lib/api'
import { useFetch, useTitle } from '../lib/hooks'
import { Badge, Empty, ErrorBox, PageHeader, Spinner } from '../components/ui'

const TABS = [
  { value: '', label: 'Barchasi' },
  { value: 'bachelors', label: 'Bakalavr' },
  { value: 'master', label: 'Magistratura' },
]

export default function Faculties() {
  useTitle('Fakultetlar')
  const [params, setParams] = useSearchParams()
  const degree = params.get('daraja') ?? ''
  const { data, error, loading } = useFetch(() => api.faculties(degree), [degree])

  return (
    <>
      <PageHeader title="Fakultetlar" subtitle="O'zingizga mos fakultet va yo'nalishni tanlang" />
      <div className="container-page py-10">
        <div className="mb-6 inline-flex rounded-xl bg-white p-1 shadow-sm ring-1 ring-slate-200" role="tablist">
          {TABS.map((t) => (
            <button key={t.value} role="tab" aria-selected={degree === t.value}
              onClick={() => setParams(t.value ? { daraja: t.value } : {})}
              className={`rounded-lg px-4 py-2 text-sm font-medium transition ${degree === t.value ? 'bg-brand-600 text-white' : 'text-slate-600 hover:text-slate-900'}`}>
              {t.label}
            </button>
          ))}
        </div>
        {loading ? <Spinner /> : error ? <ErrorBox error={error} /> : data!.results.length === 0 ? (
          <Empty>Bu bo'limda fakultetlar yo'q.</Empty>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {data!.results.map((f) => (
              <Link key={f.id} to={`/fakultetlar/${f.id}`} className="card-hover flex flex-col p-6">
                <Badge>{f.degree_display}</Badge>
                <h2 className="mt-3 text-lg font-semibold text-slate-900">{f.title}</h2>
                <p className="mt-1 flex-1 text-sm text-slate-500">{f.directions_count} ta yo'nalish</p>
                <span className="mt-4 text-sm font-medium text-brand-700">Batafsil →</span>
              </Link>
            ))}
          </div>
        )}
      </div>
    </>
  )
}
