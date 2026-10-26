import click
from openai import OpenAI

from assistant import Assistant
from tools.registry import get_tools


@click.group()
@click.version_option(version="0.1.0", prog_name="agent2")
def cli():
    """ИИ-агент для работы с файловой системой"""
    pass


@cli.command()
@click.option("--model", "-m", default="qwen3.5:4b", help="Модель LLM")
@click.option("--base-url", "-u", default="http://localhost:11434/v1", help="URL Ollama API")
@click.option("--api-key", "-k", default="ollama", help="API ключ")
@click.option("--interactive", "-i", is_flag=True, help="Интерактивный режим")
@click.option("--message", "-msg", help="Сообщение для отправки")
@click.option("--tools", "-t", default="read_file,write_file,list_directory,search_in_file", help="Комма-разделённый список инструментов")
def chat(model, base_url, api_key, interactive, message, tools):
    """Запустить чат с ИИ-агентом"""
    client = OpenAI(
        base_url=base_url,
        api_key=api_key
    )

    instructions = """
Ты — ИИ-агент.

1. Отвечай на русском языке, коротко, без markdown и emoji.
2. ВСЕГДА используй доступные инструменты для получения информации.
3. Никогда не выдумывай содержимое файлов или путей.
4. Выдавай только финальный ответ, без пояснений.

"""

    tool_list = [t.strip() for t in tools.split(",")]
    tool_instances, functions = get_tools(tool_list)

    assistant = Assistant(
        client=client,
        model=model,
        instructions=instructions,
        tools=tool_instances,
        functions=functions,
    )

    if interactive:
        click.echo("Интерактивный режим. Введите 'quit' или 'exit' для выхода.")
        while True:
            try:
                user_input = click.prompt("Вы", type=str)
            except (EOFError, KeyboardInterrupt):
                click.echo()
                break

            if user_input.lower() in ("quit", "exit"):
                break

            if not user_input.strip():
                continue

            response = assistant(user_input)
            click.echo(f"Агент: {response}")

    elif message:
        response = assistant(message)
        click.echo(response)

    else:
        click.echo("Для отправки сообщения используйте --message или запустите в интерактивном режиме с --interactive", err=True)
        click.echo("Используйте --help для справки.", err=True)
        raise SystemExit(1)


@cli.command()
@click.option("--base-url", "-u", default="http://localhost:11434/v1", help="URL Ollama API")
@click.option("--api-key", "-k", default="ollama", help="API ключ")
def ping(base_url, api_key):
    """Проверить соединение с Ollama"""
    client = OpenAI(base_url=base_url, api_key=api_key)
    try:
        models = client.models.list()
        model_names = [m.id for m in models.data]
        click.echo(f"Ollama доступен. Доступные модели: {', '.join(model_names)}")
    except Exception as e:
        click.echo(f"Ошибка подключения: {e}", err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
