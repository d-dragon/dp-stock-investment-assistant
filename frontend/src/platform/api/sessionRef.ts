export interface SessionRef {
  sessionId: string
  conversationId: string
}

export interface ChatRequestFields {
  message: string
  stream?: boolean
  provider?: string
  conversation_id?: string
}

/**
 * `sessionId` stays off the wire. Where it belongs on POST /api/chat is still open
 * (research R7). `session_id` is a deprecated alias for `conversation_id`.
 */
export function chatRequestFromSession(ref: SessionRef, fields: ChatRequestFields): ChatRequestFields {
  const body: ChatRequestFields = {
    message: fields.message,
    conversation_id: ref.conversationId,
  }
  if (fields.stream !== undefined) body.stream = fields.stream
  if (fields.provider) body.provider = fields.provider
  return body
}
