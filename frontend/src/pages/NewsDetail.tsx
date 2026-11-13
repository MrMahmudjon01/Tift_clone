import { Link, useParams } from 'react-router-dom'
import { api, ApiError } from '../lib/api'
import { formatDate, useFetch, useTitle } from '../lib/hooks'
import { ErrorBox, Html, Spinner } from '../components/ui'
import NotFound from './NotFound'

export default function NewsDetail() {
  const { slug = '' } = useParams()
  const { data, error, loading } = useFetch(() => api.newsItem(slug), [slug])
  useTitle(data?.title)

  if (error instanceof ApiError && error.status === 404) return <NotFound />
  return (
    <div className="container-page max-w-3xl py-10">
      <Link to="/yangiliklar" className="btn-ghost -ml-3 text-brand-700">← Yangiliklar</Link>
      {loading ? <Spinner /> : error ? <ErrorBox error={error} /> : (
        <article className="mt-4">
          <time dateTime={data!.publish_time} className="text-sm font-medium text-brand-600">{formatDate(data!.publish_time)}</time>
          <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900 md:text-4xl">{data!.title}</h1>
          <div className="card mt-8 p-6 md:p-8"><Html html={data!.body} /></div>
        </article>
      )}
    </div>
  )
}
