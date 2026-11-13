import { useEffect, useState, type FormEvent } from 'react'
import { Navigate, useNavigate, useSearchParams } from 'react-router-dom'
import { api, ApiError, type ApplicationInput, type Direction, type Region } from '../lib/api'
import { useAuth } from '../lib/auth'
import { useFetch, useTitle } from '../lib/hooks'
import { ErrorBox, Field, PageHeader, Spinner } from '../components/ui'

function AuthForm() {
  const { login, register } = useAuth()
  const [mode, setMode] = useState<'register' | 'login'>('register')
  const [form, setForm] = useState({ username: '', password: '', first_name: '', last_name: '' })
  const [error, setError] = useState<ApiError | null>(null)
  const [busy, setBusy] = useState(false)
  const set = (k: keyof typeof form) => (e: { target: { value: string } }) => setForm({ ...form, [k]: e.target.value })

  async function submit(e: FormEvent) {
    e.preventDefault()
    setBusy(true); setError(null)
    try {
      if (mode === 'register') await register(form)
      else await login(form.username, form.password)
    } catch (err) {
      setError(err instanceof ApiError ? err : new ApiError(0, null))
    } finally { setBusy(false) }
  }

  return (
    <div className="card mx-auto max-w-md p-6 md:p-8">
      <div className="mb-6 grid grid-cols-2 rounded-xl bg-slate-100 p-1">
        {(['register', 'login'] as const).map((m) => (
          <button key={m} type="button" onClick={() => { setMode(m); setError(null) }}
            className={`rounded-lg py-2 text-sm font-medium ${mode === m ? 'bg-white text-slate-900 shadow' : 'text-slate-500'}`}>
            {m === 'register' ? "Ro'yxatdan o'tish" : 'Kirish'}
          </button>
        ))}
      </div>
      <form onSubmit={submit} className="space-y-4" noValidate>
        {mode === 'register' && (
          <div className="grid grid-cols-2 gap-3">
            <Field label="Ism"><input className="input" value={form.first_name} onChange={set('first_name')} autoComplete="given-name" /></Field>
            <Field label="Familiya"><input className="input" value={form.last_name} onChange={set('last_name')} autoComplete="family-name" /></Field>
          </div>
        )}
        <Field label="Foydalanuvchi nomi" error={error?.field('username')}>
          <input className="input" required value={form.username} onChange={set('username')} autoComplete="username"
            aria-invalid={!!error?.field('username')} />
        </Field>
        <Field label="Parol" error={error?.field('password')} hint={mode === 'register' ? 'Kamida 8 belgi, faqat raqamlardan iborat bo\'lmasin' : undefined}>
          <input className="input" type="password" required value={form.password} onChange={set('password')}
            autoComplete={mode === 'register' ? 'new-password' : 'current-password'} aria-invalid={!!error?.field('password')} />
        </Field>
        {error && !error.field('username') && !error.field('password') && (
          <ErrorBox>{error.status === 401 ? "Foydalanuvchi nomi yoki parol noto'g'ri." : error.status === 429 ? "Juda ko'p urinish. Bir daqiqadan so'ng qayta urining." : error.message}</ErrorBox>
        )}
        <button className="btn-primary w-full" disabled={busy}>{busy ? 'Kuting...' : mode === 'register' ? "Ro'yxatdan o'tish" : 'Kirish'}</button>
      </form>
    </div>
  )
}

const EMPTY: ApplicationInput = { first_name: '', last_name: '', passport: '', pinfl: '', gender: '', birth_date: '', direction: '', district: '' }

function ApplicationForm() {
  const navigate = useNavigate()
  const { user, reload } = useAuth()
  const [params] = useSearchParams()
  const faculties = useFetch(() => api.faculties(), [])
  const regions = useFetch(() => api.regions(), [])
  const [facultyId, setFacultyId] = useState(params.get('fakultet') ?? '')
  const [regionId, setRegionId] = useState('')
  const [directions, setDirections] = useState<Direction[]>([])
  const [districts, setDistricts] = useState<Region[]>([])
  const [form, setForm] = useState<ApplicationInput>({ ...EMPTY, first_name: user?.first_name ?? '', last_name: user?.last_name ?? '' })
  const [error, setError] = useState<ApiError | null>(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    setDirections([]); setForm((f) => ({ ...f, direction: '' }))
    if (facultyId) api.faculty(facultyId).then((f) => setDirections(f.directions)).catch(() => {})
  }, [facultyId])
  useEffect(() => {
    setDistricts([]); setForm((f) => ({ ...f, district: '' }))
    if (regionId) api.districts(Number(regionId)).then((p) => setDistricts(p.results)).catch(() => {})
  }, [regionId])

  const set = (k: keyof ApplicationInput, transform = (v: string) => v) =>
    (e: { target: { value: string } }) => setForm({ ...form, [k]: transform(e.target.value) })
  const err = (k: string) => error?.field(k)

  async function submit(e: FormEvent) {
    e.preventDefault()
    setBusy(true); setError(null)
    try {
      await api.submitApplication(form)
      await reload()
      navigate('/kabinet', { state: { submitted: true } })
    } catch (ex) {
      setError(ex instanceof ApiError ? ex : new ApiError(0, null))
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } finally { setBusy(false) }
  }

  if (faculties.loading || regions.loading) return <Spinner />
  if (faculties.error || regions.error) return <ErrorBox error={faculties.error ?? regions.error} />

  return (
    <form onSubmit={submit} className="card mx-auto max-w-3xl space-y-8 p-6 md:p-8" noValidate>
      {error && (
        <ErrorBox>
          {ApiError.describe(error.data) ||
            (error.status === 429 ? "Juda ko'p urinish. Birozdan so'ng qayta urining."
              : error.status === 400 ? 'Formadagi xatolarni tuzating.' : error.message)}
        </ErrorBox>
      )}

      <fieldset className="space-y-4">
        <legend className="text-lg font-semibold text-slate-900">Shaxsiy ma'lumotlar</legend>
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Ism" error={err('first_name')}><input className="input" required value={form.first_name} onChange={set('first_name')} aria-invalid={!!err('first_name')} /></Field>
          <Field label="Familiya" error={err('last_name')}><input className="input" required value={form.last_name} onChange={set('last_name')} aria-invalid={!!err('last_name')} /></Field>
          <Field label="Pasport seriya va raqami" error={err('passport')} hint="Masalan: AA1234567">
            <input className="input uppercase" required maxLength={9} value={form.passport} placeholder="AA1234567"
              onChange={set('passport', (v) => v.toUpperCase().replace(/\s/g, ''))} aria-invalid={!!err('passport')} />
          </Field>
          <Field label="JSHSHIR (PINFL)" error={err('pinfl')} hint="14 ta raqam">
            <input className="input" required inputMode="numeric" maxLength={14} value={form.pinfl}
              onChange={set('pinfl', (v) => v.replace(/\D/g, ''))} aria-invalid={!!err('pinfl')} />
          </Field>
          <Field label="Jinsi" error={err('gender')}>
            <select className="input" required value={form.gender} onChange={set('gender')} aria-invalid={!!err('gender')}>
              <option value="">Tanlang</option><option value="male">Erkak</option><option value="female">Ayol</option>
            </select>
          </Field>
          <Field label="Tug'ilgan sana" error={err('birth_date')}>
            <input className="input" type="date" required value={form.birth_date} onChange={set('birth_date')} aria-invalid={!!err('birth_date')} />
          </Field>
        </div>
      </fieldset>

      <fieldset className="space-y-4">
        <legend className="text-lg font-semibold text-slate-900">Ta'lim yo'nalishi</legend>
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Fakultet">
            <select className="input" value={facultyId} onChange={(e) => setFacultyId(e.target.value)}>
              <option value="">Tanlang</option>
              {faculties.data!.results.map((f) => <option key={f.id} value={f.id}>{f.title} ({f.degree_display})</option>)}
            </select>
          </Field>
          <Field label="Yo'nalish" error={err('direction')}>
            <select className="input" required disabled={!directions.length} value={form.direction}
              onChange={set('direction')} aria-invalid={!!err('direction')}>
              <option value="">{facultyId ? 'Tanlang' : 'Avval fakultetni tanlang'}</option>
              {directions.map((d) => <option key={d.id} value={d.id}>{d.title} — {d.education_type}, {d.language}</option>)}
            </select>
          </Field>
        </div>
      </fieldset>

      <fieldset className="space-y-4">
        <legend className="text-lg font-semibold text-slate-900">Yashash hududi</legend>
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Viloyat">
            <select className="input" value={regionId} onChange={(e) => setRegionId(e.target.value)}>
              <option value="">Tanlang</option>
              {regions.data!.results.map((r) => <option key={r.id} value={r.id}>{r.title}</option>)}
            </select>
          </Field>
          <Field label="Tuman" error={err('district')}>
            <select className="input" required disabled={!districts.length} value={form.district}
              onChange={set('district')} aria-invalid={!!err('district')}>
              <option value="">{regionId ? 'Tanlang' : 'Avval viloyatni tanlang'}</option>
              {districts.map((d) => <option key={d.id} value={d.id}>{d.title}</option>)}
            </select>
          </Field>
        </div>
      </fieldset>

      <p className="text-xs text-slate-500">Arizani yuborish orqali ma'lumotlaringiz qabul jarayoni uchun qayta ishlanishiga rozilik bildirasiz.</p>
      <button className="btn-primary w-full py-3 text-base" disabled={busy}>{busy ? 'Yuborilmoqda...' : 'Arizani yuborish'}</button>
    </form>
  )
}

export default function Apply() {
  useTitle('Ariza topshirish')
  const { user, loading } = useAuth()
  if (user?.has_application) return <Navigate to="/kabinet" replace />
  return (
    <>
      <PageHeader title="Ariza topshirish" subtitle={user ? "Barcha maydonlarni to'ldiring va arizani yuboring" : "Ariza topshirish uchun avval hisob yarating yoki kiring"} />
      <div className="container-page py-10">{loading ? <Spinner /> : user ? <ApplicationForm /> : <AuthForm />}</div>
    </>
  )
}
