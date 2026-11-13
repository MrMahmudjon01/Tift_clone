import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import Layout from './components/Layout'
import { AuthProvider } from './lib/auth'
import Apply from './pages/Apply'
import Cabinet from './pages/Cabinet'
import Faculties from './pages/Faculties'
import FacultyDetail from './pages/FacultyDetail'
import Home from './pages/Home'
import News from './pages/News'
import NewsDetail from './pages/NewsDetail'
import NotFound from './pages/NotFound'
import './index.css'

const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      { path: '/', element: <Home /> },
      { path: '/fakultetlar', element: <Faculties /> },
      { path: '/fakultetlar/:id', element: <FacultyDetail /> },
      { path: '/yangiliklar', element: <News /> },
      { path: '/yangiliklar/:slug', element: <NewsDetail /> },
      { path: '/ariza', element: <Apply /> },
      { path: '/kabinet', element: <Cabinet /> },
      { path: '*', element: <NotFound /> },
    ],
  },
])

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  </StrictMode>,
)
