import { useRef, useState } from 'react'
import { chatRequestFromSession, type SessionRef } from '../../platform/api/sessionRef'
import { openChatStream } from '../../platform/stream/openChatStream'
import type { StreamHandle } from '../../platform/stream/types'
import { t } from '../../platform/i18n/t'
import { MessageBody } from '../../design-system/patterns/MessageBody'
import { clearDraft, readDraft, writeDraft } from './draftStorage'

export type RunStatus = 'idle' | 'streaming' | 'done' | 'interrupted' | 'error'

export interface CompanionProps {
  sessionRef: SessionRef
}

export function Companion({ sessionRef }: CompanionProps) {
  const [status, setStatus] = useState<RunStatus>('idle')
  const [draft, setDraft] = useState(() => readDraft(sessionRef))
  const [partial, setPartial] = useState('')
  const [sent, setSent] = useState('')
  const run = useRef<StreamHandle | null>(null)
  const stopRequested = useRef(false)

  const keepDraft = (next: string) => {
    setDraft(next)
    writeDraft(sessionRef, next)
  }

  const send = (message: string) => {
    if (!message) return
    stopRequested.current = false
    setSent(message)
    setStatus('streaming')
    setPartial('')
    clearDraft(sessionRef)
    setDraft('')
    const handle = openChatStream(chatRequestFromSession(sessionRef, { message, stream: true }))
    run.current = handle
    void (async () => {
      let text = ''
      try {
        for await (const event of handle.events) {
          if (stopRequested.current) break
          if ('text' in event) {
            text += event.text
            if (!stopRequested.current) setPartial(text)
          } else if ('error' in event) {
            setStatus('error')
          } else if ('fallback' in event) {
            setStatus('done')
          }
        }
      } finally {
        if (stopRequested.current) return
        const outcome = handle.outcome()
        if (outcome === 'interrupted' || outcome === 'aborted') {
          setStatus('interrupted')
          writeDraft(sessionRef, message)
          setDraft(message)
        } else if (outcome === 'error') {
          setStatus('error')
        } else if (outcome === 'ended') {
          setStatus('done')
        }
      }
    })()
  }

  const stop = () => {
    stopRequested.current = true
    run.current?.abort()
    setStatus('interrupted')
    const kept = sent || draft
    writeDraft(sessionRef, kept)
    setDraft(kept)
  }

  const streaming = status === 'streaming'
  const announced = streaming ? '' : partial

  return (
    <div>
      {streaming && partial ? <MessageBody body={partial} origin="ai" /> : null}
      <div aria-live="polite">{announced ? <MessageBody body={announced} origin="ai" /> : null}</div>
      <form
        onSubmit={(event) => {
          event.preventDefault()
          send(draft)
        }}
      >
        <label>
          {t('shell.zone.z4')}
          <textarea
            value={draft}
            aria-label={t('app.placeholder')}
            onChange={(event) => keepDraft(event.target.value)}
          />
        </label>
        <button type="submit">{t('app.send')}</button>
        {streaming ? (
          <button type="button" onClick={stop}>
            {t('app.cancel')}
          </button>
        ) : null}
        {status === 'interrupted' || status === 'error' ? (
          <button type="button" onClick={() => send(sent)}>
            {t('stream.retry')}
          </button>
        ) : null}
      </form>
    </div>
  )
}
