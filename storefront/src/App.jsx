import { Route, Routes } from 'react-router-dom'

import Layout from './components/Layout'
import AdminPage from './pages/AdminPage'
import CartPage from './pages/CartPage'
import ImportPage from './pages/ImportPage'
import ProductForm from './pages/ProductForm'
import ProductList from './pages/ProductList'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<ProductList />} />
        <Route path="/cart" element={<CartPage />} />
        <Route path="/admin" element={<AdminPage />} />
        <Route path="/import" element={<ImportPage />} />
        <Route path="/products/new" element={<ProductForm />} />
        <Route path="/products/:id/edit" element={<ProductForm />} />
      </Routes>
    </Layout>
  )
}

export default App
