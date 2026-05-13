import { useEffect, useState } from "react";
import CompanyCard from "./components/CompanyCard";

export default function App() {
  const [companies, setCompanies] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/output.json")
      .then((r) => {
        if (!r.ok) throw new Error("output.json not found — run the pipeline first");
        return r.json();
      })
      .then(setCompanies)
      .catch((e) => setError(e.message));
  }, []);

  if (error) return (
    <div className="flex items-center justify-center min-h-screen text-red-600 text-sm">
      {error}
    </div>
  );

  if (!companies) return (
    <div className="flex items-center justify-center min-h-screen text-gray-500 text-sm">
      Loading...
    </div>
  );

  const companyList = Object.values(companies);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-3xl mx-auto px-4 py-10">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">ESG Report Analyzer</h1>
        </header>
        <main className="space-y-8">
          {companyList.map((report) => (
            <CompanyCard key={report.company} report={report} />
          ))}
        </main>
      </div>
    </div>
  );
}