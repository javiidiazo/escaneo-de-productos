import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import BarcodeScanner from '../components/BarcodeScanner.jsx'

function ScannerPage () {
  const navigate = useNavigate()
  const [isActive, setIsActive] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')

  const handleDetected = (barcode) => {
    navigate(`/p/${barcode}`)
  }

  const handleError = (error) => {
    if (error?.name === 'NotFoundException') {
      return
    }
    console.error('Scanner error', error)
    if (error?.name === 'NotAllowedError') {
      setErrorMessage('No tenemos permiso para usar la cámara. Revisá los permisos del navegador.')
    } else {
      setErrorMessage('No pudimos leer el código. Revisá la iluminación y volvé a intentar.')
    }
  }

  return (
    <div className="card">
      <h2>Escaneá un producto</h2>
      <p>Permití el acceso a la cámara y enfocá el código de barras.</p>
      {!isActive && (
        <button
          type="button"
          className="button-primary"
          onClick={async () => {
            try {
              await navigator.mediaDevices.getUserMedia({ video: true })
              setIsActive(true)
              setErrorMessage('')
            } catch (err) {
              handleError(err)
            }
          }}
        >
          Iniciar cámara
        </button>
      )}
      {isActive && (
        <BarcodeScanner
          active={isActive}
          onDetected={handleDetected}
          onError={handleError}
        />
      )}
      {errorMessage && <p>{errorMessage}</p>}
    </div>
  )
}

export default ScannerPage
