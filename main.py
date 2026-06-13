import os

from smarthr_mcp_server.server import mcp

if __name__ == "__main__":
    # Cloud Run は $PORT (既定 8080) での待ち受けを要求する。
    # claude.ai のリモートコネクタは streamable-HTTP で接続する。
    port = int(os.environ.get("PORT", "8080"))
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=port,
    )
