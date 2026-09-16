const PALETTE = [
  '#4f46e5',
  '#0891b2',
  '#059669',
  '#d97706',
  '#dc2626',
  '#7c3aed',
  '#db2777',
  '#2563eb',
]

function hashString(value) {
  let hash = 0
  for (let index = 0; index < value.length; index += 1) {
    hash = (hash * 31 + value.charCodeAt(index)) | 0
  }
  return Math.abs(hash)
}

function initials(name) {
  const words = name.trim().split(/\s+/).filter(Boolean).slice(0, 2)
  if (words.length === 0) return '?'
  const letters = words
    .map((word) => {
      const letter = word.replace(/[^a-zA-Z]/g, '')[0]
      return letter ? letter.toUpperCase() : ''
    })
    .filter(Boolean)
    .join('')
  return letters || '?'
}

function ProductImage({ name, category, imageUrl }) {
  if (imageUrl) {
    return <img className="product-image" src={imageUrl} alt={name} />
  }
  const color = PALETTE[hashString(category || name || '') % PALETTE.length]
  return (
    <svg
      className="product-image"
      viewBox="0 0 96 96"
      preserveAspectRatio="xMidYMid slice"
      role="img"
      aria-label={name}
    >
      <rect width="96" height="96" fill={color} />
      <text
        x="48"
        y="48"
        dominantBaseline="central"
        textAnchor="middle"
        fontSize="32"
        fontFamily="Inter, sans-serif"
        fontWeight="600"
        fill="#ffffff"
      >
        {initials(name)}
      </text>
    </svg>
  )
}

export default ProductImage
