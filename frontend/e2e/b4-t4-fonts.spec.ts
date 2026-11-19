import { expect, test } from '@playwright/test'

const THIRD_PARTY_FONT_HOST = /fonts\.googleapis\.com|fonts\.gstatic\.com|use\.typekit\.net|fast\.fonts\.net|fontshare\.com|cdnfonts\.com|fonts\.cdnfonts\.com/i

function familyStartsWith(computed: string, family: string): boolean {
  return computed.replace(/["']/g, '').trim().startsWith(family)
}

test('self-hosted fonts: IBM Plex Mono for fmt, Be Vietnam Pro for UI', async ({ page }) => {
  const hosts: string[] = []
  page.on('request', (request) => {
    try {
      hosts.push(new URL(request.url()).host)
    } catch {
      hosts.push(request.url())
    }
  })

  await page.goto('/')

  expect(hosts.filter((host) => THIRD_PARTY_FONT_HOST.test(host))).toEqual([])

  const shell = page.locator('[data-ui="shell"]')
  await expect(shell).toBeVisible()

  const titleFamily = await shell.getByRole('heading', { level: 1 }).evaluate((element) => {
    return getComputedStyle(element).fontFamily
  })
  expect(familyStartsWith(titleFamily, 'Be Vietnam Pro')).toBe(true)

  const fmt = shell.locator('[data-fmt]').first()
  await expect(fmt).toBeVisible()
  const fmtFamily = await fmt.evaluate((element) => getComputedStyle(element).fontFamily)
  expect(familyStartsWith(fmtFamily, 'IBM Plex Mono')).toBe(true)
  await expect(fmt).not.toHaveText('25.30')
})
