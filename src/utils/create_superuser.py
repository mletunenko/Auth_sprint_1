import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import typer
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from core.config import settings
from models.user import Role, User

app = typer.Typer()


# Асинхронная команда для создания суперпользователя
@app.command()
def create_superuser(
    email: str = typer.Option(..., prompt=True, help="Email пользователя"),
    password: str = typer.Option(..., prompt=True, hide_input=True, help="Пароль пользователя"),
):
    """
    Создать суперпользователя с привязанной ролью 'superuser'.
    """
    engine = create_engine(url=str(settings.db.sync_url))
    sess_maker = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    with sess_maker() as session:
        # Проверка, существует ли роль 'superuser'
        role = session.execute(select(Role).where(Role.title == "superuser"))
        role = role.scalars().first()
        if not role:
            role = Role(title="superuser", system_role=True)  # Add other required fields if necessary
            session.add(role)
            session.commit()
            session.refresh(role)

        # Проверка, существует ли пользователь с таким email
        existing_user = session.execute(select(User).where(User.email == email))
        existing_user = existing_user.scalars().first()
        if not existing_user:
            user = User(email=email, role_id=role.id)
            user.set_password(password)
            session.add(user)
            session.commit()
        elif existing_user.role_id is None:
            existing_user.role_id = role.id
            session.commit()

        typer.echo(f"Суперпользователь {email} успешно создан.")


if __name__ == "__main__":
    app()
