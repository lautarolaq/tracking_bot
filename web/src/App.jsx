import { useState } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './hooks/useAuth'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Nutrition from './pages/Nutrition'
import Gym from './pages/Gym'
import Sleep from './pages/Sleep'
import Weight from './pages/Weight'
import Emotions from './pages/Emotions'
import Work from './pages/Work'

export default function App() {
  const [days, setDays] = useState(30)

  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/*" element={
            <Layout days={days} onDaysChange={setDays}>
              <Routes>
                <Route path="/" element={<Dashboard days={days} />} />
                <Route path="/nutrition" element={<Nutrition days={days} />} />
                <Route path="/gym" element={<Gym days={days} />} />
                <Route path="/sleep" element={<Sleep days={days} />} />
                <Route path="/weight" element={<Weight days={days} />} />
                <Route path="/emotions" element={<Emotions days={days} />} />
                <Route path="/work" element={<Work days={days} />} />
              </Routes>
            </Layout>
          } />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
