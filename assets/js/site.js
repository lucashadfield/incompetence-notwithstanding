/* site behaviour: search, back-to-top, clipboard, code copy */
(() => {
  const cfg = window.__SITE__ || {};
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));

  /* ── back to top ──────────────────────────────────────────────────── */
  $$('[data-to-top]').forEach((el) =>
    el.addEventListener('click', (e) => {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    })
  );

  /* ── clipboard ────────────────────────────────────────────────────────
     navigator.clipboard is only exposed on secure origins, and the dev server
     runs on plain http over the tailnet — so the async API is unavailable
     there and rejects. Fall back to the execCommand textarea trick. */
  const copyText = async (text) => {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
        return true;
      }
    } catch { /* fall through */ }
    try {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.setAttribute('readonly', '');
      ta.style.cssText = 'position:fixed;top:0;left:-9999px;opacity:0';
      document.body.appendChild(ta);
      ta.select();
      const ok = document.execCommand('copy');
      ta.remove();
      return ok;
    } catch {
      return false;
    }
  };

  /* ── copy-on-click links (the email address) ──────────────────────────
     The href stays a real mailto: so it degrades to the default behaviour
     with JS off, and right-click → copy link address still works. */
  $$('[data-copy]').forEach((el) => {
    const label = el.querySelector('[data-copy-label]') || el;
    const original = label.textContent;
    let timer = null;
    el.addEventListener('click', async (e) => {
      e.preventDefault();
      const ok = await copyText(el.dataset.copy);
      label.textContent = ok ? 'Copied' : el.dataset.copy;
      el.dataset.copied = ok ? '1' : '0';
      clearTimeout(timer);
      timer = setTimeout(() => {
        label.textContent = original;
        delete el.dataset.copied;
      }, 1600);
    });
  });

  /* ── code copy buttons ────────────────────────────────────────────── */
  $$('.prose pre').forEach((pre) => {
    const btn = document.createElement('button');
    btn.className = 'code-copy';
    btn.type = 'button';
    btn.textContent = 'Copy';
    btn.addEventListener('click', async () => {
      const code = pre.querySelector('code');
      const ok = await copyText((code || pre).innerText.replace(/\n$/, ''));
      if (!ok) {
        btn.textContent = 'Failed';
        return;
      }
      btn.textContent = 'Copied';
      btn.dataset.done = '1';
      setTimeout(() => {
        btn.textContent = 'Copy';
        delete btn.dataset.done;
      }, 1600);
    });
    pre.appendChild(btn);
  });

  /* ── search ───────────────────────────────────────────────────────── */
  const overlay = $('[data-search-overlay]');
  const inputs = $$('[data-search-input]');
  if (!inputs.length) return;

  let fuse = null;
  let loading = null;

  const loadScript = (src) =>
    new Promise((resolve, reject) => {
      const s = document.createElement('script');
      s.src = src;
      s.onload = resolve;
      s.onerror = reject;
      document.head.appendChild(s);
    });

  const ensureFuse = () => {
    if (fuse) return Promise.resolve(fuse);
    if (loading) return loading;
    loading = (async () => {
      const [, data] = await Promise.all([
        window.Fuse ? Promise.resolve() : loadScript(cfg.fuseURL),
        fetch(cfg.searchIndex).then((r) => r.json()),
      ]);
      fuse = new window.Fuse(data, Object.assign({ includeMatches: false }, cfg.fuseOpts || {}));
      return fuse;
    })();
    return loading;
  };

  const escapeHTML = (s) =>
    String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  const highlight = (text, query) => {
    const safe = escapeHTML(text);
    const terms = query.split(/\s+/).filter((t) => t.length > 1).map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
    if (!terms.length) return safe;
    return safe.replace(new RegExp(`(${terms.join('|')})`, 'gi'), '<mark>$1</mark>');
  };

  const snippetFor = (item, query) => {
    const body = item.content || '';
    const term = query.split(/\s+/).find((t) => t.length > 1);
    let start = 0;
    if (term) {
      const i = body.toLowerCase().indexOf(term.toLowerCase());
      if (i > 60) start = i - 60;
    }
    const raw = (item.summary && start === 0 ? item.summary : body.slice(start, start + 220)).trim();
    return (start > 0 ? '…' : '') + raw;
  };

  const render = (list, results, query) => {
    if (!query) {
      list.innerHTML = '';
      return;
    }
    if (!results.length) {
      list.innerHTML = `<li class="search-empty"><a href="#" tabindex="-1"><span class="search-result__title">No matches</span><span class="search-result__snippet">Nothing indexed for “${escapeHTML(query)}”.</span></a></li>`;
      return;
    }
    list.innerHTML = results
      .slice(0, 12)
      .map(({ item }) => {
        const meta = [item.date, item.section].filter(Boolean).join(' · ');
        return `<li><a href="${item.permalink}">
          <span class="search-result__title">${highlight(item.title, query)}</span>
          ${meta ? `<span class="search-result__meta u-micro">${escapeHTML(meta)}</span>` : ''}
          <span class="search-result__snippet">${highlight(snippetFor(item, query), query)}</span>
        </a></li>`;
      })
      .join('');
  };

  const wire = (input) => {
    const scope = input.closest('.search-overlay') || input.closest('.search-page') || document;
    const list = scope.querySelector('[data-search-results]');
    const hint = scope.querySelector('[data-search-hint]');
    let ready = false;

    const run = async () => {
      const q = input.value.trim();
      if (!ready) {
        await ensureFuse();
        ready = true;
      }
      const results = q ? fuse.search(q) : [];
      render(list, results, q);
      if (hint) {
        hint.textContent = q
          ? `${results.length} result${results.length === 1 ? '' : 's'}`
          : hint.dataset.idle || (hint.dataset.idle = hint.textContent);
      }
    };

    input.addEventListener('input', run);
    input.addEventListener('focus', ensureFuse, { once: true });

    input.addEventListener('keydown', (e) => {
      const items = $$('a', list);
      if (!items.length) return;
      const current = items.findIndex((a) => a.classList.contains('is-active'));
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        const next = e.key === 'ArrowDown'
          ? Math.min(items.length - 1, current + 1)
          : Math.max(0, current - 1);
        items.forEach((a) => a.classList.remove('is-active'));
        items[next].classList.add('is-active');
        items[next].scrollIntoView({ block: 'nearest' });
      } else if (e.key === 'Enter' && current >= 0) {
        e.preventDefault();
        window.location.href = items[current].getAttribute('href');
      }
    });

    if (input.hasAttribute('autofocus')) run();
  };

  inputs.forEach(wire);

  /* overlay open/close */
  if (overlay) {
    const input = overlay.querySelector('[data-search-input]');
    const open = () => {
      overlay.hidden = false;
      document.body.classList.add('is-locked');
      input.focus();
      input.select();
      ensureFuse();
    };
    const close = () => {
      overlay.hidden = true;
      document.body.classList.remove('is-locked');
    };
    $$('[data-search-open]').forEach((b) => b.addEventListener('click', open));
    $$('[data-search-close]', overlay).forEach((b) => b.addEventListener('click', close));
    document.addEventListener('keydown', (e) => {
      const typing = /^(input|textarea|select)$/i.test(document.activeElement.tagName);
      if (e.key === '/' && !typing && overlay.hidden) {
        e.preventDefault();
        open();
      } else if (e.key === 'Escape' && !overlay.hidden) {
        close();
      } else if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        overlay.hidden ? open() : close();
      }
    });
  }
})();
