import { useEffect, useState } from 'react'
import { Link, NavLink, Outlet, ScrollRestoration, useLocation } from 'react-router-dom'
import { api, type Social } from '../lib/api'
import { useAuth } from '../lib/auth'
import { SITE } from '../lib/hooks'

const NAV = [
  { to: '/', label: 'Bosh sahifa', end: true },
  { to: '/fakultetlar', label: 'Fakultetlar' },
  { to: '/yangiliklar', label: 'Yangiliklar' },
]

function Logo() {
  return (
    <Link to="/" className="flex items-center gap-2 font-bold text-slate-900">
      <span className="grid h-9 w-9 place-items-center rounded-lg bg-brand-600 text-lg text-white">T</span>
      <span className="text-lg">{SITE.name}</span>
    </Link>
  )
}

function Header() {
  const { user, logout } = useAuth()
  const [open, setOpen] = useState(false)
  const { pathname } = useLocation()
  useEffect(() => setOpen(false), [pathname])

  const link = ({ isActive }: { isActive: boolean }) =>
    `rounded-lg px-3 py-2 text-sm font-medium transition ${isActive ? 'bg-brand-50 text-brand-700' : 'text-slate-600 hover:text-slate-900'}`

  return (
    <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/90 backdrop-blur">
      <div className="container-page flex h-16 items-center justify-between gap-4">
        <Logo />
        <nav className="hidden items-center gap-1 md:flex">
          {NAV.map((n) => <NavLink key={n.to} to={n.to} end={n.end} className={link}>{n.label}</NavLink>)}
        </nav>
        <div className="hidden items-center gap-2 md:flex">
          {user ? (
            <>
              <NavLink to="/kabinet" className={link}>Kabinet</NavLink>
              <button onClick={logout} className="btn-ghost">Chiqish</button>
            </>
          ) : <Link to="/ariza" className="btn-primary">Ariza topshirish</Link>}
        </div>
        <button className="rounded-lg p-2 md:hidden" onClick={() => setOpen(!open)} aria-label="Menyu" aria-expanded={open}>
          <svg className="h-6 w-6" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
            <path strokeLinecap="round" d={open ? 'M6 6l12 12M6 18L18 6' : 'M4 7h16M4 12h16M4 17h16'} />
          </svg>
        </button>
      </div>
      {open && (
        <nav className="container-page flex flex-col gap-1 border-t border-slate-100 py-3 md:hidden">
          {NAV.map((n) => <NavLink key={n.to} to={n.to} end={n.end} className={link}>{n.label}</NavLink>)}
          {user ? (
            <>
              <NavLink to="/kabinet" className={link}>Kabinet</NavLink>
              <button onClick={logout} className="btn-ghost justify-start">Chiqish</button>
            </>
          ) : <Link to="/ariza" className="btn-primary mt-2">Ariza topshirish</Link>}
        </nav>
      )}
    </header>
  )
}

const SOCIAL_ICON: Record<string, string> = { telegram: '✈', instagram: '◎', facebook: 'f', youtube: '▶' }

function Footer() {
  const [socials, setSocials] = useState<Social[]>([])
  useEffect(() => { api.socials().then((p) => setSocials(p.results)).catch(() => {}) }, [])
  return (
    <footer className="mt-20 bg-slate-900 text-slate-300">
      <div className="container-page grid gap-10 py-12 md:grid-cols-3">
        <div>
          <div className="flex items-center gap-2 font-bold text-white">
            <span className="grid h-9 w-9 place-items-center rounded-lg bg-brand-600">T</span>{SITE.name}
          </div>
          <p className="mt-3 text-sm text-slate-400">{SITE.tagline}. Onlayn qabul, fakultetlar va so'nggi yangiliklar bir joyda.</p>
        </div>
        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wide text-white">Bo'limlar</h3>
          <ul className="mt-3 space-y-2 text-sm">
            {[...NAV, { to: '/ariza', label: 'Ariza topshirish' }].map((n) => <li key={n.to}><Link className="hover:text-white" to={n.to}>{n.label}</Link></li>)}
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wide text-white">Ijtimoiy tarmoqlar</h3>
          <div className="mt-3 flex flex-wrap gap-2">
            {socials.length ? socials.map((s) => (
              <a key={s.id} href={s.link} target="_blank" rel="noopener noreferrer"
                className="flex items-center gap-2 rounded-lg bg-slate-800 px-3 py-2 text-sm hover:bg-slate-700">
                <span aria-hidden>{SOCIAL_ICON[s.social] ?? '•'}</span>{s.title}
              </a>
            )) : <span className="text-sm text-slate-500">Hozircha qo'shilmagan</span>}
          </div>
        </div>
      </div>
      <div className="border-t border-slate-800 py-4 text-center text-xs text-slate-500">
        © {new Date().getFullYear()} {SITE.name} · O'quv loyihasi (demo)
      </div>
    </footer>
  )
}

export default function Layout() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1"><Outlet /></main>
      <Footer />
      <ScrollRestoration />
    </div>
  )
}
