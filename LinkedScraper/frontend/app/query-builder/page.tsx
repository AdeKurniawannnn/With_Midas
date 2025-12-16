"use client";

import { useState } from "react";
import { SiteFilter } from "@/components/query-builder/SiteFilter";
import { SearchModifiers } from "@/components/query-builder/SearchModifiers";
import { ResultsTable } from "@/components/ResultsTable";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useQueryBuilderStore } from "@/stores/queryBuilderStore";
import { searchLinkedIn, type SearchResponse } from "@/lib/api";
import { Loader2 } from "lucide-react";

/**
 * Query Builder Page
 *
 * Advanced LinkedIn Query Builder dengan backend integration.
 * Generate query manual atau search langsung via backend API.
 *
 * Route: /query-builder
 */
export default function QueryBuilderPage() {
  // Zustand store
  const query = useQueryBuilderStore((state) => state.buildQueryString());
  const modifiers = useQueryBuilderStore((state) => state.modifiers);
  const additionalFilters = useQueryBuilderStore((state) => state.additionalFilters);
  const setLocation = useQueryBuilderStore((state) => state.setLocation);

  // Search state
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null);
  const [searchError, setSearchError] = useState<string | null>(null);

  // Additional options for backend search
  const [country, setCountry] = useState("id");
  const [language, setLanguage] = useState("id");
  const [maxPages, setMaxPages] = useState(2);

  // Toast state
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState("");

  // Copy to clipboard handler
  const handleCopyQuery = async () => {
    if (!query) {
      showToastMessage("Query kosong!");
      return;
    }

    try {
      await navigator.clipboard.writeText(query);
      showToastMessage("✅ Query copied to clipboard!");
    } catch (err) {
      console.error("Failed to copy:", err);
      showToastMessage("❌ Failed to copy query");
    }
  };

  // Open in Google search
  const handleOpenInGoogle = () => {
    if (!query) {
      showToastMessage("Query kosong!");
      return;
    }

    const googleSearchUrl = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
    window.open(googleSearchUrl, "_blank");
  };

  // Search LinkedIn via backend API
  const handleSearch = async () => {
    // Validation
    if (modifiers.mustHaveKeywords.length === 0) {
      showToastMessage("❌ Tambahkan minimal 1 keyword!");
      return;
    }

    setIsSearching(true);
    setSearchError(null);
    setSearchResults(null);

    try {
      // Build role from must-have keywords
      const role = modifiers.mustHaveKeywords.join(" ");

      const result = await searchLinkedIn({
        role,
        location: additionalFilters.location || "",
        country,
        language,
        max_pages: maxPages,
      });

      setSearchResults(result);
      showToastMessage(`✅ Found ${result.total_results} profiles!`);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || "Search failed. Please try again.";
      setSearchError(errorMsg);
      showToastMessage("❌ Search failed!");
      console.error("Search error:", err);
    } finally {
      setIsSearching(false);
    }
  };

  // Show toast notification
  const showToastMessage = (message: string) => {
    setToastMessage(message);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 p-8">
      <div className="w-full max-w-4xl mx-auto space-y-6">
        {/* Page Header */}
        <div>
          <h1 className="text-4xl font-bold">LinkedIn Query Builder</h1>
          <p className="text-lg text-gray-600 mt-2">
            Buat query pencarian LinkedIn yang advanced dengan toggle UI
          </p>
        </div>

        {/* Site Filter Component */}
        <SiteFilter />

        {/* Search Modifiers Component */}
        <SearchModifiers />

        {/* Additional Search Options */}
        <Card>
          <CardHeader>
            <CardTitle>Additional Options</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Location */}
              <div className="space-y-2">
                <Label htmlFor="location">Location (Optional)</Label>
                <Input
                  id="location"
                  placeholder="e.g., Jakarta, Singapore"
                  value={additionalFilters.location}
                  onChange={(e) => setLocation(e.target.value)}
                />
              </div>

              {/* Country */}
              <div className="space-y-2">
                <Label htmlFor="country">Country</Label>
                <Select value={country} onValueChange={setCountry}>
                  <SelectTrigger id="country">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="id">Indonesia</SelectItem>
                    <SelectItem value="us">United States</SelectItem>
                    <SelectItem value="uk">United Kingdom</SelectItem>
                    <SelectItem value="sg">Singapore</SelectItem>
                    <SelectItem value="au">Australia</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Language */}
              <div className="space-y-2">
                <Label htmlFor="language">Language</Label>
                <Select value={language} onValueChange={setLanguage}>
                  <SelectTrigger id="language">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="id">Indonesian</SelectItem>
                    <SelectItem value="en">English</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Max Pages */}
              <div className="space-y-2">
                <Label htmlFor="maxPages">Max Pages (1-25)</Label>
                <Input
                  id="maxPages"
                  type="number"
                  min={1}
                  max={25}
                  value={maxPages}
                  onChange={(e) => setMaxPages(parseInt(e.target.value) || 1)}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Query Preview & Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Preview Query & Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <code className="block p-4 bg-gray-100 rounded font-mono text-sm">
                {query || "(query kosong - pilih filter di atas)"}
              </code>

              {/* Action Buttons */}
              <div className="flex flex-wrap gap-2">
                <Button
                  onClick={handleSearch}
                  variant="default"
                  size="default"
                  disabled={isSearching || modifiers.mustHaveKeywords.length === 0}
                  className="flex-1 min-w-[150px]"
                >
                  {isSearching ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Searching...
                    </>
                  ) : (
                    <>🔍 Search LinkedIn</>
                  )}
                </Button>
                <Button
                  onClick={handleCopyQuery}
                  variant="outline"
                  size="default"
                  disabled={!query}
                  className="flex-1 min-w-[150px]"
                >
                  📋 Copy Query
                </Button>
                <Button
                  onClick={handleOpenInGoogle}
                  variant="secondary"
                  size="default"
                  disabled={!query}
                  className="flex-1 min-w-[150px]"
                >
                  🌐 Open in Google
                </Button>
              </div>

              <p className="text-xs text-gray-500">
                Click "Search LinkedIn" untuk execute query via backend API
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Error Display */}
        {searchError && (
          <Card className="border-red-200 bg-red-50">
            <CardContent className="pt-6">
              <div className="flex items-start gap-2">
                <span className="text-red-600">❌</span>
                <div>
                  <p className="font-medium text-red-900">Search Failed</p>
                  <p className="text-sm text-red-700">{searchError}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Results */}
        {searchResults && (
          <ResultsTable
            profiles={searchResults.profiles}
            metadata={searchResults.metadata}
          />
        )}

        {/* Toast Notification */}
        {showToast && (
          <div className="fixed bottom-4 right-4 bg-gray-900 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-in fade-in slide-in-from-bottom-2">
            {toastMessage}
          </div>
        )}

        {/* Instructions */}
        <Card>
          <CardHeader>
            <CardTitle>Cara Pakai</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-gray-600">
            <ol className="list-decimal list-inside space-y-1">
              <li>Pilih tipe konten LinkedIn yang ingin dicari (Profile, Posts, Jobs, atau Company)</li>
              <li>Tambahkan keywords yang harus ada (Must Have) - minimal 1 keyword</li>
              <li>Optional: Tambahkan keywords exclude dan exact match phrases</li>
              <li>Optional: Atur location, country, language, dan max pages</li>
              <li>Lihat preview query yang ter-generate otomatis</li>
              <li>Pilih action:
                <ul className="list-disc list-inside ml-6 mt-1">
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
    </div>
  );
}
