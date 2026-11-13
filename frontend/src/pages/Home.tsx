import { Link } from 'react-router-dom'
import { api } from '../lib/api'
import { formatDate, SITE, useFetch, useTitle } from '../lib/hooks'
import { Badge, ErrorBox, Spinner } from '../components/ui'

const STEPS = [
  { n: 1, title: "Ro'yxatdan o'ting", text: 'Foydalanuvchi nomi va parol bilan hisob yarating.' },
  { n: 2, title: "Arizani to'ldiring", text: "Pasport ma'lumotlari, yo'nalish va hududingizni kiriting." },
  { n: 3, title: 'Natijani kuting', text: "Holatni kabinetda kuzating, qabul qilinsa shartnomani yuklab oling." },
]

export default function Home() {
  useTitle()
  const faculties = useFetch(() => api.faculties(), [])
  const news = useFetch(() => api.news(3), [])
  const directions = faculties.data?.results.reduce((s, f) => s + f.directions_count, 0) ?? 0

  return (
    <>
      <section className="relative overflow-hidden bg-gradient-to-br from-brand-950 via-brand-900 to-brand-700 text-white">
        <div className="absolute -right-24 -top-24 h-96 w-96 rounded-full bg-brand-500/30 blur-3xl" aria-hidden />
        <div className="container-page relative grid gap-10 py-20 md:grid-cols-2 md:py-28">
          <div>
            <Badge tone="amber">Qabul ochiq</Badge>
            <h1 className="mt-4 text-4xl font-extrabold leading-tight tracking-tight md:text-5xl">{SITE.tagline}</h1>
            <p className="mt-4 max-w-xl text-lg text-brand-100">
              Fakultet va yo'nalishlar bilan tanishing, so'nggi yangiliklarni o'qing va qabul arizasini bir necha daqiqada onlayn topshiring.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/ariza" className="btn-primary bg-accent-500 px-6 py-3 text-base text-slate-900 hover:bg-accent-400">Ariza topshirish</Link>
              <Link to="/fakultetlar" className="btn-secondary bg-white/10 px-6 py-3 text-base text-white ring-white/30 hover:bg-white/20">Fakultetlar</Link>
              {SITE.telegramBot && (
                <a href={`https://t.me/${SITE.telegramBot}`} target="_blank" rel="noopener noreferrer"
                  className="btn-ghost px-4 py-3 text-base text-brand-100 hover:bg-white/10 hover:text-white">Telegram bot orqali →</a>
              )}
            </div>
          </div>
          <dl className="grid grid-cols-2 gap-4 self-center">
            {[
              { label: 'Fakultet', value: faculties.data?.count },
              { label: "Yo'nalish", value: faculties.data ? directions : undefined },
              { label: "Ta'lim shakli", value: 3 },
              { label: "O'qitish tili", value: 3 },
            ].map((s) => (
              <div key={s.label} className="rounded-2xl bg-white/10 p-6 ring-1 ring-white/15 backdrop-blur">
                <dt className="text-sm text-brand-200">{s.label}</dt>
                <dd className="mt-1 text-3xl font-bold">{s.value ?? '—'}</dd>
              </div>
            ))}
          </dl>
        </div>
      </section>

      <section className="container-page py-16">
        <div className="flex items-end justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">Fakultetlar</h2>
            <p className="mt-1 text-slate-500">Bakalavriat va magistratura dasturlari</p>
          </div>
          <Link to="/fakultetlar" className="btn-ghost text-brand-700">Barchasi →</Link>
        </div>
        <div className="mt-6">
          {faculties.loading ? <Spinner /> : faculties.error ? <ErrorBox error={faculties.error} /> : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {faculties.data!.results.slice(0, 6).map((f) => (
                <Link key={f.id} to={`/fakultetlar/${f.id}`} className="card-hover p-6">
                  <Badge>{f.degree_display}</Badge>
                  <h3 className="mt-3 text-lg font-semibold text-slate-900">{f.title}</h3>
                  <p className="mt-1 text-sm text-slate-500">{f.directions_count} ta yo'nalish</p>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>

      <section className="bg-white py-16">
        <div className="container-page">
          <h2 className="text-center text-2xl font-bold text-slate-900">Qabul qanday o'tadi</h2>
          <div className="mt-10 grid gap-6 md:grid-cols-3">
            {STEPS.map((s) => (
              <div key={s.n} className="text-center">
                <div className="mx-auto grid h-12 w-12 place-items-center rounded-full bg-brand-600 text-lg font-bold text-white">{s.n}</div>
                <h3 className="mt-4 font-semibold text-slate-900">{s.title}</h3>
                <p className="mt-1 text-sm text-slate-500">{s.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="container-page py-16">
        <div className="flex items-end justify-between gap-4">
          <h2 className="text-2xl font-bold text-slate-900">So'nggi yangiliklar</h2>
          <Link to="/yangiliklar" className="btn-ghost text-brand-700">Barchasi →</Link>
        </div>
        <div className="mt-6">
          {news.loading ? <Spinner /> : news.error ? <ErrorBox error={news.error} /> : news.data!.results.length === 0 ? (
            <p className="text-slate-500">Hozircha yangiliklar yo'q.</p>
          ) : (
            <div className="grid gap-4 md:grid-cols-3">
              {news.data!.results.map((n) => (
                <Link key={n.slug} to={`/yangiliklar/${n.slug}`} className="card-hover p-6">
                  <time className="text-xs font-medium uppercase tracking-wide text-brand-600">{formatDate(n.publish_time)}</time>
                  <h3 className="mt-2 font-semibold text-slate-900">{n.title}</h3>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>
    </>
  )
}
