import { Link, useParams } from 'react-router-dom'
import { api, ApiError } from '../lib/api'
import { useFetch, useTitle } from '../lib/hooks'
import { Badge, ErrorBox, Html, PageHeader, Spinner } from '../components/ui'
import NotFound from './NotFound'

export default function FacultyDetail() {
  const { id = '' } = useParams()
  const { data, error, loading } = useFetch(() => api.faculty(id), [id])
  useTitle(data?.title)

  if (error instanceof ApiError && error.status === 404) return <NotFound />
  return (
    <>
      <PageHeader title={data?.title ?? 'Fakultet'} subtitle={data?.degree}
        crumbs={[{ to: '/', label: 'Bosh sahifa' }, { to: '/fakultetlar', label: 'Fakultetlar' }]} />
      <div className="container-page py-10">
        {loading ? <Spinner /> : error ? <ErrorBox error={error} /> : (
          <div className="grid gap-8 lg:grid-cols-3">
            <div className="space-y-8 lg:col-span-2">
              <article className="card p-6 md:p-8"><Html html={data!.body} /></article>
              <section>
                <h2 className="mb-4 text-xl font-bold text-slate-900">Yo'nalishlar ({data!.directions.length})</h2>
                <div className="space-y-4">
                  {data!.directions.map((d) => (
                    <details key={d.id} className="card group p-5 open:ring-1 open:ring-brand-200">
                      <summary className="flex cursor-pointer list-none flex-wrap items-center justify-between gap-3">
                        <span className="font-semibold text-slate-900">{d.title}</span>
                        <span className="flex gap-2"><Badge tone="slate">{d.education_type}</Badge><Badge>{d.language}</Badge></span>
                      </summary>
                      <Html html={d.body} className="mt-4 border-t border-slate-100 pt-4 text-sm" />
                    </details>
                  ))}
                  {data!.directions.length === 0 && <p className="text-slate-500">Yo'nalishlar hali qo'shilmagan.</p>}
                </div>
              </section>
            </div>
            <aside className="space-y-6">
              {data!.director && (
                <div className="card overflow-hidden">
                  {data!.director.picture && (
                    <img src={data!.director.picture} alt={data!.director.full_name} className="aspect-[4/3] w-full object-cover"
                      onError={(e) => { e.currentTarget.style.display = 'none' }} />
                  )}
                  <div className="p-5">
                    <p className="text-xs font-medium uppercase tracking-wide text-brand-600">Fakultet dekani</p>
                    <h3 className="mt-1 font-semibold text-slate-900">{data!.director.full_name}</h3>
                    {data!.director.phone_number && (
                      <a href={`tel:${data!.director.phone_number}`} className="mt-1 block text-sm text-slate-500 hover:text-brand-700">{data!.director.phone_number}</a>
                    )}
                    <Html html={data!.director.bio} className="mt-3 text-sm" />
                  </div>
                </div>
              )}
              <div className="card bg-brand-50 p-6 ring-1 ring-brand-100">
                <h3 className="font-semibold text-slate-900">Shu fakultetga kirmoqchimisiz?</h3>
                <p className="mt-1 text-sm text-slate-600">Arizani onlayn topshiring — bir necha daqiqa oladi.</p>
                <Link to={`/ariza?fakultet=${data!.id}`} className="btn-primary mt-4 w-full">Ariza topshirish</Link>
              </div>
            </aside>
          </div>
        )}
      </div>
    </>
  )
}
