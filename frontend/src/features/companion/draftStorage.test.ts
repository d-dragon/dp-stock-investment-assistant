import { describe, expect, it } from 'vitest'
import { clearDraft, draftKey, readDraft, writeDraft } from './draftStorage'

const ref = { sessionId: 's1', conversationId: 'c1' }

describe('draft storage', () => {
  it('namespaces the key and clears it only on send', () => {
    sessionStorage.clear()
    expect(draftKey(ref)).toBe('dp-stock:z4-draft:s1:c1')
    writeDraft(ref, 'hello')
    expect(readDraft(ref)).toBe('hello')
    expect(sessionStorage.getItem(draftKey(ref))).toBe('hello')
    clearDraft(ref)
    expect(sessionStorage.getItem(draftKey(ref))).toBeNull()
  })
})
