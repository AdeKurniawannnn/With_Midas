"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { ExternalLink, Download } from "lucide-react";
import type { LinkedInProfile } from "@/lib/api";

interface ResultsTableProps {
  profiles: LinkedInProfile[];
  metadata?: {
    country: string;
    language: string;
    pages_fetched: number;
    search_engine: string;
    has_errors: boolean;
  };
}

export function ResultsTable({ profiles, metadata }: ResultsTableProps) {
  // State untuk tracking checkbox
  const [selectedProfiles, setSelectedProfiles] = useState<Set<number>>(new Set());

  const handleToggle = (index: number) => {
    const newSelected = new Set(selectedProfiles);
    if (newSelected.has(index)) {
      newSelected.delete(index);
    } else {
      newSelected.add(index);
    }
    setSelectedProfiles(newSelected);
  };

  const handleExportCSV = () => {
    // Convert to CSV with new format - tambah kolom Selected
    const headers = ["No", "Selected", "Nama", "Pekerjaan", "Description", "Profile URL"];
    const rows = profiles.map((p, index) => {
      const titleParts = p.title.split(' - ');
      const name = titleParts[0].trim();
      const headline = titleParts.slice(1).join(' - ').trim();

      return [
        index + 1,
        selectedProfiles.has(index) ? "Yes" : "No",
        `"${name.replace(/"/g, '""')}"`,
        `"${headline.replace(/"/g, '""')}"`,
        `"${(p.description || "").replace(/"/g, '""')}"`,
        p.profile_url,
      ];
    });

    const csv = [
      headers.join(","),
      ...rows.map((row) => row.join(",")),
    ].join("\n");

    // Download
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `linkedin-profiles-${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (profiles.length === 0) {
    return null;
  }

  return (
    <Card className="w-full max-w-6xl mx-auto mt-8">
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className="text-2xl">Search Results</CardTitle>
          <CardDescription>
            Found {profiles.length} LinkedIn profiles
            {metadata && (
              <>
                {" • "}
                {metadata.pages_fetched} pages fetched via {metadata.search_engine}
              </>
            )}
          </CardDescription>
        </div>
        <Button onClick={handleExportCSV} variant="outline">
          <Download className="mr-2 h-4 w-4" />
          Export CSV
        </Button>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-16">No</TableHead>
                <TableHead className="w-16 text-center">Togle</TableHead>
                <TableHead className="w-48">Nama</TableHead>
                <TableHead className="w-64">Pekerjaan</TableHead>
                <TableHead>Description</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {profiles.map((profile, index) => {
                // Parse name dan headline dari title
                const titleParts = profile.title.split(' - ');
                const name = titleParts[0].trim();
                const headline = titleParts.slice(1).join(' - ').trim();

                return (
                  <TableRow key={index} className="hover:bg-gray-50">
                    <TableCell className="font-medium text-center">
                      {index + 1}
                    </TableCell>
                    <TableCell className="text-center">
                      <Checkbox
                        checked={selectedProfiles.has(index)}
                        onCheckedChange={() => handleToggle(index)}
                      />
                    </TableCell>
                    <TableCell>
                      <a
                        href={profile.profile_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-medium text-blue-600 hover:text-blue-800 hover:underline"
                      >
                        {name}
                      </a>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm text-gray-700">
                        {headline || '-'}
                      </div>
                    </TableCell>
                    <TableCell>
                      {profile.description ? (
                        <div className="text-sm text-gray-600 line-clamp-2">
                          {profile.description}
                        </div>
                      ) : (
                        <span className="text-gray-400 text-sm">-</span>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
