import { expect, test } from '@playwright/test'

test('draft survives reload and clears on send', async ({ page }) => {
  await page.setViewportSize({ width: 1920, height: 1080 })
  await page.goto('/')
  await expect(page.locator('html')).toHaveAttribute('data-mocks', 'on')
  const box = page.getByRole('textbox')
  await box.fill('FPT')
  await page.reload()
  await expect(box).toHaveValue('FPT')
  await page.getByRole('button', { name: 'Gửi' }).click()
  await expect(box).toHaveValue('')
})
