import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'

import { deleteProduct, formatError, listCategories, listProducts } from '../api/client'
import PageBanner from '../components/PageBanner'
import { useDebounce } from '../hooks/useDebounce'

const PAGE_SIZE = 20
const EMPTY_PAGE = { items: [], total: 0, page: 1, pages: 0 }

function AdminPage() {
  const location = useLocation()
  const [data, setData] = useState(EMPTY_PAGE)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(() => {
    if (location.state?.saved && location.state?.name) {
      return location.state.saved === 'updated'
        ? `"${location.state.name}" was updated.`
        : `"${location.state.name}" was created.`
    }
    return null
  })
  const debouncedSearch = useDebounce(search, 300)

  useEffect(() => {
    listCategories()
      .then(setCategories)
      .catch(() => setCategories([]))
  }, [])

  useEffect(() => {
    let active = true
    setLoading(true)
    listProducts({ search: debouncedSearch, category, sort: 'name', order: 'asc', page, page_size: PAGE_SIZE })
      .then((result) => {
        if (active) {
          setData(result)
          setError(null)
        }
      })
      .catch((err) => {
        if (active) setError(formatError(err))
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [debouncedSearch, category, page])

  function handleSearchChange(e) {
    setSearch(e.target.value)
    setPage(1)
  }

  function handleCategoryChange(e) {
    setCategory(e.target.value)
    setPage(1)
  }

  async function handleDelete(product) {
    if (!window.confirm(`Delete "${product.name}"?`)) return
    try {
      await deleteProduct(product.id)
      setData((current) => ({
        ...current,
        items: current.items.filter((item) => item.id !== product.id),
        total: current.total - 1,
      }))
    } catch (err) {
      setError(formatError(err))
    }
  }

  return (
    <section>
      <PageBanner title="Admin" crumb="Home / Admin" />

      <div className="admin-toolbar">
        <Link className="button button-primary" to="/products/new">
          New product
        </Link>
        <Link className="button" to="/import">
          Import catalog
        </Link>
        <input
          className={`input search${search ? ' filter-active' : ''}`}
          type="search"
          placeholder="Search by name, SKU or description"
          value={search}
          onChange={handleSearchChange}
          style={{ flex: 1 }}
        />
        <select
          className={`input${category ? ' filter-active' : ''}`}
          value={category}
          onChange={handleCategoryChange}
        >
          <option value="">All categories</option>
          {categories.map((name) => (
            <option key={name} value={name}>{name}</option>
          ))}
        </select>
      </div>

      {success && (
        <p className="alert alert-success">
          {success}
          <button className="alert-dismiss" onClick={() => setSuccess(null)}>✕</button>
        </p>
      )}
      {error && <p className="alert alert-error">{error}</p>}

      {loading && data.items.length === 0 ? (
        <p className="muted">Loading...</p>
      ) : data.items.length === 0 ? (
        <p className="muted">No products found.</p>
      ) : (
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>SKU</th>
                <th>Category</th>
                <th>Price</th>
                <th>Stock</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((product) => (
                <tr key={product.id}>
                  <td>{product.name}</td>
                  <td className="muted">{product.sku}</td>
                  <td>{product.category || <span className="muted">—</span>}</td>
                  <td>${parseFloat(product.price).toFixed(2)}</td>
                  <td>
                    <span className={product.stock === 0 ? 'stock stock-out' : 'stock'}>
                      {product.stock}
                    </span>
                  </td>
                  <td className="admin-actions">
                    <Link className="button button-sm" to={`/products/${product.id}/edit`}>
                      Edit
                    </Link>
                    <button
                      className="button button-sm button-danger"
                      onClick={() => handleDelete(product)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="pagination">
        <button className="button" disabled={page <= 1} onClick={() => setPage((v) => v - 1)}>
          Previous
        </button>
        <span className="muted">
          Page {data.pages === 0 ? 0 : data.page} of {data.pages} ({data.total} products)
        </span>
        <button
          className="button"
          disabled={page >= data.pages}
          onClick={() => setPage((v) => v + 1)}
        >
          Next
        </button>
      </div>
    </section>
  )
}

export default AdminPage
