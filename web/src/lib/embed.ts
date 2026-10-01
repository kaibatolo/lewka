import type { Item } from "./api";

export function embedSrc(item: Item): string | null {
  const url = item.url || "";
  const id = (item.id || "").split(":").slice(1).join(":");

  const eporner = url.match(/eporner\.com\/video-([A-Za-z0-9]+)/i) || (item.source === "eporner" && id ? ["", id] : null);
  if (eporner) return `https://www.eporner.com/embed/${eporner[1]}/`;

  const ph = url.match(/pornhub\.com\/view_video\.php\?viewkey=([A-Za-z0-9]+)/i);
  if (ph) return `https://www.pornhub.com/embed/${ph[1]}`;

  const xv = url.match(/xvideos\.com\/video\.?([0-9]+)/i);
  if (xv) return `https://www.xvideos.com/embedframe/${xv[1]}`;

  const rg = url.match(/redgifs\.com\/(?:watch|ifr)\/([A-Za-z0-9]+)/i);
  if (rg) return `https://www.redgifs.com/ifr/${rg[1]}`;

  if ((item.kind === "image" || /\.(jpe?g|png|webp|gif)(\?|$)/i.test(url)) && url.startsWith("http")) {
    return url;
  }
  return null;
}

export function isVideoEmbed(src: string) {
  return /eporner|pornhub|xvideos|redgifs/.test(src);
}
