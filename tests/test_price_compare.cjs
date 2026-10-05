// this_file: tests/test_price_compare.cjs
const {test} = require('node:test');
const assert = require('node:assert/strict');
const {cost, compare} = require('../src_docs/md/price_compare.js');
const bot = (id, rates) => ({id, pricing: {scraped: {details: {rates}}}});
const rate = (label, amount, unit = 'message', quantity = 1, currency = 'points') => ({label, amount, unit, quantity, currency});

test('zero, decimals, tiny dollar values, and missing prices sort numerically', () => {
    const rows = [bot('missing', []), bot('two', [rate('Total cost', '2')]), bot('zero', [rate('Total cost', '0')]), bot('fraction', [rate('Total cost', '0.02')])];
    assert.deepEqual(rows.sort(compare).map(r => r.id), ['zero', 'fraction', 'two', 'missing']);
    assert.equal(rows.sort((a,b) => compare(a,b,'desc')).at(-1).id, 'missing');
    assert.ok(Math.abs(cost({id:'tiny',pricing:{api:{prompt:'1e-9',completion:'2e-9'}}}).amount - 0.000003) < 1e-18);
});
test('image quality tables include generation and text input instead of just prompt tokens', () => {
    const value = cost(bot('image', [rate('Input (text)',151,'tokens',1000),rate('Image Output (low)',328,'image'),rate('Image Output (high)',4000,'image')]));
    assert.equal(value.amount,479);
    assert.equal(value.from,true);
    assert.match(value.basis,/image/);
});
test('input, output and mandatory message fee are added with their own denominators', () => {
    const value = cost(bot('text', [rate('Input', 2,'tokens',1e6,'usd'),rate('Output',10,'tokens',1e6,'usd'),rate('Bot message',0.05,'message',1,'usd')]),'usd');
    assert.equal(value.amount, 0.062);
    assert.match(value.basis, /message fee/);
});
test('image rates, partial token prices and currencies remain explicit', () => {
    assert.equal(cost(bot('image',[rate('Image Output',850,'megapixel')])).basis,'per megapixel');
    assert.match(cost(bot('partial',[rate('Input',1,'tokens',1000)])).label,/^From /);
    const usd = bot('usd',[rate('Total cost',0.0001,'message',1,'usd')]);
    const points = bot('points',[rate('Total cost',2)]);
    assert.ok(compare(points,usd) < 0);
});
test('legacy flat zero and zero API rates stay known', () => {
    assert.equal(cost({id:'zero',pricing:{scraped:{details:{total_cost:'0 points/message'}}}}).amount,0);
    assert.equal(cost({id:'api',pricing:{api:{prompt:0,completion:0}}}).amount,0);
});
