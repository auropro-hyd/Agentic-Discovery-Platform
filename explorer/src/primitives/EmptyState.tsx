/* Shown when a count-variable section has no data (e.g. p2p has 1 data_table where o2c has 5,
 * and some sections are empty). Keeps every renderer count-agnostic. */
export function EmptyState({ children }: { children?: React.ReactNode }) {
  return <div className="empty">{children ?? "Nothing recorded for this section in this domain."}</div>;
}

export function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="section">
      <h2>{title}</h2>
      {children}
    </section>
  );
}
