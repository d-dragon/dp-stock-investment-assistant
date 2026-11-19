import { messages } from './messages/vi-VN'

export type MessageKey = keyof typeof messages

export function t(key: MessageKey): string {
  return messages[key]
}
