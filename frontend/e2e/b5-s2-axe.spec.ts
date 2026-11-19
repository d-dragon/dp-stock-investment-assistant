import AxeBuilder from '@axe-core/playwright'
import { expect, test } from '@playwright/test'

const widths = [1920, 1440, 1024, 768]

for (const width of widths) {
  test(`shell axe at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 })
    await page.goto('/')
    await expect(page.locator('html')).toHaveAttribute('data-mocks', 'on')
    if (width < 1440) {
      await page.getByRole('button', { name: /trợ lý|mở/i }).click()
    }
    const results = await new AxeBuilder({ page }).analyze()
    const blocking = results.violations.filter((item) => item.impact === 'serious' || item.impact === 'critical')
    expect(blocking).toEqual([])
  })
}
