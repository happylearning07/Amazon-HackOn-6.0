const API_BASE = 'https://secondlife-backend-dzl6.onrender.com'

export async function gradeItem(imageFile, formData) {
  const body = new FormData()
  body.append('file', imageFile)
  body.append('item_name', formData.itemName.trim())
  body.append('original_price', String(parseFloat(formData.originalPrice)))
  body.append('category', formData.category)
  body.append('asin', formData.asin || '')
  body.append('seller_id', formData.sellerId)

  const response = await fetch(`${API_BASE}/api/grade`, {
    method: 'POST',
    body,
  })

  if (!response.ok) {
    let detail = 'Grading failed — is the backend running on port 8000?'
    try {
      const err = await response.json()
      detail = err.detail || detail
    } catch {
      /* ignore */
    }
    throw new Error(typeof detail === 'string' ? detail : 'Grading failed')
  }

  return response.json()
}

export async function routeItem(listingId, action) {
  const body = new FormData()
  body.append('action', action)

  const response = await fetch(`${API_BASE}/api/route/${listingId}`, {
    method: 'POST',
    body,
  })

  if (!response.ok) {
    throw new Error('Routing failed')
  }

  return response.json()
}

export async function fetchMarketplace() {
  const response = await fetch(`${API_BASE}/api/marketplace`)
  if (!response.ok) {
    throw new Error('Could not load marketplace')
  }
  const data = await response.json()
  return data.listings || []
}

export async function fetchSeller(sellerId) {
  const response = await fetch(`${API_BASE}/api/seller/${sellerId}`)
  if (!response.ok) {
    throw new Error('Could not load seller profile')
  }
  return response.json()
}
