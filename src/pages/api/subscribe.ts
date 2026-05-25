// Cloudflare Pages redeploy trigger
export const prerender = false;

export async function POST({ request }) {
  const { email } = await request.json();

  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return new Response(JSON.stringify({ ok: false, error: "Invalid email" }), { status: 400 });
  }

  const API_KEY = import.meta.env.BUTTONDOWN_API_KEY;

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
    return new Response(JSON.stringify({ ok: false, error: errBody.detail || "Buttondown error" }), { status: 500 });
  }

  return new Response(JSON.stringify({ ok: true }));
}
