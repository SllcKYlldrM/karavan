type ContactEnv = {
  CONTACT_TO?: string;
  CONTACT_FROM?: string;
  RESEND_API_KEY?: string;
  TURNSTILE_SECRET_KEY?: string;
};

type PagesContext = {
  request: Request;
  env: ContactEnv;
};

const json = (body: Record<string, string>, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8" },
  });

export const onRequestPost = async ({ request, env }: PagesContext) => {
  if (!env.CONTACT_TO || !env.CONTACT_FROM || !env.RESEND_API_KEY || !env.TURNSTILE_SECRET_KEY) {
    return json({ message: "The contact service is not configured yet." }, 503);
  }

  const contentType = request.headers.get("content-type") ?? "";
  if (!contentType.includes("multipart/form-data") && !contentType.includes("application/x-www-form-urlencoded")) {
    return json({ message: "Invalid form submission." }, 415);
  }

  const form = await request.formData();
  const name = String(form.get("name") ?? "").trim();
  const email = String(form.get("email") ?? "").trim();
  const subject = String(form.get("subject") ?? "").trim();
  const message = String(form.get("message") ?? "").trim();
  const website = String(form.get("website") ?? "").trim();
  const turnstileToken = String(form.get("cf-turnstile-response") ?? "").trim();

  if (website) return json({ message: "Your message has been received." });

  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (name.length < 2 || name.length > 100 || !emailPattern.test(email) || subject.length > 160 || message.length < 20 || message.length > 5000) {
    return json({ message: "Please check the form fields and try again." }, 400);
  }

  const turnstileResponse = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      secret: env.TURNSTILE_SECRET_KEY,
      response: turnstileToken,
      remoteip: request.headers.get("CF-Connecting-IP"),
    }),
  });
  const turnstileResult = (await turnstileResponse.json()) as { success?: boolean };
  if (!turnstileResult.success) return json({ message: "Please complete the spam protection check." }, 400);

  const resendResponse = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
      "content-type": "application/json",
    },
    body: JSON.stringify({
      from: env.CONTACT_FROM,
      to: [env.CONTACT_TO],
      reply_to: email,
      subject: subject || `VanSpecs contact message from ${name}`,
      text: `Name: ${name}\nEmail: ${email}\n\n${message}`,
    }),
  });

  if (!resendResponse.ok) return json({ message: "The message could not be sent. Please try again later." }, 502);
  return json({ message: "Your message has been sent. Thank you for contacting VanSpecs." });
};
