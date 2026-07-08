"""User resource commands."""

from __future__ import annotations

from typing import Optional

import typer

from ._common import FILTER_HELP, run_graphql_by_name, run_list

APP_NAME = "user"
APP_HELP = "Organization users."


def register(app: typer.Typer) -> None:
    app.command("list")(list_users)
    app.command("invite")(invite_user)
    app.command("delete")(delete_user)
    app.command("remove")(remove_user)


def list_users(
    ctx: typer.Context,
    filter_json: Optional[str] = typer.Option(None, "--filter", help=FILTER_HELP),
    limit: int = typer.Option(100, "--limit"),
    after: Optional[str] = typer.Option(None, "--after", help="Resume after this cursor."),
    fields: Optional[str] = typer.Option(None, "--fields", help="Comma-separated dot-path projection, e.g. id,name,risk.score."),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """List organization users."""
    run_list(
        ctx,
        method_name="iter_users",
        filter_json=filter_json,
        limit=limit,
        after=after,
        fields=fields,
        dry_run=dry_run,
    )


def invite_user(
    ctx: typer.Context,
    email: str = typer.Option(..., "--email"),
    role: str = typer.Option(..., "--role"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    yes: bool = typer.Option(False, "--yes"),
) -> None:
    """Invite a user to the organization."""
    run_graphql_by_name(
        ctx,
        method_name="mutation_user_invite",
        input_model_name="InviteUserInput",
        input_param="user_invite_args",
        payload={"email": email, "role": role},
        risk="write",
        dry_run=dry_run,
        yes=yes,
    )


def delete_user(
    ctx: typer.Context,
    user_id: str = typer.Argument(..., help="User ID."),
    dry_run: bool = typer.Option(False, "--dry-run"),
    yes: bool = typer.Option(False, "--yes"),
) -> None:
    """Delete a user."""
    run_graphql_by_name(
        ctx,
        method_name="mutation_user_delete",
        input_model_name="UserInput",
        input_param="user_delete_args",
        payload={"id": user_id},
        risk="destructive",
        dry_run=dry_run,
        yes=yes,
    )


def remove_user(
    ctx: typer.Context,
    user_id: str = typer.Argument(..., help="User ID."),
    dry_run: bool = typer.Option(False, "--dry-run"),
    yes: bool = typer.Option(False, "--yes"),
) -> None:
    """Remove a user from the organization."""
    run_graphql_by_name(
        ctx,
        method_name="mutation_user_remove",
        input_model_name="UserInput",
        input_param="user_remove_args",
        payload={"id": user_id},
        risk="destructive",
        dry_run=dry_run,
        yes=yes,
    )
