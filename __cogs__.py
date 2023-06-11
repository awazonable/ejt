extensions = {
    'voice',
    'translate',
    'utility',
}

async def setup(bot):
    for ext in extensions:
        await bot.load_extension(ext)

async def teardown(bot):
    for ext in extensions:
        await bot.load_extension(ext)