import { useState } from 'react'
import { Link } from 'react-router-dom'

import { formatError, importProducts } from '../api/client'
import PageBanner from '../components/PageBanner'

function ImportPage() {
  const [file, setFile] = useState(null)
  const [report, setReport] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    if (!file) return
    setLoading(true)
    setError(null)
    setReport(null)
    try {
      const result = await importProducts(file)
      setReport(result)
    } catch (err) {
      setError(formatError(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <section>
      <PageBanner title="Import Catalog" crumb="Home / Import" />
      <Link className="back-link" to="/admin">← Back to Admin</Link>

      <div className="form-page">
        <p className="muted">
          Upload a CSV with columns name, sku, description, category, price, stock, weight_kg. Each
          row is validated independently and the result is reported below.
        </p>

        <form className="import-form" onSubmit={handleSubmit}>
          <input
            className="input"
            type="file"
            accept=".csv,text/csv"
            onChange={(event) => setFile(event.target.files[0] || null)}
          />
          <button className="button button-primary" type="submit" disabled={!file || loading}>
            {loading ? 'Importing...' : 'Import'}
          </button>
        </form>

        {error && <p className="alert alert-error">{error}</p>}

        {report && (
          <div className="report">
            <div className="stats">
              <div className="stat">
                <span className="stat-value">{report.total}</span>
                <span className="stat-label">Total rows</span>
              </div>
              <div className="stat">
                <span className="stat-value stat-ok">{report.imported}</span>
                <span className="stat-label">Imported</span>
              </div>
              <div className="stat">
                <span className="stat-value stat-ok">{report.updated}</span>
                <span className="stat-label">Updated</span>
              </div>
              <div className="stat">
                <span className="stat-value">{report.skipped}</span>
                <span className="stat-label">Skipped</span>
              </div>
              <div className="stat">
                <span className="stat-value stat-error">{report.errors.length}</span>
                <span className="stat-label">Rejected</span>
              </div>
            </div>

            {report.errors.length > 0 && (
              <table className="error-table">
                <thead>
                  <tr>
                    <th>Row</th>
                    <th>Reason</th>
                  </tr>
                </thead>
                <tbody>
                  {report.errors.map((item) => (
                    <tr key={item.row}>
                      <td>{item.row}</td>
                      <td>{item.reason}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            <Link className="button" to="/">
              View catalog
            </Link>
          </div>
        )}
      </div>
    </section>
  )
}

export default ImportPage
