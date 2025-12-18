"use client";

import { useState } from "react";
import { SearchForm } from "@/components/SearchForm";
import { CompanySearchForm } from "@/components/CompanySearchForm";
import { ResultsTable } from "@/components/ResultsTable";
import { ProgressBar } from "@/components/ProgressBar";
import { SiteFilter } from "@/components/query-builder/SiteFilter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { searchLinkedIn, type SearchResponse } from "@/lib/api";
import { useQueryBuilderStore } from "@/stores/queryBuilderStore";

/**
 * LinkedIn Query Builder - Advanced Search
 *
 * Halaman pencarian LinkedIn dengan multiple options (Profile, Posts, Jobs, Company).
 * Route: /query-builder
 */
export default function QueryBuilderPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Get siteFilter from Zustand store
  const siteFilter = useQueryBuilderStore((state) => state.siteFilter);

  const handleSearch = async (params: {
    role: string;
    location: string;
    country: string;
    language: string;
    max_pages: number;
  }) => {
    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const data = await searchLinkedIn(params);
      setResults(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to search. Please try again.");
      console.error("Search error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 py-12 px-4">
      {/* Header */}
      <header className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          LinkedIn Query Builder
        </h1>
        <p className="text-lg text-gray-600">
          Buat query pencarian LinkedIn yang advanced dengan toggle UI
        </p>
      </header>

      {/* Cara Pakai Box */}
      <div className="w-full max-w-4xl mx-auto mb-8">
        <Card>
          <CardHeader>
            <CardTitle>Cara Pakai</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-gray-700">
            <ol className="list-decimal list-inside space-y-2">
              <li>Pilih tipe konten LinkedIn yang ingin dicari (Profile, Posts, Jobs, atau Company)</li>
              <li>Tambahkan keywords yang harus ada (Must Have) - minimal 1 keyword</li>
              <li>Optional: Tambahkan keywords exclude dan exact match phrases</li>
              <li>Optional: Atur location, country, language, dan max pages</li>
              <li>Lihat preview query yang ter-generate otomatis</li>
              <li>Pilih action:
                <ul className="list-disc list-inside ml-6 mt-2 space-y-1">
                  <li><strong>Search LinkedIn</strong> - Execute query via backend API (dapat hasil scraping)</li>
                  <li><strong>Copy Query</strong> - Copy query string ke clipboard</li>
                  <li><strong>Open in Google</strong> - Buka query di Google search</li>
                </ul>
              </li>
              <li>Jika search via API, results akan muncul di bawah dengan option export CSV</li>
            </ol>
          </CardContent>
        </Card>
      </div>

      {/* Site Filter - Always Visible */}
      <div className="w-full max-w-4xl mx-auto mb-8">
        <SiteFilter />
      </div>

      {/* Conditional Content Based on Site Filter */}

      {/* Profile Search */}
      {siteFilter === 'profile' && (
        <>
          {/* Search Form - Same as homepage */}
          <SearchForm onSearch={handleSearch} isLoading={isLoading} />

          {/* Progress Bar */}
          <ProgressBar isLoading={isLoading} />

          {/* Error Message */}
          {error && (
            <div className="w-full max-w-2xl mx-auto mt-8">
              <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
                <p className="font-medium">Error</p>
                <p className="text-sm">{error}</p>
              </div>
            </div>
          )}

          {/* Results Table */}
          {results && (
            <ResultsTable
              profiles={results.profiles}
              metadata={results.metadata}
            />
          )}
        </>
      )}

      {/* Company Search */}
      {siteFilter === 'company' && (
        <>
          {/* Company Search Form - Custom for company search */}
          <CompanySearchForm onSearch={handleSearch} isLoading={isLoading} />

          {/* Progress Bar */}
          <ProgressBar isLoading={isLoading} />

          {/* Error Message */}
          {error && (
            <div className="w-full max-w-2xl mx-auto mt-8">
              <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
                <p className="font-medium">Error</p>
                <p className="text-sm">{error}</p>
              </div>
            </div>
          )}

          {/* Results Table */}
          {results && (
            <ResultsTable
              profiles={results.profiles}
              metadata={results.metadata}
            />
          )}
        </>
      )}

      {/* Placeholder for other filters (Semua, Posts, Jobs) */}
      {siteFilter !== 'profile' && siteFilter !== 'company' && (
        <div className="w-full max-w-4xl mx-auto mt-8">
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-gray-600 text-lg font-medium mb-2">
                🚧 Coming Soon
              </p>
              <p className="text-gray-500 text-sm">
                Fitur untuk <strong>{siteFilter === 'all' ? 'Semua' : siteFilter === 'posts' ? 'Postingan' : 'Lowongan'}</strong> sedang dalam pengembangan
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Footer */}
      <footer className="text-center mt-16 text-sm text-gray-500">
        <p>Powered by Bright Data API • Built with Next.js & FastAPI</p>
      </footer>
    </div>
  );
}
