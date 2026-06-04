import { DomainSwitcher } from "./DomainSwitcher";
import { SearchBar } from "../search/SearchBar";

export function TopBar({ domain }: { domain: string }) {
  return (
    <header className="topbar">
      <DomainSwitcher current={domain} />
      <div className="spacer" />
      <SearchBar domain={domain} />
    </header>
  );
}
