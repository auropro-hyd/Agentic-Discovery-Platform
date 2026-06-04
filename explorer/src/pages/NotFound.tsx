import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="panel" style={{ textAlign: "center", maxWidth: "42ch", margin: "10vh auto" }}>
      <header className="page-head">
        <div className="eyebrow">Error 404</div>
        <h1>Page not found</h1>
        <p className="lede" style={{ margin: "0 auto" }}>
          The page you are looking for does not exist or may have moved.
        </p>
      </header>
      <Link to="/">Go to the discovery overview</Link>
    </div>
  );
}
