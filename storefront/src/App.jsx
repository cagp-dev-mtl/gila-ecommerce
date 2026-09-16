import { Route, Routes } from 'react-router-dom'

import Layout from './components/Layout'
import ImportPage from './pages/ImportPage'
import ProductForm from './pages/ProductForm'
import ProductList from './pages/ProductList'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<ProductList />} />
        <Route path="/import" element={<ImportPage />} />
        <Route path="/products/new" element={<ProductForm />} />
        <Route path="/products/:id/edit" element={<ProductForm />} />
      </Routes>
    </Layout>
  )
}

export default App
