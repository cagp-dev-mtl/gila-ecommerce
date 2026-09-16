import { useState } from 'react'
import { Link } from 'react-router-dom'

import { createOrder, formatError } from '../api/client'
import { useCart } from '../context/CartContext'

function CartPage() {
  const { entries, count, total, setQuantity, removeItem, clearCart } = useCart()
  const [submitting, setSubmitting] = useState(false)
  const [order, setOrder] = useState(null)
  const [error, setError] = useState(null)

  async function handleCheckout() {
    setSubmitting(true)
    setError(null)
    const idempotencyKey = crypto.randomUUID()
    try {
      const result = await createOrder(
        entries.map((entry) => ({ product_id: entry.product.id, quantity: entry.quantity })),
        idempotencyKey
      )
      clearCart()
      setOrder(result)
    } catch (err) {
      setError(formatError(err))
    } finally {
      setSubmitting(false)
    }
  }

  if (order) {
    return (
      <section className="form-page">
        <h2>Order confirmed</h2>
        <div className="order-confirmation">
          <p className="confirmation-label">Order ID</p>
          <p className="confirmation-value">#{order.id}</p>
          <p className="confirmation-label">Reference</p>
          <p className="confirmation-value">{order.payment_reference}</p>
          <p className="confirmation-label">Total</p>
          <p className="confirmation-value confirmation-total">${parseFloat(order.total).toFixed(2)}</p>
        </div>
        <div className="form-actions" style={{ marginTop: '24px' }}>
          <Link className="button button-primary" to="/">
            Continue shopping
          </Link>
        </div>
      </section>
    )
  }

  if (count === 0) {
    return (
      <section className="form-page">
        <h2>Cart</h2>
        <p className="muted">Your cart is empty.</p>
        <Link className="button button-primary" to="/">
          Browse products
        </Link>
      </section>
    )
  }

  return (
    <section className="form-page cart-page">
      <h2>Cart</h2>

      {error && <p className="alert alert-error">{error}</p>}

      <table className="cart-table">
        <thead>
          <tr>
            <th>Product</th>
            <th>Price</th>
            <th>Qty</th>
            <th>Subtotal</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {entries.map(({ product, quantity }) => (
            <tr key={product.id}>
              <td>
                <span className="cart-product-name">{product.name}</span>
                <span className="sku"> {product.sku}</span>
              </td>
              <td>${parseFloat(product.price).toFixed(2)}</td>
              <td>
                <input
                  className="input qty-input"
                  type="number"
                  min="1"
                  max={product.stock}
                  value={quantity}
                  onChange={(e) => setQuantity(product.id, parseInt(e.target.value, 10) || 1)}
                />
              </td>
              <td>${(parseFloat(product.price) * quantity).toFixed(2)}</td>
              <td>
                <button className="button button-danger" onClick={() => removeItem(product.id)}>
                  Remove
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="cart-footer">
        <span className="cart-total">Total: ${total.toFixed(2)}</span>
        <button
          className="button button-primary"
          disabled={submitting}
          onClick={handleCheckout}
        >
          {submitting ? 'Placing order...' : 'Place order'}
        </button>
      </div>
    </section>
  )
}

export default CartPage
