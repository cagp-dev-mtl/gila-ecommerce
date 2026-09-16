const BASE = '/api'

export class ApiError extends Error {
  constructor(status, detail) {
    super(typeof detail === 'string' ? detail : 'Request failed')
    this.status = status
    this.detail = detail
  }
}

async function request(path, options = {}) {
  const response = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  })
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new ApiError(response.status, body ? body.detail : response.statusText)
  }
  if (response.status === 204) {
    return null
  }
  return response.json()
}

function buildQuery(params) {
  const query = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== '' && value !== null && value !== undefined) {
      query.set(key, value)
    }
  })
  return query.toString()
}

export function listProducts(params) {
  return request(`/products?${buildQuery(params)}`)
}

export function getProduct(id) {
  return request(`/products/${id}`)
}

export function createProduct(data) {
  return request('/products', { method: 'POST', body: JSON.stringify(data) })
}

export function updateProduct(id, data) {
  return request(`/products/${id}`, { method: 'PUT', body: JSON.stringify(data) })
}

export function deleteProduct(id) {
  return request(`/products/${id}`, { method: 'DELETE' })
}

export function listCategories() {
  return request('/products/categories')
}

export async function importProducts(file) {
  const body = new FormData()
  body.append('file', file)
  const response = await fetch(`${BASE}/products/import`, { method: 'POST', body })
  if (!response.ok) {
    const detail = await response.json().catch(() => null)
    throw new ApiError(response.status, detail ? detail.detail : response.statusText)
  }
  return response.json()
}

export function createOrder(items, idempotencyKey) {
  return request('/orders', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey },
    body: JSON.stringify({ items }),
  })
}

export function formatError(error) {
  const detail = error && error.detail
  if (Array.isArray(detail)) {
    return detail.map((item) => `${item.loc[item.loc.length - 1]}: ${item.msg}`).join('. ')
  }
  if (typeof detail === 'string') {
    return detail
  }
  return error && error.message ? error.message : 'Request failed'
}
