// this_file: tests/test_price_compare.cjs
const {test} = require('node:test');
const assert = require('node:assert/strict');
const {cost, compare, configure, tier} = require('../src_docs/md/price_compare.js');
configure(require('../src_docs/md/data/poe_bots.json').data);
const bot = (id, rates) => ({id, pricing: {scraped: {details: {rates}}}});
const rate = (label, amount, unit = 'message', quantity = 1, currency = 'points') => ({label, amount, unit, quantity, currency});

test('zero, decimals, tiny dollar values, and missing prices sort numerically', () => {
    const rows = [bot('missing', []), bot('two', [rate('Total cost', '2')]), bot('zero', [rate('Total cost', '0')]), bot('fraction', [rate('Total cost', '0.02')])];
    assert.deepEqual(rows.sort(compare).map(r => r.id), ['zero', 'fraction', 'two', 'missing']);
    assert.equal(rows.sort((a,b) => compare(a,b,'desc')).at(-1).id, 'missing');
    assert.ok(Math.abs(cost({id:'tiny',pricing:{api:{prompt:'1e-9',completion:'2e-9'}}},'usd').amount - 0.0000015) < 1e-18);
});
test('image quality tables include generation and text input instead of just prompt tokens', () => {
    const value = cost(bot('image', [rate('Input (text)',151,'tokens',1000),rate('Image Output (low)',328,'image'),rate('Image Output (high)',4000,'image')]));
    assert.equal(value.amount,328);
    assert.equal(value.from,true);
    assert.match(value.basis,/image/);
});
test('input, output and mandatory message fee are added with their own denominators', () => {
    const value = cost(bot('text', [rate('Input', 2,'tokens',1e6,'usd'),rate('Output',10,'tokens',1e6,'usd'),rate('Bot message',0.05,'message',1,'usd')]),'usd');
    assert.equal(value.amount, 0.056);
    assert.match(value.basis, /message fee/);
});
test('image rates, partial token prices and currencies remain explicit', () => {
    assert.equal(cost(bot('image',[rate('Image Output',850,'megapixel')])).amount,850 * 1.048576);
    assert.match(cost(bot('partial',[rate('Input',1,'tokens',1000)])).label,/^From /);
    const usd = bot('usd',[rate('Total cost',0.0001,'message',1,'usd')]);
    const points = bot('points',[rate('Total cost',2)]);
    assert.ok(compare(points,usd) < 0);
});
test('legacy flat zero and zero API rates stay known', () => {
    assert.equal(cost({id:'zero',pricing:{scraped:{details:{total_cost:'0 points/message'}}}}).amount,0);
    assert.equal(cost({id:'api',pricing:{api:{prompt:0,completion:0}}}).amount,0);
});

test('flat message points take precedence over token and USD rates', () => {
    const value = cost(bot('text',[rate('Input',10,'tokens',1000),rate('Output',20,'tokens',1000),rate('Total cost',7)]));
    assert.equal(value.amount,7);
    assert.equal(value.basis,'per message');
});
test('text comparison uses 1000 total tokens split evenly with fee', () => {
    const value = cost(bot('text',[rate('Input',10,'tokens',1000),rate('Output',30,'tokens',1000),rate('Bot message',5)]));
    assert.equal(value.amount,25);
    assert.match(value.basis,/1,000 tokens/);
});
test('character and time denominators scale to the requested quantities', () => {
    assert.equal(cost(bot('tts',[rate('Output',3,'characters',1000)])).amount,12);
    assert.equal(cost(bot('video',[rate('Video Output',12,'second')])).amount,120);
    assert.equal(cost(bot('video',[rate('Video Output',600,'minute')])).amount,100);
});
test('USD conversion uses local matched rate pairs before the catalog median', () => {
    const value = cost(bot('mixed',[rate('Input',10,'tokens',1000),rate('Input',0.001,'tokens',1000,'usd'),rate('Output',0.003,'tokens',1000,'usd')]));
    assert.equal(value.amount,20);
    assert.equal(value.currency,'points');
    assert.equal(value.estimated,true);
    assert.equal(value.conversion.pointsPerDollar,10000);
});
test('catalog conversion ignores zeros and mismatched units', () => {
    const result = configure([bot('pair',[rate('Output',300),rate('Output',0.01,'message',1,'usd'),rate('Zero',0),rate('Zero',0,'message',1,'usd')])]);
    assert.equal(result.pointsPerDollar,30000);
    const value = cost(bot('dollars',[rate('Output',0.02,'image',1,'usd')]));
    assert.equal(value.amount,600);
    assert.match(value.label,/≈/);
    configure(require('../src_docs/md/data/poe_bots.json').data);
});
test('1024 square image prefers matching size and excludes prompt tokens', () => {
    const value = cost(bot('image',[rate('Image Output (low; 512x512)',5,'image'),rate('Image Output (low; 1024x1024)',15,'image'),rate('Input',10,'tokens',1000)]));
    assert.equal(value.amount,15);
    assert.match(value.basis,/1024/);
});
test('megapixel billing honors explicit rounding', () => {
    const r = rate('Image Output',34,'megapixel');
    r.raw = 'rounded up to nearest integer';
    assert.equal(cost(bot('upscale',[r])).amount,68);
});
test('video flat rate estimates ten seconds with duration or an explicit assumption', () => {
    assert.equal(cost(bot('video',[rate('Video Output (5 seconds)',100,'video')])).amount,200);
    const value = cost(bot('video',[rate('Video Output',100,'video')]));
    assert.equal(value.amount,200);
    assert.match(value.basis,/assumed 5s/);
    assert.equal(value.estimated,true);
});
test('image input costs are not presented as generation costs', () => {
    const model = bot('unknown',[rate('Input (image)',10,'tokens',1000)]);
    model.architecture = {output_modalities:['image']};
    assert.equal(cost(model).amount,null);
});
test('tiers use every requested boundary and require explicit zero in both currencies', () => {
    for (const [amount, expected] of [[1,1],[9,1],[9.01,2],[29,2],[29.01,3],[99,3],[100,4],[299,4],[300,5],[999,5],[1000,6],[2999,6],[3000,7]]) {
        assert.equal(tier(bot('priced',[rate('Total cost',amount)])),expected,`Tier boundary for ${amount}`);
    }
    assert.equal(tier(bot('free',[rate('Total cost',0),rate('Total cost',0,'message',1,'usd')])),0);
    assert.equal(tier(bot('zero-unconfirmed',[rate('Total cost',0)])),8);
    assert.equal(tier(bot('search',[rate('Search',10,'search')])),8);
    assert.equal(tier(bot('unknown',[])),9);
});
test('exchange pairs support different token denominators', () => {
    const value = configure([bot('paired',[rate('Input',30,'tokens',1000),rate('Input',1,'tokens',1e6,'usd')])]);
    assert.equal(value.pointsPerDollar,30000);
    configure(require('../src_docs/md/data/poe_bots.json').data);
});
test('video prices with and without audio both normalize to ten seconds', () => {
    const value = cost(bot('video',[rate('Video Output without audio',56,'second'),rate('Video Output with audio',84,'second')]));
    assert.equal(value.amount,560);
    assert.match(value.basis,/10 seconds video/);
});
test('first and additional megapixel rates include the mandatory first megapixel', () => {
    const first = {...rate('Image Input/Output',2334,'megapixel'),raw:'First Megapixel'};
    const next = {...rate('Image Input/Output',1000,'megapixel'),raw:'Additional Megapixel'};
    assert.ok(Math.abs(cost(bot('image',[first,next])).amount - 2382.576) < 1e-8);
});
