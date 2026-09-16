function PageBanner({ title, crumb }) {
  return (
    <div className="page-banner">
      <h1 className="page-banner-title">{title}</h1>
      {crumb && <p className="page-banner-crumb">{crumb}</p>}
    </div>
  )
}

export default PageBanner
