import { env } from "cloudflare:workers";

export const prerender = false;

export async function POST({ request }) {
  const { email } = await request.json();

  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return new Response(JSON.stringify({ ok: false, error: "Invalid email" }), { status: 400 });
  }

  console.log("Available env keys:", Object.keys(env));
  console.log("API key loaded:", Boolean(env.BUTTONDOWN_API_KEY));
  const API_KEY = env.BUTTONDOWN_API_KEY;

  const res = await fetch("https://api.buttondown.email/v1/subscribers", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Token ${API_KEY}`
    },
    body: JSON.stringify({ email: email })
  });

  const errBody = await res.json().catch(() => ({}));
  if (!res.ok) {
    return new Response(JSON.stringify({ ok: false, error: errBody.detail || "Buttondown error" }), { status: 500 });
  }

  return new Response(JSON.stringify({ ok: true }));
}
