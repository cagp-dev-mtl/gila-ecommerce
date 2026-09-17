import { useEffect, useRef, useState, useCallback } from 'react'

import { formatError, listCategories, listProducts } from '../api/client'
import ProductImage from '../components/ProductImage'
import { useCart } from '../context/CartContext'
import { useDebounce } from '../hooks/useDebounce'

const PAGE_SIZE = 10
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
  const { addItem } = useCart()
  const catalogRef = useRef(null)
  const [addedId, setAddedId] = useState(null)

  const handleAddItem = useCallback((product) => {
    addItem(product)
    setAddedId(product.id)
    setTimeout(() => setAddedId(null), 1200)
  }, [addItem])

  const hasFilters = search !== '' || category !== ''

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
        if (active) setError(formatError(err))
      })
      .finally(() => {
        if (active) setLoading(false)
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

  function clearFilters() {
    setSearch('')
    setCategory('')
    setPage(1)
  }

  function toggleCategory(name) {
    setCategory((current) => (current === name ? '' : name))
    setPage(1)
    catalogRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <section>
      <div className="hero">
        <div className="hero-content">
          <p className="hero-eyebrow">New arrivals every day</p>
          <h1 className="hero-title">Find what you&apos;re looking for</h1>
          <p className="hero-sub">
            {data.total > 0
              ? `${data.total} products across ${categories.length} categories`
              : 'Search, filter, and discover products from our full catalog'}
          </p>
          <button
            className="hero-cta"
            onClick={() => catalogRef.current?.scrollIntoView({ behavior: 'smooth' })}
          >
            Shop now
          </button>
        </div>
      </div>

      {categories.length > 0 && (
        <div className="category-strip">
          {categories.map((name) => (
            <button
              key={name}
              className={`category-chip${category === name ? ' category-chip-active' : ''}`}
              onClick={() => toggleCategory(name)}
            >
              {name}
            </button>
          ))}
        </div>
      )}

      <div ref={catalogRef} className="catalog-section">
        <div className="toolbar">
          <input
            className={`input search${search ? ' filter-active' : ''}`}
            type="search"
            placeholder="Search by name, SKU or description"
            value={search}
            onChange={changeFilter(setSearch)}
          />
          <select
            className={`input${category ? ' filter-active' : ''}`}
            value={category}
            onChange={changeFilter(setCategory)}
          >
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
          {hasFilters && (
            <button className="button" onClick={clearFilters}>
              Clear filters
            </button>
          )}
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
                <div className="product-card-image">
                  <ProductImage
                    name={product.name}
                    category={product.category}
                    imageUrl={product.image_url}
                  />
                </div>
                <div className="product-body">
                  {product.category && <span className="badge">{product.category}</span>}
                  <h3 className="product-name">{product.name}</h3>
                  <p className="product-meta">
                    <span className="sku">{product.sku}</span>
                  </p>
                  <p className="product-price">${parseFloat(product.price).toFixed(2)}</p>
                  <p className={product.stock > 0 ? 'stock' : 'stock stock-out'}>
                    {product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
                  </p>
                </div>
                <div className="product-card-footer">
                  <button
                    className={`btn-add-cart${addedId === product.id ? ' btn-add-cart--added' : ''}`}
                    disabled={product.stock === 0}
                    onClick={() => handleAddItem(product)}
                  >
                    {addedId === product.id ? '✓ Added' : product.stock === 0 ? 'Out of stock' : 'Add to cart'}
                  </button>
                </div>
              </article>
            ))}
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
      </div>
    </section>
  )
}

export default ProductList
