export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // 當網址為 /api/hello 時，由後端 Worker 回傳動態 JSON 資料
    if (url.pathname === "/api/hello") {
      return Response.json({
        ok: true,
        message: "這是來自 Cloudflare Worker 邊緣運算的即時回應！",
        serverTime: new Date().toISOString(),
        colo: request.cf?.colo || "Local"
      });
    }

    // 其他路徑自動回傳 public 資料夾中的前端網頁
    return env.ASSETS.fetch(request);
  }
};