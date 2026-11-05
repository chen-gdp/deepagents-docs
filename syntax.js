import './vendor/prism.js';

const prism = globalThis.Prism;
const escapeHtml = text => text.replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
}[char]));

const fileLanguages = {
  py: 'python', json: 'json', ipynb: 'json', sh: 'bash',
  toml: 'toml', yaml: 'yaml', yml: 'yaml', sql: 'sql',
  js: 'javascript', ts: 'typescript', tsx: 'tsx', jsx: 'jsx',
  css: 'css', html: 'markup', svg: 'markup', xml: 'markup',
  md: 'markdown', ini: 'ini',
};

export function languageForFile(path) {
  const name = path.split('/').at(-1);
  if (name === 'Makefile') return 'makefile';
  if (name === 'Dockerfile') return 'docker';
  return fileLanguages[name.split('.').at(-1)] || 'plain';
}

export function highlightCode(text, language) {
  return highlightSourceLines(text, language).join('\n');
}

export function highlightSourceLines(text, language) {
  const grammar = prism.languages[language];
  if (!grammar) return text.split('\n').map(escapeHtml);

  // Tokenize the whole file once so a page starting inside a docstring keeps
  // Python's multiline context. Each returned line has balanced HTML spans.
  const lines = [''];
  function append(tokens, ancestors = []) {
    if (Array.isArray(tokens)) {
      tokens.forEach(token => append(token, ancestors));
      return;
    }
    if (typeof tokens !== 'string') {
      const aliases = tokens.alias ? [tokens.alias].flat() : [];
      append(tokens.content, [...ancestors, [tokens.type, ...aliases].map(escapeHtml).join(' ')]);
      return;
    }
    tokens.split('\n').forEach((part, index) => {
      if (index) lines.push('');
      if (!part) return;
      const html = ancestors.reduceRight(
        (content, classes) => `<span class="token ${classes}">${content}</span>`,
        escapeHtml(part),
      );
      lines[lines.length - 1] += html;
    });
  }
  append(prism.tokenize(text, grammar));
  return lines;
}
