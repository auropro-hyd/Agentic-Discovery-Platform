import { Component, type ReactNode } from "react";
import { LoadError } from "../lib/loadSynthesis";

interface Props {
  children: ReactNode;
}
interface State {
  error: Error | null;
}

/** Catches data-contract (zod) failures and renders a "data contract changed" banner instead of
 *  a blank screen. Anything that throws under the layout lands here. */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  render() {
    const { error } = this.state;
    if (error) {
      const isContract = error instanceof LoadError;
      return (
        <div className="banner error" role="alert">
          <strong>{isContract ? "Data contract changed" : "Something went wrong"}</strong>
          <p style={{ margin: "6px 0 0" }}>{error.message}</p>
          {error instanceof LoadError && error.detail && (
            <p className="small" style={{ margin: "4px 0 0", fontFamily: "var(--mono)" }}>
              {error.detail}
            </p>
          )}
          <p className="small" style={{ margin: "10px 0 0" }}>
            Re-run <code>npm run sync:data</code> after regenerating the suite, then reload.
          </p>
        </div>
      );
    }
    return this.props.children;
  }
}
