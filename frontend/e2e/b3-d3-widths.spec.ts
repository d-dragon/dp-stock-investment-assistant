import { expect, test } from '@playwright/test'

const widths = [1920, 1440, 1024, 768]

for (const width of widths) {
  test(`shell at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 })
    await page.goto('/')
    await expect(page.locator('html')).toHaveAttribute('data-mocks', 'on')
    const zones = ['z1', 'z2', 'z3', 'z4']
    if (width < 1440) {
      await page.getByRole('button', { name: /trợ lý|mở/i }).click()
    }
    for (const zone of zones) {
      await expect(page.locator(`[data-zone="${zone}"]`)).toBeVisible()
    }
    const scroll = await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)
    expect(scroll).toBe(true)
    const icons = page.locator('[data-zone="z1"] [data-track-icon]')
    if (width < 1024) {
      const box = await page.locator('[data-zone="z1"]').boundingBox()
      expect(box?.width).toBeLessThanOrEqual(56)
      await expect(icons).toHaveCount(2)
      const iconBoxes = await icons.evaluateAll((nodes) =>
        nodes.map((node) => {
          const rect = node.getBoundingClientRect()
          return { width: rect.width, height: rect.height }
        }),
      )
      for (const iconBox of iconBoxes) {
        expect(iconBox.width).toBeGreaterThanOrEqual(12)
        expect(iconBox.height).toBeGreaterThanOrEqual(12)
      }
      const labels = await page.locator('[data-zone="z1"] a').evaluateAll((nodes) =>
        nodes.map((node) => node.getAttribute('aria-label') ?? ''),
      )
      expect(labels.filter((label) => label.length > 0)).toHaveLength(2)
    } else {
      await expect(icons).toHaveCount(0)
    }
    if (width === 768) {
      const main = await page.locator('[data-zone="z3"]').boundingBox()
      expect(main?.width ?? 0).toBeGreaterThanOrEqual(712)
    }
    const z1 = await page.locator('[data-zone="z1"]').boundingBox()
    const z3 = await page.locator('[data-zone="z3"]').boundingBox()
    expect(z1).toBeTruthy()
    expect(z3).toBeTruthy()
    expect(Math.abs((z1?.y ?? 0) - (z3?.y ?? 0))).toBeLessThan(8)
    expect((z1?.x ?? 0) + (z1?.width ?? 0)).toBeLessThanOrEqual((z3?.x ?? 0) + 1)
  })
}
