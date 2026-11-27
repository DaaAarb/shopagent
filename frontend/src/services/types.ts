// Reflejan los DTOs de backend/app/dtos/.

export type ProductCategory = 'balls' | 'chew' | 'rope' | 'plush' | 'interactive'
export type DogSize = 'small' | 'medium' | 'large' | 'all'
export type OrderStatus = 'pending' | 'paid' | 'shipped' | 'delivered' | 'cancelled'

export interface User {
  id: number
  name: string
  email: string
}

export interface Product {
  id: number
  slug: string
  name: string
  category: ProductCategory
  description: string
  price_cents: number
  stock: number
  material: string
  dog_size: DogSize
  image_url: string | null
  model_url: string | null
}

export interface OrderItem {
  product_id: number
  product_name: string
  quantity: number
  unit_price_cents: number
}

export interface Order {
  id: number
  status: OrderStatus
  total_cents: number
  shipping_address: string
  created_at: string // ISO 8601
  items: OrderItem[]
}

export interface OrderCreate {
  items: { product_id: number; quantity: number }[]
  shipping_address: string
}

export interface PendingAction {
  id: string
  description: string
}

export interface ChatReply {
  reply: string
  pending_action: PendingAction | null
}
