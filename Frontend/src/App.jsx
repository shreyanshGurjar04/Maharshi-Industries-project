import { Routes, Route } from 'react-router-dom'
import Sidebar from './Components/Sidebar'
import Detection from './Pages/Detection'
import Analytics from './Pages/Analytics'
import Dashboard from './Pages/Dashboard'
import BlackList from './Pages/BlackList'
import WhiteList from './Pages/WhiteList'
import VideoPlay from './Pages/VideoPlay'

function App() {
  return (
    <div className="app">
      <Sidebar />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/detection" element={<Detection />} />
        <Route path="/blacklist" element={<BlackList />} />
        <Route path="/whitelist" element={<WhiteList />} />
        <Route path="/videoplayback" element={<VideoPlay />} />
      </Routes>
    </div>
  )
}

export default App
