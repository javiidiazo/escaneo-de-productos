import { Outlet } from 'react-router-dom'

import './styles/app.css'

function App () {
  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Escáner de Productos</h1>
        <p>Escaneá el código y descubrí la info al instante.</p>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  )
}

export default App
