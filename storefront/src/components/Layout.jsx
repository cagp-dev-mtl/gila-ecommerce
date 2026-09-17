import { NavLink } from 'react-router-dom'

import { useCart } from '../context/CartContext'
import Footer from './Footer'

function Layout({ children }) {
  const { count } = useCart()

  return (
    <div className="app">
      <header className="app-header">
        <NavLink to="/" className="brand">
          Gila Commerce
        </NavLink>
        <nav className="app-nav">
          <NavLink
            to="/"
            end
            className={({ isActive }) => `nav-link${isActive ? ' nav-link--active' : ''}`}
          >
            Catalog
          </NavLink>
          <NavLink
            to="/cart"
            className={({ isActive }) => `nav-cart${isActive ? ' nav-cart--active' : ''}`}
          >
            Cart
            {count > 0 && <span className="cart-badge">{count}</span>}
          </NavLink>
          <NavLink
            to="/admin"
            className={({ isActive }) => `nav-admin${isActive ? ' nav-admin--active' : ''}`}
          >
            Admin
          </NavLink>
        </nav>
      </header>
      <main className="app-main">{children}</main>
      <Footer />
    </div>
  )
}

export default Layout
