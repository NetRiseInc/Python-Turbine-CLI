"""Notification resource commands — use api tier for full CRUD."""

from __future__ import annotations

import typer

APP_NAME = "notification"
APP_HELP = "Notification configurations (use `turbine api` for full CRUD)."


def register(app: typer.Typer) -> None:
    app.command("list")(list_notifications)


def list_notifications(ctx: typer.Context) -> None:
    """List notification configurations via API."""
    from ._common import run_graphql_by_name

    run_graphql_by_name(
        ctx,
        method_name="query_list_notification_configurations",
        input_model_name="ListNotificationConfigurationsInput",
        input_param="list_notification_configurations_args",
        payload={"cursor": {"first": 50}},
        risk="read",
    )
