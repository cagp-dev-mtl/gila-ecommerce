import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { deleteProduct, formatError, listCategories, listProducts } from '../api/client'
import ProductImage from '../components/ProductImage'
import { useDebounce } from '../hooks/useDebounce'

const PAGE_SIZE = 12
const EMPTY_PAGE = { items: [], total: 0, page: 1, page_size: PAGE_SIZE, pages: 0 }

function ProductList() {
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')
  const [sort, setSort] = useState('name')
  const [order, setOrder] = useState('asc')
  const [page, setPage] = useState(1)
  const [data, setData] = useState(EMPTY_PAGE)
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const debouncedSearch = useDebounce(search, 300)

  useEffect(() => {
    listCategories()
      .then(setCategories)
      .catch(() => setCategories([]))
  }, [])

  useEffect(() => {
    let active = true
    setLoading(true)
    listProducts({ search: debouncedSearch, category, sort, order, page, page_size: PAGE_SIZE })
      .then((result) => {
        if (active) {
          setData(result)
          setError(null)
        }
      })
      .catch((err) => {
        if (active) {
          setError(formatError(err))
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false)
        }
      })
    return () => {
      active = false
    }
  }, [debouncedSearch, category, sort, order, page])

  function changeFilter(setter) {
    return (event) => {
      setter(event.target.value)
      setPage(1)
    }
  }

  async function handleDelete(product) {
    if (!window.confirm(`Delete "${product.name}"?`)) {
      return
    }
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
      <div className="toolbar">
        <input
          className="input search"
          type="search"
          placeholder="Search by name, SKU or description"
          value={search}
          onChange={changeFilter(setSearch)}
        />
        <select className="input" value={category} onChange={changeFilter(setCategory)}>
          <option value="">All categories</option>
          {categories.map((name) => (
            <option key={name} value={name}>
              {name}
            </option>
          ))}
        </select>
        <select className="input" value={sort} onChange={changeFilter(setSort)}>
          <option value="name">Name</option>
          <option value="price">Price</option>
          <option value="newest">Newest</option>
        </select>
        <select className="input" value={order} onChange={changeFilter(setOrder)}>
          <option value="asc">Ascending</option>
          <option value="desc">Descending</option>
        </select>
      </div>

      {error && <p className="alert alert-error">{error}</p>}

      {loading && data.items.length === 0 ? (
        <p className="muted">Loading products...</p>
      ) : data.items.length === 0 ? (
        <p className="muted">No products found.</p>
      ) : (
        <div className="product-grid">
          {data.items.map((product) => (
            <article key={product.id} className="product-card">
              <ProductImage
                name={product.name}
                category={product.category}
                imageUrl={product.image_url}
              />
              <div className="product-body">
                <h3 className="product-name">{product.name}</h3>
                <p className="product-meta">
                  <span className="sku">{product.sku}</span>
                  {product.category && <span className="badge">{product.category}</span>}
                </p>
                <p className="product-price">${product.price}</p>
                <p className={product.stock > 0 ? 'stock' : 'stock stock-out'}>
                  {product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
                </p>
              </div>
              <div className="product-actions">
                <Link className="button" to={`/products/${product.id}/edit`}>
                  Edit
                </Link>
                <button className="button button-danger" onClick={() => handleDelete(product)}>
                  Delete
                </button>
              </div>
            </article>
          ))}
        </div>
      )}

      <div className="pagination">
        <button className="button" disabled={page <= 1} onClick={() => setPage((value) => value - 1)}>
          Previous
        </button>
        <span className="muted">
          Page {data.pages === 0 ? 0 : data.page} of {data.pages} ({data.total} products)
        </span>
        <button
          className="button"
          disabled={page >= data.pages}
          onClick={() => setPage((value) => value + 1)}
        >
          Next
        </button>
      </div>
    </section>
  )
}

export default ProductList
