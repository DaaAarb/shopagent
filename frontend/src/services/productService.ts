import { http } from './httpClient'
import type { Product } from './types'

export const productService = {
  list: () => http.get<Product[]>('/products'),
}
