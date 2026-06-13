"""認証・認可まわりの設定。

- Google OAuth (FastMCP `GoogleProvider`) を環境変数から構築する
- 認証済みユーザーのメールドメインを検証し、許可ドメイン以外を拒否する
  Middleware を提供する

Cloud Run などのリモート環境で claude.ai から接続される前提のため、
すべてのアクセスに Google ログイン(OAuth)を必須とし、さらに
`ALLOWED_GOOGLE_DOMAINS` で社内ドメインに限定する。
"""

import os
import logging
from typing import Optional

from fastmcp.server.auth.providers.google import GoogleProvider
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.dependencies import get_access_token
from fastmcp.exceptions import ToolError

logger = logging.getLogger("smarthr-mcp-server.auth")


def build_google_auth() -> Optional[GoogleProvider]:
    """環境変数から GoogleProvider を構築する。

    必要な環境変数:
      - GOOGLE_OAUTH_CLIENT_ID
      - GOOGLE_OAUTH_CLIENT_SECRET
      - PUBLIC_BASE_URL        … 例: https://xxx.a.run.app (末尾スラッシュなし)

    認証を無効化したい場合(ローカル疎通確認など)は環境変数
    DISABLE_AUTH=1 を設定する。
    """
    if os.getenv("DISABLE_AUTH") == "1":
        logger.warning("DISABLE_AUTH=1 が設定されています。認証なしで起動します。")
        return None

    client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
    base_url = os.getenv("PUBLIC_BASE_URL")

    missing = [
        name
        for name, value in {
            "GOOGLE_OAUTH_CLIENT_ID": client_id,
            "GOOGLE_OAUTH_CLIENT_SECRET": client_secret,
            "PUBLIC_BASE_URL": base_url,
        }.items()
        if not value
    ]
    if missing:
        raise ValueError(
            "Google OAuth に必要な環境変数が未設定です: " + ", ".join(missing)
        )

    return GoogleProvider(
        client_id=client_id,
        client_secret=client_secret,
        base_url=base_url.rstrip("/"),
        required_scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
        ],
    )


def _csv_env(name: str) -> list[str]:
    raw = os.getenv(name, "")
    return [v.strip().lower() for v in raw.split(",") if v.strip()]


class DomainRestrictionMiddleware(Middleware):
    """認証済みユーザーのメール/ドメインを検証する Middleware。

    許可判定 (どちらか一致で許可):
      - `ALLOWED_GOOGLE_EMAILS` (カンマ区切り) … 完全一致するメールアドレス
      - `ALLOWED_GOOGLE_DOMAINS` (カンマ区切り) … 一致するメールドメイン

    特定メンバーのみに限定したい場合は `ALLOWED_GOOGLE_EMAILS` だけを設定し、
    `ALLOWED_GOOGLE_DOMAINS` は空にする。
    両方未設定なら制限しない(警告)。
    """

    def __init__(self) -> None:
        self.allowed_emails = _csv_env("ALLOWED_GOOGLE_EMAILS")
        self.allowed_domains = _csv_env("ALLOWED_GOOGLE_DOMAINS")
        if self.allowed_emails:
            logger.info("許可メール: %s", ", ".join(self.allowed_emails))
        if self.allowed_domains:
            logger.info("許可ドメイン: %s", ", ".join(self.allowed_domains))
        if not self.allowed_emails and not self.allowed_domains:
            logger.warning(
                "ALLOWED_GOOGLE_EMAILS / ALLOWED_GOOGLE_DOMAINS が未設定です。"
                "アクセス制限は無効です。"
            )

    def _assert_allowed(self) -> None:
        if not self.allowed_emails and not self.allowed_domains:
            return
        try:
            token = get_access_token()
        except Exception:
            token = None
        if token is None:
            # 認証プロバイダが無効(DISABLE_AUTH)の場合はトークンが無い
            if os.getenv("DISABLE_AUTH") == "1":
                return
            raise ToolError("認証が必要です。")

        email = (token.claims or {}).get("email", "").lower()
        hd = (token.claims or {}).get("hd", "").lower()
        email_domain = email.split("@")[-1] if "@" in email else ""

        if email and email in self.allowed_emails:
            return
        if email_domain and email_domain in self.allowed_domains:
            return
        if hd and hd in self.allowed_domains:
            return

        logger.warning("アクセス拒否: email=%s hd=%s", email, hd)
        raise ToolError("このアカウントではアクセスが許可されていません。")

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        self._assert_allowed()
        return await call_next(context)

    async def on_read_resource(self, context: MiddlewareContext, call_next):
        self._assert_allowed()
        return await call_next(context)
