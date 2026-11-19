import ReactMarkdown, { defaultUrlTransform } from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { t } from '../../../platform/i18n/t'

export interface MessageBodyProps {
  body: string
  origin: 'ai' | 'investor'
}

export function MessageBody({ body, origin }: MessageBodyProps) {
  const dashed = origin === 'ai'
  return (
    <div
      data-origin={origin}
      style={{
        borderWidth: 1,
        borderStyle: dashed ? 'dashed' : 'solid',
        borderColor: dashed ? 'var(--surface-text2)' : 'var(--surface-text)',
      }}
    >
      <p>{dashed ? t('ai.suggested') : t('ai.confirmed')}</p>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        skipHtml
        urlTransform={defaultUrlTransform}
        components={{
          a: ({ href, children }) => (
            <a href={href} rel="noopener noreferrer nofollow" target="_blank">
              {children}
            </a>
          ),
          img: () => null,
        }}
      >
        {body}
      </ReactMarkdown>
    </div>
  )
}
