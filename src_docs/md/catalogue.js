// this_file: src_docs/md/catalogue.js
// Give the standalone table the documentation page's active light/dark palette.
(() => {
    const sync = () => {
        const scheme = document.body.getAttribute('data-md-color-scheme') || 'default';
        document.querySelector('.poe-catalogue')?.contentWindow?.postMessage({poeScheme: scheme}, window.location.origin);
    };
    new MutationObserver(sync).observe(document.body, {attributes: true, attributeFilter: ['data-md-color-scheme']});
    document.addEventListener('load', event => { if (event.target.matches?.('.poe-catalogue')) sync(); }, true);
    window.addEventListener('message', event => { if (event.origin === window.location.origin && event.data?.poeReady) sync(); });
    sync();
})();
