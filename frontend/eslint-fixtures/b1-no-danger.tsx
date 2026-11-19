export function UnsafeHtml(props: { html: string }) {
  return <div dangerouslySetInnerHTML={{ __html: props.html }} />
}
