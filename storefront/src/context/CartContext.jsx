import { createContext, useContext, useReducer } from 'react'

const CartContext = createContext(null)

function reducer(state, action) {
  switch (action.type) {
    case 'ADD': {
      const existing = state[action.product.id]
      const next = existing
        ? { ...existing, quantity: existing.quantity + 1 }
        : { product: action.product, quantity: 1 }
      return { ...state, [action.product.id]: next }
    }
    case 'SET': {
      if (action.quantity <= 0) {
        const next = { ...state }
        delete next[action.productId]
        return next
      }
      return {
        ...state,
        [action.productId]: { ...state[action.productId], quantity: action.quantity },
      }
    }
    case 'REMOVE': {
      const next = { ...state }
      delete next[action.productId]
      return next
    }
    case 'CLEAR':
      return {}
    default:
      return state
  }
}

export function CartProvider({ children }) {
  const [items, dispatch] = useReducer(reducer, {})

  function addItem(product) {
    dispatch({ type: 'ADD', product })
  }

  function setQuantity(productId, quantity) {
    dispatch({ type: 'SET', productId, quantity })
  }

  function removeItem(productId) {
    dispatch({ type: 'REMOVE', productId })
  }

  function clearCart() {
    dispatch({ type: 'CLEAR' })
  }

  const entries = Object.values(items)
  const count = entries.reduce((sum, entry) => sum + entry.quantity, 0)
  const total = entries.reduce(
    (sum, entry) => sum + parseFloat(entry.product.price) * entry.quantity,
    0
  )

  return (
    <CartContext.Provider value={{ items, entries, count, total, addItem, setQuantity, removeItem, clearCart }}>
      {children}
    </CartContext.Provider>
  )
}

export function useCart() {
  return useContext(CartContext)
}
