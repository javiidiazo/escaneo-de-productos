import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { fetchProductByBarcode } from '../api/client.js'
import ProductCard from '../components/ProductCard.jsx'

function ProductPage () {
  const { barcode } = useParams()
  const [status, setStatus] = useState('loading')
  const [product, setProduct] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function loadProduct () {
      setStatus('loading')
      try {
        const data = await fetchProductByBarcode(barcode)
        setProduct(data)
        setStatus('loaded')
      } catch (err) {
        setError(err)
        setStatus('error')
      }
    }
    loadProduct()
  }, [barcode])

  if (status === 'loading') {
    return <div className="card"><p>Buscando el producto...</p></div>
  }

  if (status === 'error') {
    return (
      <div className="card">
        <h2>No encontramos el producto</h2>
        <p>Probá escanearlo de nuevo o consultá con el equipo del local.</p>
        {error && <pre style={{ background: '#f1f5f9', padding: '1rem', borderRadius: '0.75rem' }}>{error.message}</pre>}
        <Link className="button-primary" to="/">Volver a escanear</Link>
      </div>
    )
  }

  return (
    <div>
      <ProductCard product={product} />
      <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
        <Link className="button-primary" to="/">Escanear otro producto</Link>
      </div>
    </div>
  )
}

export default ProductPage
