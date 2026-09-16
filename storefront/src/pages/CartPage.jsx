import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import { createOrder, formatError } from '../api/client'
import PageBanner from '../components/PageBanner'
import ProductImage from '../components/ProductImage'
import { useCart } from '../context/CartContext'

const EMPTY_PAYMENT = { name: '', number: '', expiry: '', cvc: '' }

function CartPage() {
  const { entries, count, total, setQuantity, removeItem, clearCart } = useCart()
  const [step, setStep] = useState('cart')
  const [payment, setPayment] = useState(EMPTY_PAYMENT)
  const [submitting, setSubmitting] = useState(false)
  const [order, setOrder] = useState(null)
  const [error, setError] = useState(null)

  const cartSignature = entries.map((e) => `${e.product.id}:${e.quantity}`).join('|')
  const idempotencyKey = useMemo(() => crypto.randomUUID(), [cartSignature])

  function handlePaymentChange(e) {
    setPayment((p) => ({ ...p, [e.target.name]: e.target.value }))
  }

  async function handlePlaceOrder() {
    setSubmitting(true)
    setError(null)
    try {
      const result = await createOrder(
        entries.map((e) => ({ product_id: e.product.id, quantity: e.quantity })),
        idempotencyKey
      )
      clearCart()
      setOrder(result)
      setStep('confirmed')
    } catch (err) {
      setError(formatError(err))
    } finally {
      setSubmitting(false)
    }
  }

  if (step === 'confirmed' && order) {
    return (
      <section>
        <PageBanner title="Order Confirmed" crumb="Home / Cart / Confirmation" />
        <div className="confirmation-card">
          <div className="confirmation-icon">✓</div>
          <h2>Thank you for your purchase</h2>
          <p className="muted">Your order has been placed and is being processed.</p>
          <div className="confirmation-details">
            <div className="confirmation-row">
              <span>Order</span>
              <strong>#{order.id}</strong>
            </div>
            <div className="confirmation-row">
              <span>Reference</span>
              <strong>{order.payment_reference}</strong>
            </div>
            <div className="confirmation-row confirmation-row-total">
              <span>Total charged</span>
              <strong>${parseFloat(order.total).toFixed(2)}</strong>
            </div>
          </div>
          <Link className="button button-primary" to="/">
            Continue shopping
          </Link>
        </div>
      </section>
    )
  }

  if (count === 0) {
    return (
      <section>
        <PageBanner title="Shopping Cart" crumb="Home / Cart" />
        <div className="empty-cart">
          <p>Your cart is empty.</p>
          <Link className="button button-primary" to="/">
            Browse products
          </Link>
        </div>
      </section>
    )
  }

  if (step === 'payment') {
    return (
      <section>
        <PageBanner title="Checkout" crumb="Home / Cart / Payment" />
        {error && <p className="alert alert-error">{error}</p>}
        <div className="checkout-layout">
          <aside className="order-summary">
            <h3>Order summary</h3>
            {entries.map(({ product, quantity }) => (
              <div key={product.id} className="summary-item">
                <span className="summary-name">
                  {product.name} <span className="muted">×{quantity}</span>
                </span>
                <span>${(parseFloat(product.price) * quantity).toFixed(2)}</span>
              </div>
            ))}
            <div className="summary-total">
              <span>Total</span>
              <strong>${total.toFixed(2)}</strong>
            </div>
          </aside>

          <div className="payment-form-card">
            <h3>Payment details</h3>
            <p className="payment-note">Demo environment — no real charges are made.</p>
            <div className="field">
              <label>Name on card</label>
              <input
                className="input"
                name="name"
                placeholder="Jane Smith"
                value={payment.name}
                onChange={handlePaymentChange}
              />
            </div>
            <div className="field">
              <label>Card number</label>
              <input
                className="input"
                name="number"
                placeholder="4242 4242 4242 4242"
                value={payment.number}
                onChange={handlePaymentChange}
                maxLength="19"
              />
            </div>
            <div className="payment-row">
              <div className="field">
                <label>Expiry</label>
                <input
                  className="input"
                  name="expiry"
                  placeholder="MM/YY"
                  value={payment.expiry}
                  onChange={handlePaymentChange}
                  maxLength="5"
                />
              </div>
              <div className="field">
                <label>CVC</label>
                <input
                  className="input"
                  name="cvc"
                  placeholder="123"
                  value={payment.cvc}
                  onChange={handlePaymentChange}
                  maxLength="3"
                />
              </div>
            </div>
            <div className="payment-actions">
              <button className="button" onClick={() => setStep('cart')}>
                Back to cart
              </button>
              <button
                className="button button-primary"
                disabled={submitting}
                onClick={handlePlaceOrder}
              >
                {submitting ? 'Processing...' : `Pay $${total.toFixed(2)}`}
              </button>
            </div>
          </div>
        </div>
      </section>
    )
  }

  return (
    <section>
      <PageBanner title="Shopping Cart" crumb="Home / Cart" />
      {error && <p className="alert alert-error">{error}</p>}
      <div className="cart-layout">
        <div className="cart-items-col">
          <div className="cart-items">
            {entries.map(({ product, quantity }) => (
              <div key={product.id} className="cart-item">
                <div className="cart-item-image">
                  <ProductImage
                    name={product.name}
                    category={product.category}
                    imageUrl={product.image_url}
                  />
                </div>
                <div className="cart-item-info">
                  <p className="cart-item-name">{product.name}</p>
                  <p className="cart-item-sku">{product.sku}</p>
                </div>
                <div className="cart-item-price">${parseFloat(product.price).toFixed(2)}</div>
                <div className="cart-qty">
                  <button
                    className="cart-qty-btn"
                    onClick={() => setQuantity(product.id, quantity - 1)}
                    disabled={quantity <= 1}
                  >
                    −
                  </button>
                  <span className="cart-qty-value">{quantity}</span>
                  <button
                    className="cart-qty-btn"
                    onClick={() => setQuantity(product.id, quantity + 1)}
                    disabled={quantity >= product.stock}
                  >
                    +
                  </button>
                </div>
                <div className="cart-item-subtotal">
                  ${(parseFloat(product.price) * quantity).toFixed(2)}
                </div>
                <button className="btn-remove" onClick={() => removeItem(product.id)}>
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>

        <aside className="cart-summary-card">
          <h3>Order summary</h3>
          <div className="summary-row">
            <span>Subtotal</span>
            <span>${total.toFixed(2)}</span>
          </div>
          <div className="summary-row">
            <span>Shipping</span>
            <span>Free</span>
          </div>
          <div className="summary-row summary-row-total">
            <span>Total</span>
            <strong>${total.toFixed(2)}</strong>
          </div>
          <button className="button button-primary btn-checkout" onClick={() => setStep('payment')}>
            Proceed to checkout
          </button>
        </aside>
      </div>
    </section>
  )
}

export default CartPage
