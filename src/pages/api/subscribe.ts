import { env } from "cloudflare:workers";

export const prerender = false;

export async function POST({ request }) {
  try {
    const { email } = await request.json();

    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return new Response(JSON.stringify({ ok: false, error: "Invalid email" }), { status: 400 });
    }

    console.log("API key loaded:", Boolean(env.BUTTONDOWN_API_KEY));
    console.log("API key length:", env.BUTTONDOWN_API_KEY ? env.BUTTONDOWN_API_KEY.length : 0);
    const API_KEY = env.BUTTONDOWN_API_KEY;

    if (!API_KEY) {
      return new Response(JSON.stringify({ ok: false, error: "API key not configured" }), { status: 500 });
    }

    const res = await fetch("https://api.buttondown.email/v1/subscribers", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Token ${API_KEY}`
      },
      body: JSON.stringify({ email_address: email })
    });

    const errBody = await res.json().catch(() => ({}));
    if (!res.ok) {
      const errDetail = Array.isArray(errBody) ? errBody[0]?.detail : (errBody as any).detail;
      return new Response(JSON.stringify({ ok: false, error: errDetail || JSON.stringify(errBody) }), { status: 500 });
    }

    return new Response(JSON.stringify({ ok: true }));
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    console.error("Subscribe error:", msg);
    return new Response(JSON.stringify({ ok: false, error: msg }), { status: 500 });
  }
}
