import { http } from './httpClient'
import type { ChatReply } from './types'

export const chatService = {
  send: (message: string) => http.post<ChatReply>('/chat', { message }),
  confirm: (actionId: string, approve: boolean) =>
    http.post<ChatReply>('/chat/confirm', { action_id: actionId, approve }),
}
