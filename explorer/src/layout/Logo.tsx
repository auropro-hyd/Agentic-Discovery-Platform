/** The AuroPro brand mark — inline SVG (offline-safe), navy/blue twin-triangle device.
 *  Identical geometry to the print suite's _LOGO so the SPA and PDF share one mark. */
export function Logo({ size = 26 }: { size?: number }) {
  return (
    <svg viewBox="0 0 32 32" width={size} height={size} xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <path d="M16 3 L27 26 H19 L16 18 L13 26 H5 Z" fill="#ffffff" />
      <path d="M16 3 L21 13 L16 13 Z" fill="#2563eb" />
    </svg>
  );
}
