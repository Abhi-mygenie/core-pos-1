# BUG-671 / BUG-685 helper: login to cafe103 preprod and land on dashboard
async def login(page):
    await page.wait_for_selector('[data-testid="login-email"]', timeout=20000)
    await page.fill('[data-testid="login-email"]', "owner@cafe103.com")
    await page.fill('[data-testid="login-password"]', "Qplazm@10")
    await page.click('[data-testid="login-button"]')
    await page.wait_for_url("**/dashboard**", timeout=90000)
    await page.wait_for_timeout(3000)
