import type { SessionRef } from '../../platform/api/sessionRef'

export function draftKey(ref: Pick<SessionRef, 'sessionId' | 'conversationId'>): string {
  return `dp-stock:z4-draft:${ref.sessionId}:${ref.conversationId}`
}

export function readDraft(ref: SessionRef): string {
  return sessionStorage.getItem(draftKey(ref)) ?? ''
}

export function writeDraft(ref: SessionRef, text: string): void {
  sessionStorage.setItem(draftKey(ref), text)
}

export function clearDraft(ref: SessionRef): void {
  sessionStorage.removeItem(draftKey(ref))
}
