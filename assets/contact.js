/* Contact page — copy the PGP public key to the clipboard.
   External (not inline) so the site can run a strict script-src 'self' CSP. */
(function () {
  var btn = document.querySelector('.pgp-copy');
  if (!btn) return;
  btn.addEventListener('click', function () {
    var pre = document.getElementById(btn.getAttribute('data-copy-target'));
    var note = document.querySelector('.pgp-copied');
    if (!pre) return;
    var text = pre.textContent;
    function ok() { if (note) { note.textContent = 'Copied ✓'; setTimeout(function () { note.textContent = ''; }, 2200); } }
    function legacy(s) {
      var t = document.createElement('textarea');
      t.value = s; t.setAttribute('readonly', '');
      t.style.position = 'absolute'; t.style.left = '-9999px';
      document.body.appendChild(t); t.select();
      try { document.execCommand('copy'); } catch (e) {}
      document.body.removeChild(t);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(ok, function () { legacy(text); ok(); });
    } else { legacy(text); ok(); }
  });
})();
