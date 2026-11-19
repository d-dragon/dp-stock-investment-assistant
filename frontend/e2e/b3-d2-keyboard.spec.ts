import { expect, test } from '@playwright/test'

test('keyboard order at 1920 px', async ({ page }) => {
  await page.setViewportSize({ width: 1920, height: 1080 })
  await page.goto('/')
  await expect(page.locator('html')).toHaveAttribute('data-mocks', 'on')

  await page.keyboard.press('Tab')
  await expect(page.locator(':focus')).toHaveAttribute('href', '#zone-z3')

  const zones: string[] = []
  for (let step = 0; step < 16 && zones.length < 4; step += 1) {
    await page.keyboard.press('Tab')
    const focused = page.locator(':focus')
    const outline = await focused.evaluate((el) => getComputedStyle(el).outlineWidth)
    expect(Number.parseFloat(outline)).toBeGreaterThanOrEqual(2)
    const zone = await focused.evaluate((el) => el.closest('[data-zone]')?.getAttribute('data-zone') ?? '')
    if (zone && zones[zones.length - 1] !== zone) zones.push(zone)
  }

  expect(zones).toEqual(['z2', 'z1', 'z3', 'z4'])
})

test('ArrowRight on a resize handle widens Z1 at 1920 px', async ({ page }) => {
  await page.setViewportSize({ width: 1920, height: 1080 })
  await page.goto('/')
  await expect(page.locator('html')).toHaveAttribute('data-mocks', 'on')

  const before = await page.locator('[data-zone="z1"]').boundingBox()
  await page.getByRole('separator').first().focus()
  await page.keyboard.press('ArrowRight')
  const after = await page.locator('[data-zone="z1"]').boundingBox()

  expect(before).toBeTruthy()
  expect(after).toBeTruthy()
  expect(after?.width ?? 0).toBeGreaterThan((before?.width ?? 0) + 40)
})
