export const fmt = n => (n == null ? '—' : Number(n).toFixed(2));

export const badge = status =>
  status === 'Pass' || status === 'OK' ? 'badge-pass' : 'badge-fail';

export const initials = name =>
  name ? name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2) : '?';

export const sortAlpha = (arr, key = 'name') =>
  [...arr].sort((a, b) => a[key].localeCompare(b[key]));
