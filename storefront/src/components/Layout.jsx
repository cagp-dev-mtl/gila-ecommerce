import { Link } from 'react-router-dom'

function Layout({ children }) {
  return (
    <div className="app">
      <header className="app-header">
        <Link to="/" className="brand">
          Gila Commerce
        </Link>
        <nav className="app-nav">
          <Link to="/">Catalog</Link>
          <Link to="/import">Import</Link>
          <Link to="/products/new" className="button button-primary">
            New product
          </Link>
        </nav>
      </header>
      <main className="app-main">{children}</main>
    </div>
  )
}

export default Layout
