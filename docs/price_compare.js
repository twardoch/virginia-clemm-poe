// this_file: src_docs/md/price_compare.js
// Compare disclosed rates with explicit units. Never infer a points/USD exchange rate.
(function (root) {
    'use strict';
    const finite = value => value !== null && value !== undefined && value !== '' && Number.isFinite(Number(value)) && Number(value) >= 0;
    const number = value => Number(value);

    function ratesFor(model) {
        const details = model.pricing?.scraped?.details || model.pricing?.details || {};
        const rates = details.rates?.length ? [...details.rates] : [];
        // Legacy files are still readable; explicit units and zero values survive.
        for (const [label, value] of Object.entries(details)) {
            if (details.rates?.length) break;
            if (label === 'rate_card' || label === 'rates' || /discount/i.test(label)) continue;
            for (const text of (Array.isArray(value) ? value : [value])) {
                if (typeof text !== 'string') continue;
                const unitMatch = text.match(/\/\s*(?:(\d+(?:\.\d+)?)([kKmM])?\s*)?(tokens?|images?|messages?|megapixels?|seconds?|minutes?|characters?)/);
                const quantity = unitMatch ? Number(unitMatch[1] || 1) * ({k: 1000, m: 1e6}[unitMatch[2]?.toLowerCase()] || 1) : 1;
                const unit = unitMatch ? ({token: 'tokens', character: 'characters'}[unitMatch[3]] || unitMatch[3].replace(/s$/, '')) : 'message';
                for (const [currency, pattern] of [['usd', /\$\s*([\d,.]+(?:e[+-]?\d+)?)/i], ['points', /([\d,.]+)\s*(?:points?|pts?)/i]]) {
                    const match = text.match(pattern);
                    if (match) rates.push({label, currency, amount: match[1].replace(/,/g, ''), quantity, unit, lower_bound: /\+|\bfrom\b/i.test(text)});
                }
            }
        }
        if (rates.some(r => r.currency === 'usd')) return rates;
        const api = model.pricing?.api || {};
        for (const [key, label, unit] of [['prompt', 'Input (text)', 'tokens'], ['completion', 'Output (text)', 'tokens'], ['request', 'Bot message', 'message'], ['image', 'Image Output', 'image']]) {
            if (finite(api[key])) rates.push({label, unit, currency: 'usd', amount: api[key], quantity: 1, source: 'api'});
        }
        return rates;
    }

    function cost(model, preferred = 'points') {
        const all = ratesFor(model).filter(r => finite(r.amount) && finite(r.quantity) && number(r.quantity) > 0);
        if (!all.length) {
            const card = model.pricing?.scraped?.details?.rate_card || '';
            return {amount: null, currency: preferred, label: /multiple calls|respective bots/i.test(card) ? 'Usage based' : 'Not disclosed', basis: /multiple calls|respective bots/i.test(card) ? 'Charged at called bots’ rates' : 'No numeric rate published'};
        }
        const currency = all.some(r => r.currency === preferred) ? preferred : all[0].currency;
        const rates = all.filter(r => r.currency === currency);
        const text = rates.filter(r => r.unit === 'tokens' && !/image|audio|video|citation|reasoning/i.test(r.label));
        const per = r => number(r.amount) / number(r.quantity);
        const minimum = rows => rows.reduce((a, b) => per(a) <= per(b) ? a : b);
        const input = text.filter(r => /input|prompt/i.test(r.label));
        const output = text.filter(r => /output|completion|response/i.test(r.label));
        let used, amount, basis, partial = false;
        const images = rates.filter(r => /image.output|output.*image/i.test(r.label) && r.unit !== 'tokens');
        if (images.length) {
            const image = minimum(images);
            used = [image]; amount = per(image); basis = `per ${image.unit}`;
            if (input.length) { const prompt = minimum(input); used.push(prompt); amount += per(prompt) * 1000; basis += ' + 1k input tokens'; }
            partial = images.length > 1 && new Set(images.map(per)).size > 1;
        } else if (input.length || output.length) {
            used = [input.length && minimum(input), output.length && minimum(output)].filter(Boolean);
            amount = used.reduce((sum, r) => sum + per(r) * 1000, 0);
            partial = !input.length || !output.length;
            basis = partial ? `1k ${input.length ? 'input' : 'output'} tokens only` : '1k input + 1k output tokens';
            const fees = rates.filter(r => /bot.message|base.fee|base.cost|per.message/i.test(r.label) && r.unit !== 'tokens');
            if (fees.length) { const fee = minimum(fees); used.push(fee); amount += per(fee); basis += ' + message fee'; }
        } else {
            // Prefer generation/flat rates over ancillary input and optional tool charges.
            const primary = rates.filter(r => !/input|search|finetun|extra|upscale|cache/i.test(r.label));
            const choices = primary.length ? primary : rates;
            const selected = minimum(choices);
            used = [selected]; amount = per(selected);
            basis = `per ${selected.unit}`;
            if (!['message', 'image', 'video', 'second', 'minute', 'megapixel', 'characters', 'tokens', 'search', 'call'].includes(selected.unit)) basis = `rate: ${selected.label}`;
            partial = choices.length > 1 && new Set(choices.map(r => per(r))).size > 1;
        }
        const from = partial || used.some(r => r.lower_bound);
        const formatted = amount === 0 ? '0' : amount < 0.000001 ? amount.toExponential(3) : amount.toLocaleString('en-US', {maximumSignificantDigits: 7});
        const label = `${from ? 'From ' : ''}${currency === 'usd' ? '$' : ''}${formatted}${currency === 'points' ? ' points' : ''}`;
        return {amount, currency, label, basis, from, source: used.some(r => r.source === 'api') ? 'API' : 'Website'};
    }

    function compare(a, b, direction = 'asc', preferred = 'points') {
        const x = cost(a, preferred), y = cost(b, preferred);
        if (x.amount === null || y.amount === null) return x.amount === y.amount ? a.id.localeCompare(b.id) : x.amount === null ? 1 : -1;
        if (x.amount === 0 || y.amount === 0) {
            if (x.amount !== y.amount) return (x.amount - y.amount) * (direction === 'asc' ? 1 : -1);
        }
        // Unconverted currencies stay in separate groups, with the selected currency first.
        if (x.currency !== y.currency) return x.currency === preferred ? -1 : 1;
        return (x.amount - y.amount) * (direction === 'asc' ? 1 : -1) || a.id.localeCompare(b.id);
    }
    const api = {cost, compare, ratesFor};
    if (typeof module !== 'undefined') module.exports = api;
    root.PoePrices = api;
})(typeof window !== 'undefined' ? window : globalThis);
