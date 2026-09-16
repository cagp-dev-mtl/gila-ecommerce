import { Link } from 'react-router-dom'

import { useCart } from '../context/CartContext'
import Footer from './Footer'

function Layout({ children }) {
  const { count } = useCart()

  return (
    <div className="app">
      <header className="app-header">
        <Link to="/" className="brand">
          Gila Commerce
        </Link>
        <nav className="app-nav">
          <Link to="/" className="nav-link">
            Catalog
          </Link>
          <Link to="/import" className="nav-link">
            Import
          </Link>
          <Link to="/cart" className="nav-cart">
            Cart
            {count > 0 && <span className="cart-badge">{count}</span>}
          </Link>
          <Link to="/products/new" className="nav-primary">
            New product
          </Link>
        </nav>
      </header>
      <main className="app-main">{children}</main>
      <Footer />
    </div>
  )
}

export default Layout
