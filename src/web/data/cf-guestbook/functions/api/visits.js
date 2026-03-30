/**
 * GET /api/visits
 * 從 KV 讀取訪客計數，每次呼叫自動 +1
 * Binding: VISITS (KV Namespace)
 */
export async function onRequestGet({ env }) {
  const key = 'visit_count';
  const raw = await env.VISITS.get(key);
  const count = raw ? parseInt(raw, 10) + 1 : 1;
  await env.VISITS.put(key, String(count));

  return new Response(JSON.stringify({ count }), {
    headers: { 'Content-Type': 'application/json' },
  });
}
