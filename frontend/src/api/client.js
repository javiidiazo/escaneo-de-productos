import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 8000
})

export const fetchProductByBarcode = async (barcode) => {
  const response = await client.get(`/products/${barcode}`)
  return response.data
}

export default client
