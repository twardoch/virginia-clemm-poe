// this_file: src_docs/md/price_compare.js
// Normalize reference quantities; retain observations and label all assumptions.
(function (root) {
    'use strict';
    const finite = value => value !== null && value !== undefined && value !== '' && Number.isFinite(Number(value)) && Number(value) >= 0;
    const number = value => Number(value);
    let calibration = null;
    const per = r => number(r.amount) / number(r.quantity);
    const key = r => `${r.label}|${r.unit}`;
    const median = values => {
        values.sort((a, b) => a - b);
        const i = Math.floor(values.length / 2);
        return values.length % 2 ? values[i] : (values[i - 1] + values[i]) / 2;
    };

    function exchange(rates, source) {
        const ratios = [];
        for (const p of rates.filter(r => r.currency === 'points' && per(r) > 0)) {
            const matches = rates.filter(r => r.currency === 'usd' && key(r) === key(p) && per(r) > 0 && r.source !== 'api');
            const u = matches.find(r => r.raw && r.raw === p.raw) || matches[0];
            if (u) ratios.push(per(p) / per(u));
        }
        return ratios.length ? {pointsPerDollar: median(ratios), observations: ratios.length, source} : null;
    }

    function configure(models) {
        calibration = exchange(models.flatMap(model => ratesFor(model).map(r => ({...r, label: `${model.id}: ${r.label}`}))), 'catalog matched website rates');
        return calibration;
    }

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
        const unknown = () => {
            const card = model.pricing?.scraped?.details?.rate_card || '';
            return {amount: null, currency: preferred, label: /multiple calls|respective bots/i.test(card) ? 'Usage based' : 'Not disclosed', basis: /multiple calls|respective bots/i.test(card) ? 'Charged at called bots’ rates' : 'No numeric rate published'};
        };
        if (!all.length) return unknown();
        const conversion = exchange(all, 'this bot’s matched website rates') || calibration;
        const currency = preferred;
        const rates = all.filter(r => r.currency === currency).map(r => ({...r}));
        if (preferred === 'points' && conversion) {
            for (const r of all.filter(r => r.currency === 'usd')) {
                if (!rates.some(p => key(p) === key(r))) rates.push({...r, amount: per(r) * number(r.quantity) * conversion.pointsPerDollar, currency: 'points', estimated: true});
            }
        }
        if (!rates.length) return unknown();
        const text = rates.filter(r => r.unit === 'tokens' && !/image|audio|video|citation|reasoning/i.test(r.label));
        const minimum = rows => rows.reduce((a, b) => per(a) <= per(b) ? a : b);
        const input = text.filter(r => /input|prompt/i.test(r.label));
        const output = text.filter(r => /output|completion|response/i.test(r.label));
        let used, amount, basis, partial = false;
        const modalities = model.architecture?.output_modalities || [];
        const card = model.pricing?.scraped?.details?.rate_card || '';
        const images = rates.filter(r => (!/input/i.test(r.label) || /output/i.test(r.label)) && (r.unit === 'image' || r.unit === 'megapixel' || /image.output|output.*image/i.test(r.label)));
        const videoModel = modalities.includes('video') || /video generation|per second of video/i.test(card);
        const videos = rates.filter(r => !/input|fee|^audio/i.test(r.label) && (r.unit === 'video' || /video/i.test(r.label) || (videoModel && ['second','minute'].includes(r.unit))));
        const flat = rates.filter(r => r.unit === 'message' && /total.cost|per.message|message.cost|initial.cost/i.test(r.label));
        let assumed = false;
        if (videos.length && !images.length) {
            const tenSeconds = videos.filter(r => r.unit === 'second' && number(r.quantity) === 10);
            used = [minimum(tenSeconds.length ? tenSeconds : videos)];
            const video = used[0];
            const seconds = video.unit === 'second' ? 1 : video.unit === 'minute' ? 60 : null;
            const duration = `${video.label} ${video.raw || ''}`.match(/\b(\d+(?:\.\d+)?)\s*(?:s\b|seconds?)/i);
            if (seconds) { amount = per(video) * 10 / seconds; basis = 'per 10 seconds video'; }
            else if (video.unit === 'tokens' && /^seedance/i.test(model.id)) {
                amount = per(video) * (1280 * 720 * 24 * 10 / 1024);
                basis = 'per 10 seconds video (assumed 720p, 24 fps)'; assumed = true;
            } else if (video.unit === 'tokens') {
                amount = per(video) * 5792 * 10;
                basis = 'per 10 seconds video (assumed 5,792 tokens/s, 720p)'; assumed = true;
            } else {
                const length = duration ? Number(duration[1]) : 5;
                amount = per(video) * 10 / length;
                basis = `per 10 seconds video (${duration ? 'scaled from' : 'assumed'} ${length}s clip)`; assumed = true;
            }
            partial = videos.length > 1;
        } else if (images.length) {
            const square = images.filter(r => /1024\s*[x×]\s*1024/i.test(r.label));
            const firstMP = images.find(r => /first megapixel/i.test(r.raw || ''));
            const image = firstMP || minimum(square.length ? square : images);
            used = [image]; amount = per(image); basis = image.unit === 'message' ? 'per message (image output)' : 'per image';
            if (image.unit === 'megapixel') {
                const additional = images.find(r => /additional megapixel/i.test(r.raw || ''));
                if (firstMP && additional) {
                    amount += per(additional) * 0.048576; used.push(additional);
                } else amount *= /round.*up/i.test(image.raw || '') ? 2 : 1.048576;
                basis = 'per 1024×1024 image (1.048576 MP' + (/round.*up/i.test(image.raw || '') ? ', billed as 2 MP)' : ')'); assumed = true;
            } else if (image.unit === 'tokens') {
                const tokens = /gpt|openai/i.test(model.id) ? 1056 : /nano-banana-2|gemini-3.1/i.test(model.id) ? 1120 : 1290;
                amount *= tokens; basis = `per 1024×1024 image (assumed ${tokens} output tokens)`; assumed = true;
            } else if (square.length) basis = 'per 1024×1024 image';
            else if (!['image','message'].includes(image.unit)) { basis = 'per 1024×1024 image (assumed one generation)'; assumed = true; }
            partial = images.length > 1 && new Set(images.map(per)).size > 1;
        } else if (flat.length) {
            used = [minimum(flat)]; amount = per(used[0]); basis = 'per message';
        } else if (modalities.includes('image') && rates.every(r => /input/i.test(r.label) && !/output/i.test(r.label))) {
            return unknown();
        } else if (input.length || output.length) {
            used = [input.length && minimum(input), output.length && minimum(output)].filter(Boolean);
            amount = used.reduce((sum, r) => sum + per(r) * (input.length && output.length ? 500 : 1000), 0);
            partial = !input.length || !output.length;
            basis = partial ? `1,000 ${input.length ? 'input' : 'output'} tokens only` : '1,000 tokens (500 input + 500 output)';
            const fees = rates.filter(r => /bot.message|base.fee|base.cost|per.message/i.test(r.label) && r.unit !== 'tokens');
            if (fees.length) { const fee = minimum(fees); used.push(fee); amount += per(fee); basis += ' + message fee'; }
        } else {
            // Prefer generation/flat rates over ancillary input and optional tool charges.
            const primary = rates.filter(r => !/input|search|finetun|extra|upscale|cache/i.test(r.label));
            const choices = primary.length ? primary : rates;
            const selected = minimum(choices);
            used = [selected]; amount = per(selected);
            basis = `per ${selected.unit}`;
            if (selected.unit === 'characters') { amount *= 4000; basis = 'per 4,000 characters'; }
            if (!['message', 'image', 'video', 'second', 'minute', 'megapixel', 'characters', 'tokens', 'search', 'call'].includes(selected.unit)) basis = `rate: ${selected.label}`;
            partial = choices.length > 1 && new Set(choices.map(r => per(r))).size > 1;
        }
        const from = partial || used.some(r => r.lower_bound);
        const estimated = assumed || used.some(r => r.estimated);
        const formatted = amount === 0 ? '0' : amount < 0.000001 ? amount.toExponential(3) : amount.toLocaleString('en-US', {maximumSignificantDigits: 7});
        const label = `${from ? 'From ' : ''}${estimated ? '≈ ' : ''}${currency === 'usd' ? '$' : ''}${formatted}${currency === 'points' ? ' points' : ''}`;
        return {amount, currency, label, basis, from, estimated, conversion: used.some(r => r.estimated) ? conversion : null, source: used.some(r => r.source === 'api') ? 'API' : 'Website'};
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

    function tier(model) {
        const value = cost(model);
        if (value.amount === null) return ratesFor(model).length ? 8 : 9;
        const card = model.pricing?.scraped?.details?.rate_card || '';
        if (!/per message|per image|per 1024|per 10 seconds video|per 4,000 characters|1,000 .*tokens/.test(value.basis)
            || /plus the rates|multiple calls|respective bots/i.test(card)) return 8;
        if (value.amount === 0) return cost(model, 'usd').amount === 0 && !value.estimated && !value.from ? 0 : 8;
        const index = [9, 29, 99, 299, 999, 2999].findIndex(limit => value.amount <= limit);
        return index === -1 ? 7 : index + 1;
    }
    const api = {cost, compare, ratesFor, configure, tier};
    if (typeof module !== 'undefined') module.exports = api;
    root.PoePrices = api;
})(typeof window !== 'undefined' ? window : globalThis);
