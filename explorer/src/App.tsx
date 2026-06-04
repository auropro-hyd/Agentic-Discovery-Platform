import { lazy, Suspense } from "react";
import { HashRouter, Routes, Route, Navigate } from "react-router-dom";
import { DomainLayout } from "./layout/DomainLayout";

const OverviewPage = lazy(() => import("./pages/OverviewPage"));
const CurrentStatePage = lazy(() => import("./pages/CurrentStatePage"));
const PainPointList = lazy(() => import("./pages/PainPointList"));
const PainPointDetail = lazy(() => import("./pages/PainPointDetail"));
const OpportunityPortfolio = lazy(() => import("./pages/OpportunityPortfolio"));
const OpportunityDetail = lazy(() => import("./pages/OpportunityDetail"));
const RoadmapPage = lazy(() => import("./pages/RoadmapPage"));
const EvidencePage = lazy(() => import("./pages/EvidencePage"));
const AssumptionsRegister = lazy(() => import("./pages/AssumptionsRegister"));
const TraceabilityPage = lazy(() => import("./pages/TraceabilityPage"));
const SearchResultsPage = lazy(() => import("./pages/SearchResultsPage"));
const NotFound = lazy(() => import("./pages/NotFound"));

const ConsolePage = lazy(() => import("./console/ConsolePage"));

export function App() {
  return (
    <HashRouter>
      <Suspense fallback={<div className="loading">Loading…</div>}>
        <Routes>
          {/* the Console (operator flow) is the landing page; the report suite lives under /suite */}
          <Route path="/" element={<ConsolePage />} />
          <Route path="/suite/:domain" element={<DomainLayout />}>
            <Route index element={<Navigate to="overview" replace />} />
            <Route path="overview" element={<OverviewPage />} />
            <Route path="current-state" element={<CurrentStatePage />} />
            <Route path="pain-points" element={<PainPointList />} />
            <Route path="pain-points/:ppId" element={<PainPointDetail />} />
            <Route path="opportunities" element={<OpportunityPortfolio />} />
            <Route path="opportunities/:oppId" element={<OpportunityDetail />} />
            <Route path="roadmap" element={<RoadmapPage />} />
            <Route path="evidence" element={<EvidencePage />} />
            <Route path="assumptions" element={<AssumptionsRegister />} />
            <Route path="traceability" element={<TraceabilityPage />} />
            <Route path="search" element={<SearchResultsPage />} />
          </Route>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </HashRouter>
  );
}
