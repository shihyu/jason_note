/**
 * GET  /api/messages  → 列出所有留言（D1）
 * POST /api/messages  → 新增一則留言（D1）
 * Binding: DB (D1 Database)
 */

// 確保資料表存在
async function ensureTable(db) {
  await db.prepare(
    "CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, message TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT (datetime('now')))"
  ).run();
}

export async function onRequestGet({ env }) {
  try {
    await ensureTable(env.DB);
    const { results } = await env.DB.prepare(
      'SELECT id, name, message, created_at FROM messages ORDER BY id DESC LIMIT 50'
    ).all();

    return new Response(JSON.stringify({ messages: results }), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}

export async function onRequestPost({ request, env }) {
  try {
    const body = await request.json();
    const name    = (body.name    || '').trim().slice(0, 50);
    const message = (body.message || '').trim().slice(0, 500);

    if (!name || !message) {
      return new Response(JSON.stringify({ error: '名字與留言不可為空' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    await ensureTable(env.DB);
    await env.DB.prepare(
      'INSERT INTO messages (name, message) VALUES (?, ?)'
    ).bind(name, message).run();

    return new Response(JSON.stringify({ success: true }), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}
