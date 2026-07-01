const SUPABASE_URL = 'https://aqqhyeipxzbjdkgerxow.supabase.co';
const SUPABASE_KEY = 'sb_publishable_vCMA8DWK6KuHFOOJ5NVbMQ_9OSEG2Q2';

function getExpectedToken() {
  return process.env.PINPAY_WEBHOOK_TOKEN || process.env.LOWIFY_WEBHOOK_TOKEN || 'UM_TOKEN_SECRETO';
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

function readPath(source, paths) {
  for (const path of paths) {
    const value = path.split('.').reduce((current, key) => {
      if (current === null || current === undefined) return undefined;
      return current[key];
    }, source);

    if (value !== null && value !== undefined && value !== '') return value;
  }

  return null;
}

function normalizeAmount(value) {
  if (value === null || value === undefined || value === '') return null;

  if (typeof value === 'number') {
    return value >= 1000 ? value / 100 : value;
  }

  const cleaned = String(value)
    .replace(/[^\d,.-]/g, '')
    .replace(/\./g, '')
    .replace(',', '.');

  const number = Number(cleaned);
  if (!Number.isFinite(number)) return null;

  return number >= 1000 ? number / 100 : number;
}

function normalizeStatus(rawEvent, rawStatus) {
  const text = `${rawEvent || ''} ${rawStatus || ''}`
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '');

  if (text.includes('aprov') || text.includes('paid') || text.includes('pix recebido') || text.includes('received')) {
    return 'sale.paid';
  }

  if (text.includes('pendent') || text.includes('pending') || text.includes('waiting') || text.includes('pix') || text.includes('aguard')) {
    return 'sale.pending';
  }

  if (text.includes('estorn') || text.includes('refund') || text.includes('reembols') || text.includes('chargeback')) {
    return 'sale.refund';
  }

  if (text.includes('recus') || text.includes('reject') || text.includes('declin') || text.includes('cancel')) {
    return 'sale.refused';
  }

  return rawEvent || rawStatus || 'pinpay.unknown';
}

function normalizePinpayPayload(payload) {
  const rawEvent = readPath(payload, ['event', 'event_name', 'type', 'name', 'evento']);
  const rawStatus = readPath(payload, [
    'status',
    'payment.status',
    'transaction.status',
    'data.status',
    'data.payment.status',
    'data.transaction.status',
    'sale.status'
  ]);

  const amount = normalizeAmount(readPath(payload, [
    'amount_total',
    'amount',
    'total',
    'value',
    'price',
    'payment.amount',
    'payment.total',
    'transaction.amount',
    'transaction.total',
    'data.amount',
    'data.total',
    'data.value',
    'data.payment.amount',
    'data.transaction.amount',
    'sale.amount',
    'sale.total'
  ]));

  const saleId = readPath(payload, [
    'sale_id',
    'id',
    'order_id',
    'transaction_id',
    'payment_id',
    'payment.id',
    'transaction.id',
    'order.id',
    'data.id',
    'data.sale_id',
    'data.order_id',
    'data.transaction_id',
    'data.payment.id',
    'data.transaction.id',
    'sale.id'
  ]);

  const productId = readPath(payload, ['product.id', 'product_id', 'data.product.id', 'data.product_id', 'item.id']);
  const productName = readPath(payload, ['product.name', 'product_name', 'data.product.name', 'data.product_name', 'item.name']);

  const customerName = readPath(payload, ['customer.name', 'customer_name', 'client.name', 'buyer.name', 'data.customer.name', 'data.client.name', 'data.buyer.name']);
  const customerEmail = readPath(payload, ['customer.email', 'customer_email', 'client.email', 'buyer.email', 'data.customer.email', 'data.client.email', 'data.buyer.email']);
  const customerPhone = readPath(payload, ['customer.phone', 'customer_phone', 'client.phone', 'buyer.phone', 'data.customer.phone', 'data.client.phone', 'data.buyer.phone']);

  const tracking = {
    click_id: readPath(payload, ['tracking.click_id', 'click_id', 'data.tracking.click_id', 'data.click_id', 'utm.click_id']),
    campaign_id: readPath(payload, ['tracking.campaign_id', 'campaign_id', 'data.tracking.campaign_id', 'data.campaign_id', 'utm.campaign_id']),
    utm_source: readPath(payload, ['tracking.utm_source', 'utm_source', 'data.tracking.utm_source', 'data.utm_source', 'utm.source']),
    utm_medium: readPath(payload, ['tracking.utm_medium', 'utm_medium', 'data.tracking.utm_medium', 'data.utm_medium', 'utm.medium']),
    utm_campaign: readPath(payload, ['tracking.utm_campaign', 'utm_campaign', 'data.tracking.utm_campaign', 'data.utm_campaign', 'utm.campaign']),
    utm_content: readPath(payload, ['tracking.utm_content', 'utm_content', 'data.tracking.utm_content', 'data.utm_content', 'utm.content']),
    utm_term: readPath(payload, ['tracking.utm_term', 'utm_term', 'data.tracking.utm_term', 'data.utm_term', 'utm.term']),
    fbclid: readPath(payload, ['tracking.fbclid', 'fbclid', 'data.tracking.fbclid', 'data.fbclid']),
    gclid: readPath(payload, ['tracking.gclid', 'gclid', 'data.tracking.gclid', 'data.gclid'])
  };

  return {
    event: normalizeStatus(rawEvent, rawStatus),
    gateway: 'pinpay',
    sale_id: saleId || undefined,
    timestamp: readPath(payload, ['timestamp', 'created_at', 'paid_at', 'updated_at', 'data.timestamp', 'data.created_at', 'data.paid_at']) || new Date().toISOString(),
    product: {
      id: productId || undefined,
      name: productName || 'Protocolo completo anti queda capilar'
    },
    customer: {
      name: customerName || undefined,
      email: customerEmail || undefined,
      phone: customerPhone || undefined
    },
    amount: amount !== null ? amount.toFixed(2) : undefined,
    currency: readPath(payload, ['currency', 'data.currency']) || 'BRL',
    tracking,
    pinpay_payload: payload
  };
}

async function saveGatewaySale(payload) {
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
      endpoint: 'webhook-pinpay',
      message: 'Endpoint ativo. Use POST para receber eventos da PinPay.'
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
  const normalizedPayload = normalizePinpayPayload(payload);

  try {
    const result = await saveGatewaySale(normalizedPayload);

    return res.status(200).json({
      ok: true,
      saved: result
    });
  } catch (error) {
    console.error('Erro ao salvar webhook PinPay:', error);

    return res.status(500).json({
      ok: false,
      error: 'Erro ao salvar webhook no Supabase.'
    });
  }
};
