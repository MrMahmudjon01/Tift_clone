import { Link } from 'react-router-dom'
import { useTitle } from '../lib/hooks'

export default function NotFound() {
  useTitle('Sahifa topilmadi')
  return (
    <div className="container-page py-24 text-center">
      <p className="text-6xl font-extrabold text-brand-600">404</p>
      <h1 className="mt-4 text-2xl font-bold text-slate-900">Sahifa topilmadi</h1>
      <p className="mt-2 text-slate-500">Siz qidirgan sahifa mavjud emas yoki o'chirilgan.</p>
      <Link to="/" className="btn-primary mt-8">Bosh sahifaga qaytish</Link>
    </div>
  )
}
