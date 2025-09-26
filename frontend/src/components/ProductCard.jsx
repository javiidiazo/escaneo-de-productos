function ProductCard ({ product }) {
  const {
    title,
    price,
    currency,
    image_url: imageUrl,
    description,
    brand,
    attributes
  } = product

  return (
    <div className="card">
      {imageUrl && <img className="product-image" src={imageUrl} alt={title} />}
      <div className="product-meta">
        <h2>{title}</h2>
        <p><strong>Precio:</strong> {currency} {Number(price).toLocaleString('es-AR')}</p>
        {brand && <p><strong>Marca:</strong> {brand}</p>}
        {description && <p>{description}</p>}
        {attributes && Object.keys(attributes).length > 0 && (
          <section>
            <h3>Detalles</h3>
            <ul>
              {Object.entries(attributes).map(([key, value]) => (
                <li key={key}><strong>{key}:</strong> {value}</li>
              ))}
            </ul>
          </section>
        )}
      </div>
    </div>
  )
}

export default ProductCard
