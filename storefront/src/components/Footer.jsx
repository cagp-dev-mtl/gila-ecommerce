import { Link } from 'react-router-dom'

function Footer() {
  return (
    <footer className="app-footer">
      <div className="footer-inner">
        <div className="footer-brand">
          <span className="footer-logo">Gila Commerce</span>
          <p>A full-stack e-commerce platform built with FastAPI, React, and PostgreSQL.</p>
        </div>
        <div className="footer-col">
          <h4>Shop</h4>
          <Link to="/">All products</Link>
          <Link to="/cart">Shopping cart</Link>
          <Link to="/import">Import catalog</Link>
        </div>
        <div className="footer-col">
          <h4>Manage</h4>
          <Link to="/products/new">New product</Link>
          <a href="/api/docs" target="_blank" rel="noreferrer">API docs</a>
        </div>
        <div className="footer-col">
          <h4>Stack</h4>
          <span>FastAPI + SQLAlchemy</span>
          <span>React + Vite</span>
          <span>PostgreSQL 16</span>
          <span>Docker Compose</span>
        </div>
      </div>
      <div className="footer-bottom">
        <span>© 2026 Gila Commerce</span>
      </div>
    </footer>
  )
}

export default Footer
