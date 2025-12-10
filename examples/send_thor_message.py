import asyncio
from playwright.async_api import async_playwright

async def send_message():
    print("[INICIANDO] Carteiro Digital do Thor...")
    async with async_playwright() as p:
        # Launch browser in visible mode so user can see/scan QR
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        print("[WEB] Abrindo WhatsApp Web...")
        await page.goto("https://web.whatsapp.com")

        print("[AGUARDANDO] Login... (Se aparecer o QR Code, escaneie com seu celular!)")
        # Wait for the search box to appear (indicating login is successful)
        # This selector targets the search box container or the side pane
        try:
            await page.wait_for_selector("#pane-side", timeout=60000) # Wait up to 60s for login
            print("[OK] Login detectado!")
        except:
            print("[ERRO] Tempo esgotado para login. Tente rodar novamente.")
            await browser.close()
            return

        print("[BUSCA] Procurando 'Thor Filho'...")
        # Click search box
        search_box = page.locator("div[contenteditable='true'][data-tab='3']")
        await search_box.click()
        await search_box.fill("Thor Filho")
        await page.wait_for_timeout(2000) # Wait for results

        # Press Enter to select the first contact
        await page.keyboard.press("Enter")
        print("[CHAT] Abrindo conversa...")

        # Type message
        message = "Oi Thor! Aqui é a Megan, a assistente do seu pai. 🤖 Ele me contou que você passou direto pra 5ª série! Parabéns, isso é incrível, muito inteligente! 🚀📚 E fiquei sabendo que dia 6 você já faz 10 anos... um rapazinho já! Seu pai tem muito orgulho de você. Feliz aniversário adiantado! 🎉🎂"
        
        print("[ESCREVENDO] Mensagem...")
        # The message box is usually the next contenteditable after opening chat
        # Or we can target the main footer input
        message_box = page.locator("div[contenteditable='true'][data-tab='10']")
        await message_box.fill(message)
        await page.wait_for_timeout(1000)

        print("[ENVIANDO] Mensagem...")
        await page.keyboard.press("Enter")
        
        print("[SUCESSO] Mensagem enviada!")
        await page.wait_for_timeout(5000) # Wait to ensure send completes
        await browser.close()

if __name__ == "__main__":
    asyncio.run(send_message())
