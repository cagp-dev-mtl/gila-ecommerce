import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { createProduct, formatError, getProduct, updateProduct } from '../api/client'

const EMPTY = {
  sku: '',
  name: '',
  description: '',
  category: '',
  price: '',
  stock: '0',
  weight_kg: '',
  image_url: '',
}

function ProductForm() {
  const { id } = useParams()
  const navigate = useNavigate()
  const editing = Boolean(id)
  const [form, setForm] = useState(EMPTY)
  const [error, setError] = useState(null)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!editing) {
      return
    }
    getProduct(id)
      .then((product) =>
        setForm({
          sku: product.sku,
          name: product.name,
          description: product.description || '',
          category: product.category || '',
          price: product.price,
          stock: String(product.stock),
          weight_kg: product.weight_kg || '',
          image_url: product.image_url || '',
        }),
      )
      .catch((err) => setError(formatError(err)))
  }, [id, editing])

  function update(field) {
    return (event) => setForm((current) => ({ ...current, [field]: event.target.value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setSaving(true)
    setError(null)
    const payload = {
      sku: form.sku,
      name: form.name,
      description: form.description || null,
      category: form.category || null,
      price: form.price,
      stock: Number(form.stock),
      weight_kg: form.weight_kg === '' ? null : form.weight_kg,
      image_url: form.image_url || null,
    }
    try {
      if (editing) {
        await updateProduct(id, payload)
      } else {
        await createProduct(payload)
      }
      navigate('/')
    } catch (err) {
      setError(formatError(err))
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="form-page">
      <h2>{editing ? 'Edit product' : 'New product'}</h2>
      {error && <p className="alert alert-error">{error}</p>}
      <form className="form" onSubmit={handleSubmit}>
        <label className="field">
          <span>Name</span>
          <input className="input" value={form.name} onChange={update('name')} required />
        </label>
        <label className="field">
          <span>SKU</span>
          <input className="input" value={form.sku} onChange={update('sku')} required />
        </label>
        <label className="field field-wide">
          <span>Description</span>
          <textarea className="input" rows="3" value={form.description} onChange={update('description')} />
        </label>
        <label className="field">
          <span>Category</span>
          <input className="input" value={form.category} onChange={update('category')} />
        </label>
        <label className="field">
          <span>Image URL</span>
          <input className="input" value={form.image_url} onChange={update('image_url')} />
        </label>
        <label className="field">
          <span>Price</span>
          <input className="input" type="number" step="0.01" min="0" value={form.price} onChange={update('price')} required />
        </label>
        <label className="field">
          <span>Stock</span>
          <input className="input" type="number" step="1" min="0" value={form.stock} onChange={update('stock')} required />
        </label>
        <label className="field">
          <span>Weight (kg)</span>
          <input className="input" type="number" step="0.001" min="0" value={form.weight_kg} onChange={update('weight_kg')} />
        </label>
        <div className="form-actions">
          <button type="button" className="button" onClick={() => navigate('/')}>
            Cancel
          </button>
          <button type="submit" className="button button-primary" disabled={saving}>
            {saving ? 'Saving...' : 'Save product'}
          </button>
        </div>
      </form>
    </section>
  )
}

export default ProductForm
