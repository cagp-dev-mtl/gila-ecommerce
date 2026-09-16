import { Link } from 'react-router-dom'

import { useCart } from '../context/CartContext'

function Layout({ children }) {
  const { count } = useCart()

  return (
    <div className="app">
      <header className="app-header">
        <Link to="/" className="brand">
          Gila Commerce
        </Link>
        <nav className="app-nav">
          <Link to="/">Catalog</Link>
          <Link to="/import">Import</Link>
          <Link to="/cart" className="button">
            Cart{count > 0 && <span className="cart-badge">{count}</span>}
          </Link>
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
