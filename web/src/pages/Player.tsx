import { embedSrc, isVideoEmbed } from "../lib/embed";
import type { Item } from "../lib/api";

export function Player({ item, onClose }: { item: Item; onClose: () => void }) {
  const src = embedSrc(item);
  const video = src ? isVideoEmbed(src) : false;

  return (
    <div className="player-scrim" onClick={onClose} role="presentation">
      <div className="player" onClick={(e) => e.stopPropagation()} role="dialog" aria-label={item.title || "player"}>
        <div className="player-top">
          <p>{item.source}{item.title ? ` · ${item.title.slice(0, 72)}` : ""}</p>
          <button type="button" className="ghost" onClick={onClose}>
            close
          </button>
        </div>
        {src && video ? (
          <iframe
            src={src}
            title={item.title || "lewka player"}
            allow="autoplay; fullscreen; encrypted-media"
            allowFullScreen
          />
        ) : src ? (
          <img src={src} alt="" />
        ) : (
          <p className="meta">no embed. <a href={item.url} target="_blank" rel="noreferrer">open source</a></p>
        )}
      </div>
    </div>
  );
}
