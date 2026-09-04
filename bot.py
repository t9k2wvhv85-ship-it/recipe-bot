import json
import logging
import os
from pathlib import Path

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

RECIPES_PATH = Path(__file__).parent / "recipes.json"


def load_recipes():
    with open(RECIPES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


RECIPES = load_recipes()


def find_recipes_by_ingredient(query: str):
    query = query.strip().lower()
    if not query:
        return []
    results = []
    for recipe in RECIPES:
        ingredients_lower = [i.lower() for i in recipe["ingredients"]]
        if any(query in ing for ing in ingredients_lower):
            results.append(recipe)
    return results


def format_recipe(recipe: dict) -> str:
    ingredients = "\n".join(f"• {i}" for i in recipe["ingredients"])
    return (
        f"🍽 <b>{recipe['name']}</b>\n\n"
        f"⏱ Время: {recipe.get('time', '—')}\n"
        f"🍴 Порции: {recipe.get('servings', '—')}\n\n"
        f"<b>Ингредиенты:</b>\n{ingredients}\n\n"
        f"<b>Приготовление:</b>\n{recipe['instructions']}"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я помогу найти рецепт по ингредиенту.\n\n"
        "Просто напиши название продукта (например: курица, лосось, картофель), "
        "и я покажу подходящие рецепты.\n\n"
        "Команда /help — подробнее."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Напиши название ингредиента текстом — я найду рецепты, где он используется.\n\n"
        "Команды:\n"
        "/start — начать\n"
        "/help — помощь\n"
        "/count — сколько рецептов в базе\n\n"
        "Совет: если ничего не находится, попробуй единственное число "
        "(«помидор» вместо «помидоры»)."
    )


async def count_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"В базе {len(RECIPES)} рецептов.")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    matches = find_recipes_by_ingredient(query)

    if not matches:
        await update.message.reply_text(
            f"Не нашёл рецептов с «{query}». Попробуй другое название "
            "(например, в единственном числе)."
        )
        return

    if len(matches) == 1:
        await update.message.reply_text(format_recipe(matches[0]), parse_mode="HTML")
        return

    buttons = [
        [InlineKeyboardButton(r["name"], callback_data=f"recipe:{r['id']}")]
        for r in matches
    ]
    await update.message.reply_text(
        f"Нашёл {len(matches)} рецептов с «{query}»:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    recipe_id = query.data.split(":", 1)[1]
    recipe = next((r for r in RECIPES if str(r["id"]) == recipe_id), None)
    if recipe:
        await query.message.reply_text(format_recipe(recipe), parse_mode="HTML")
    else:
        await query.message.reply_text("Рецепт не найден, попробуй ещё раз.")


def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "Не задан токен бота. Установи переменную окружения BOT_TOKEN "
            "(см. README.md)."
        )

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("count", count_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(handle_callback))

    logger.info("Бот запущен")
    app.run_polling()


if __name__ == "__main__":
    main()
