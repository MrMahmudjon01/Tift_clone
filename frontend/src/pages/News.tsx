import { Link } from 'react-router-dom'
import { api } from '../lib/api'
import { formatDate, useFetch, useTitle } from '../lib/hooks'
import { Empty, ErrorBox, PageHeader, Spinner } from '../components/ui'

export default function News() {
  useTitle('Yangiliklar')
  const { data, error, loading } = useFetch(() => api.news(), [])
  return (
    <>
      <PageHeader title="Yangiliklar" subtitle="E'lonlar, tadbirlar va qabul jarayoniga oid so'nggi xabarlar" />
      <div className="container-page py-10">
        {loading ? <Spinner /> : error ? <ErrorBox error={error} /> : data!.results.length === 0 ? (
          <Empty>Hozircha yangiliklar yo'q.</Empty>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {data!.results.map((n) => (
              <Link key={n.slug} to={`/yangiliklar/${n.slug}`} className="card-hover flex flex-col p-6">
                <time dateTime={n.publish_time} className="text-xs font-medium uppercase tracking-wide text-brand-600">{formatDate(n.publish_time)}</time>
                <h2 className="mt-2 flex-1 text-lg font-semibold text-slate-900">{n.title}</h2>
                <span className="mt-4 text-sm font-medium text-brand-700">O'qish →</span>
              </Link>
            ))}
          </div>
        )}
      </div>
    </>
  )
}
