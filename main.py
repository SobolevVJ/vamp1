from pyrogram import Client, filters
from rich.console import Console
from rich.progress import Progress
from rich import print
import asyncio
import re
from colorama import init, Fore

api_id = 'id'
api_hash = 'hash'
phone_number = "+phone"
message = "ENDWAY РУЛИТ!"

app = Client("my_account", api_id=api_id, api_hash=api_hash, phone_number=phone_number)
console = Console()

auto_reply_message = "ENDWAY РУЛИТ!"

@app.on_message(filters.private & ~filters.me)
def handle_private_message(client, message):
    message.reply_text(auto_reply_message)

async def send_messages(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
    except FileNotFoundError:
        console.print(f"[red]Файл '{file_path}' не найден[/red]")
        return
    
    total_users = len(lines)
    
    with Progress() as progress:
        task = progress.add_task("[green]Отправка сообщений...", total=total_users)
        for line in lines:
            user_id = line.split(",")[0].split(":")[1].strip()
            username = line.split(",")[2].split(":")[1].strip()
            
            if username == "No username":
                console.print(f"[yellow]Пользователь (ID: {user_id}) пропущен, так как у него нет имени пользователя[/yellow]")
                progress.update(task, advance=1)
                continue
            
            if "bot" in username:
                console.print(f"[yellow]Пользователь (ID: {user_id}) пропущен, так как он является ботом[/yellow]")
                progress.update(task, advance=1)
                continue
            
            try:
                await app.send_message(chat_id=username, text=message)
                console.print(f"[green]Пользователю (ID: {user_id}) отправил сообщение[/green]")
            except Exception as e:
                console.print(f"[red]Пользователю (ID: {user_id}) не отправилось сообщение, причина: {e}[/red]")
            progress.update(task, advance=1)
            await asyncio.sleep(2) 

async def get_chat_members(chat_username):
    total_members = 0
    async for member in app.get_chat_members(chat_username):
        total_members += 1
    
    members = []
    with Progress() as progress:
        task = progress.add_task("[green]Начинаю собирать список участников...", total=total_members)
        async for member in app.get_chat_members(chat_username):
            full_name = f"{member.user.first_name or ''} {member.user.last_name or ''}".strip()
            username = f"@{member.user.username}" if member.user.username else "No username"
            members.append({
                "user_id": member.user.id,
                "full_name": full_name,
                "username": username,
            })
            progress.update(task, advance=1, description=f"[green]Начинаю собирать список участников ({len(members)}/{total_members})")
    
    with open("parsing.txt", "w", encoding="utf-8") as file:
        for member in members:
            file.write(f"User ID: {member['user_id']}, Full Name: {member['full_name']}, Username: {member['username']}\n")

async def invite_members(chat_id, file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
    except FileNotFoundError:
        console.print(f"[red]Файл '{file_path}' не найден[/red]")
        return
    
    total_users = len(lines)
    
    with Progress() as progress:
        task = progress.add_task("[green]Приглашение пользователей...", total=total_users)
        for line in lines:
            username = line.split(",")[2].split(":")[1].strip()
            
            if username == "No username":
                console.print(f"[yellow]Пользователь пропущен, так как у него нет имени пользователя[/yellow]")
                progress.update(task, advance=1)
                continue
            
            if "bot" in username:
                console.print(f"[yellow]Пользователь (username: {username}) пропущен, так как он является ботом[/yellow]")
                progress.update(task, advance=1)
                continue
            
            try:
                await app.add_chat_members(chat_id, username)
                console.print(f"[green]Пользователь (username: {username}) приглашен в чат[/green]")
            except Exception as e:
                console.print(f"[red]Пользователя (username: {username}) не удалось пригласить, причина: {e}[/red]")
            progress.update(task, advance=1)
            await asyncio.sleep(2)  

async def report():
    console.print("\n[bold]Выберите тип репорта:[/bold]")
    console.print("1. Пост в канале")
    console.print("2. Пользователь")
    console.print("3. Бот")
    console.print("4. Канал")
    report_type = console.input("Введите номер действия: ")

    if report_type == "1":
        post_link = console.input("Введите ссылку на пост в канале: ")
        comment = console.input("Введите комментарий к жалобе (необязательно): ")
        await report_post(post_link, comment)
    elif report_type == "2":
        user_id = console.input("Введите ID или юзернейм пользователя: ")
        comment = console.input("Введите комментарий к жалобе (необязательно): ")
        await report_user(user_id, comment)
    elif report_type == "3":
        bot_username = console.input("Введите юзернейм бота: ")
        comment = console.input("Введите комментарий к жалобе (необязательно): ")
        await report_bot(bot_username, comment)
    elif report_type == "4":
        channel_username = console.input("Введите юзернейм канала: ")
        comment = console.input("Введите комментарий к жалобе (необязательно): ")
        await report_channel(channel_username, comment)
    else:
        console.print("[red]Неверный выбор[/red]")

async def report_post(post_link, comment):
    console.print(f"[green]Жалоба на пост '{post_link}' отправлена. Комментарий: {comment}[/green]")

async def report_user(user_id, comment):
    console.print(f"[green]Жалоба на пользователя '{user_id}' отправлена. Комментарий: {comment}[/green]")

async def report_bot(bot_username, comment):
    console.print(f"[green]Жалоба на бота '{bot_username}' отправлена. Комментарий: {comment}[/green]")

async def report_channel(channel_username, comment):
    console.print(f"[green]Жалоба на канал '{channel_username}' отправлена. Комментарий: {comment}[/green]")

async def get_commenters(post_link):
    try:
        chat_id, message_id = parse_post_link(post_link)

        members = []
        total_comments = 0
        async for message in app.get_discussion_replies(chat_id, message_id):
            total_comments += 1
            user = message.from_user
            if user:
                full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
                username = f"@{user.username}" if user.username else "No username"
                members.append({
                    "user_id": user.id,
                    "full_name": full_name,
                    "username": username,
                })

        with Progress() as progress:
            task = progress.add_task("[green]Сбор пользователей из комментариев...", total=total_comments)
            for _ in range(total_comments):
                progress.update(task, advance=1)
        
        with open("commenters.txt", "w", encoding="utf-8") as file:
            for member in members:
                file.write(f"User ID: {member['user_id']}, Full Name: {member['full_name']}, Username: {member['username']}\n")
        
        console.print(f"[green]Список пользователей из комментариев сохранен в 'commenters.txt'[/green]")
    except Exception as e:
        console.print(f"[red]Ошибка при парсинге пользователей: {e}[/red]")

def parse_post_link(post_link):
    try:
        parts = post_link.split("/")
        chat_id = parts[-2]
        message_id = int(parts[-1])
        if not chat_id.startswith("@"):
            chat_id = f"@{chat_id}"
        return chat_id, message_id
    except Exception as e:
        console.print(f"[red]Неверный формат ссылки на пост: {e}[/red]")
        raise ValueError("Неверный формат ссылки на пост")

def read_groups_from_file(file_path):
    with open(file_path, "r") as file:
        lines = file.read().splitlines()
    groups = []
    for line in lines:
        match = re.search(r't.me/(\w+)', line)
        if match:
            groups.append(match.group(1))
        else:
            groups.append(line)
    return groups

async def spam_to_groups(groups, message):
    total_groups = len(groups)
    with Progress() as progress:
        task = progress.add_task("[green]Отправка сообщений в группы...", total=total_groups)
        for group in groups:
            try:
                await app.send_message(group, message)
                console.print(f"[green]Сообщение отправлено в {group}")
            except Exception as e:
                if "CHAT_WRITE_FORBIDDEN" in str(e):
                    error_message = "Вы не находитесь в чате"
                else:
                    error_message = str(e)
                console.print(f"[red]Сообщение не было доставлено в группу {group}: {error_message}")
            progress.update(task, advance=1)
            await asyncio.sleep(2)

async def spam_to_single_group(group, message):
    try:
        await app.send_message(group, message)
        console.print(f"[green]Сообщение отправлено в {group}")
    except Exception as e:
        if "CHAT_WRITE_FORBIDDEN" in str(e):
            error_message = "Вы не находитесь в чате"
        else:
            error_message = str(e)
        console.print(f"[red]Сообщение не было доставлено в группу {group}: {error_message}")

async def run_auto_reply():
    console.print("[bold green]Автоответчик включен. Бот будет автоматически отвечать на личные сообщения.[/bold green]")
    await app.idle()

#ENDWAY

async def main():
    auto_reply_task = None
    await app.start()
    while True:
        console.print("\n[bold]Выберите действие:[/bold]")
        console.print("1. Спам по личкам")
        console.print("2. Парсинг пользователей из чата")
        console.print("3. Инвайт пользователей в чат")
        console.print("4. Отправить репорт")
        console.print("5. Парсинг пользователей из комментариев")
        console.print("6. Автоответчик")
        console.print("7. Спам по чатам")
        console.print("8. Выход")
        choice = console.input("Введите номер действия: ")

        if choice == "1":
            file_path = console.input("Введите путь и название файла с данными для спама: ")
            await send_messages(file_path)
        elif choice == "2":
            chat_username = console.input("Введите юзернейм группы (с @): ")
            await get_chat_members(chat_username)
        elif choice == "3":
            chat_id = console.input("Введите юзернейм группы для инвайта (с @): ")
            file_path = console.input("Введите путь и название файла с данными для инвайта: ")
            await invite_members(chat_id, file_path)
        elif choice == "4":
            await report()
        elif choice == "5":
            post_link = console.input("Введите ссылку на пост в канале (с обсуждением): ")
            await get_commenters(post_link)
        elif choice == "6":
            if auto_reply_task is None or auto_reply_task.done():
                auto_reply_task = asyncio.create_task(run_auto_reply())
            else:
                console.print("[bold yellow]Автоответчик уже запущен.[/bold yellow]")
        elif choice == "7":
            console.print("ENDWAY 1. Спам по чатам из файла")
            console.print("ENDWAY 2. Спам по одному чату")
            spam_choice = console.input("Введите номер действия: ")
            message = console.input("Введите сообщение для спама: ")
            if spam_choice == "1":
                file_path = console.input("Введите путь и название файла с группами: ")
                groups = read_groups_from_file(file_path)
                await spam_to_groups(groups, message)
            elif spam_choice == "2":
                group = console.input("Введите юзернейм группы (с @): ")
                await spam_to_single_group(group, message)
            else:
                console.print("[red]Неверный выбор[/red]")
        elif choice == "8":
            console.print("[bold]Выход из программы[/bold]")
            await app.stop()
            break
        else:
            console.print("[red]Неверный выбор[/red]")

if __name__ == "__main__":
    asyncio.run(main())
