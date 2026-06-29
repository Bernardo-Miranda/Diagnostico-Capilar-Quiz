const SUPABASE_URL = 'https://aqqhyeipxzbjdkgerxow.supabase.co';
const SUPABASE_KEY = 'sb_publishable_vCMA8DWK6KuHFOOJ5NVbMQ_9OSEG2Q2';

function getExpectedToken() {
  return process.env.LOWIFY_WEBHOOK_TOKEN || 'UM_TOKEN_SECRETO';
}

function getReceivedToken(req) {
  const queryToken = req.query?.token;
  const headerToken = req.headers['x-webhook-token'];
  const authorization = req.headers.authorization || '';

  if (Array.isArray(queryToken)) return queryToken[0];
  if (queryToken) return queryToken;
  if (Array.isArray(headerToken)) return headerToken[0];
  if (headerToken) return headerToken;
  if (authorization.toLowerCase().startsWith('bearer ')) {
    return authorization.slice(7).trim();
  }

  return '';
}

function normalizeBody(body) {
  if (!body) return {};
  if (typeof body === 'object') return body;

  try {
    return JSON.parse(body);
  } catch {
    return { raw_body: String(body) };
  }
}

async function saveLowifySale(payload) {
  const response = await fetch(`${SUPABASE_URL}/rest/v1/rpc/save_lowify_sale`, {
    method: 'POST',
    headers: {
      apikey: SUPABASE_KEY,
      Authorization: `Bearer ${SUPABASE_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ payload })
  });

  const text = await response.text();
  let data = null;

  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }

  if (!response.ok) {
    const message = typeof data === 'string' ? data : JSON.stringify(data);
    throw new Error(message || `Supabase error ${response.status}`);
  }

  return data;
}

module.exports = async function handler(req, res) {
  res.setHeader('Content-Type', 'application/json; charset=utf-8');

  if (req.method === 'GET') {
    return res.status(200).json({
      ok: true,
      endpoint: 'webhook-lowify',
      message: 'Endpoint ativo. Use POST para receber eventos da Lowify.'
    });
  }

  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Webhook-Token');
    return res.status(204).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({
      ok: false,
      error: 'Metodo nao permitido. Use POST.'
    });
  }

  const expectedToken = getExpectedToken();
  const receivedToken = getReceivedToken(req);

  if (!expectedToken || receivedToken !== expectedToken) {
    return res.status(401).json({
      ok: false,
      error: 'Token invalido.'
    });
  }

  const payload = normalizeBody(req.body);

  try {
    const result = await saveLowifySale(payload);

    return res.status(200).json({
      ok: true,
      saved: result
    });
  } catch (error) {
    console.error('Erro ao salvar webhook Lowify:', error);

    return res.status(500).json({
      ok: false,
      error: 'Erro ao salvar webhook no Supabase.'
    });
  }
};
