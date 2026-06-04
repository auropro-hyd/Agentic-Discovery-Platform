import { useState } from "react";
import { useNavigate } from "react-router-dom";

/** Global search box in the top bar. Submits to /:domain/search?q=… (state in the URL so a search
 *  view is shareable and the back-button works). */
export function SearchBar({ domain }: { domain: string }) {
  const [q, setQ] = useState("");
  const navigate = useNavigate();

  function submit(e: React.FormEvent) {
    e.preventDefault();
    const query = q.trim();
    if (query) navigate(`/${domain}/search?q=${encodeURIComponent(query)}`);
  }

  return (
    <form className="searchbar" onSubmit={submit} role="search">
      <input
        type="search"
        placeholder="Search this suite…"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        aria-label="Search the discovery suite"
      />
    </form>
  );
}
