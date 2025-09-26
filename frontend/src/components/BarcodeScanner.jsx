import { BrowserMultiFormatReader } from '@zxing/library'
import { useEffect, useRef, useState } from 'react'

const DEFAULT_HINTS = {
  tryHarder: true
}

function BarcodeScanner ({ onDetected, onError, active }) {
  const videoRef = useRef(null)
  const codeReaderRef = useRef(null)
  const [isActive, setIsActive] = useState(false)
  const detectedRef = useRef(onDetected)
  const errorRef = useRef(onError)

  useEffect(() => {
    detectedRef.current = onDetected
  }, [onDetected])

  useEffect(() => {
    errorRef.current = onError
  }, [onError])

  useEffect(() => {
    const codeReader = new BrowserMultiFormatReader()
    codeReaderRef.current = codeReader

    function stopScanner () {
      codeReader.reset()
      setIsActive(false)
    }

    async function startScanner () {
      try {
        const devices = await codeReader.listVideoInputDevices()
        const preferredDevice = devices.find(device => /back|rear|environment/i.test(device.label))
        await codeReader.decodeFromVideoDevice(
          preferredDevice ? preferredDevice.deviceId : undefined,
          videoRef.current,
          (result, err) => {
            if (result) {
              detectedRef.current?.(result.getText())
              stopScanner()
            }
            if (err && err.name !== 'NotFoundException') {
              errorRef.current?.(err)
            }
          },
          DEFAULT_HINTS
        )
        setIsActive(true)
      } catch (error) {
        if (error?.name === 'NotFoundException') {
          return
        }
        setIsActive(false)
        stopScanner()
        errorRef.current?.(error)
      }
    }

    if (active) {
      startScanner()
    } else {
      stopScanner()
    }

    return () => {
      stopScanner()
    }
  }, [active])

  return (
    <div>
      <video ref={videoRef} style={{ width: '100%', borderRadius: '0.75rem' }} autoPlay muted playsInline />
      {active && !isActive && <p>No pudimos acceder a la cámara. Revisá permisos y volvé a intentar.</p>}
    </div>
  )
}

export default BarcodeScanner
