"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
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
  const handleExportCSV = () => {
    // Convert to CSV with available fields
    const headers = ["Position", "Title", "Description", "Profile URL", "Avg Position", "Frequency", "Pages Seen"];
    const rows = profiles.map((p) => [
      p.best_position,
      `"${p.title.replace(/"/g, '""')}"`,
      `"${(p.description || "").replace(/"/g, '""')}"`,
      p.profile_url,
      p.avg_position.toFixed(1),
      p.frequency,
      `"${p.pages_seen.join(', ')}"`,
    ]);

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
                <TableHead className="w-16">Rank</TableHead>
                <TableHead>Profile Info</TableHead>
                <TableHead className="w-24">Avg Pos</TableHead>
                <TableHead className="w-20">Seen</TableHead>
                <TableHead className="w-24">Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {profiles.map((profile, index) => (
                <TableRow key={index}>
                  <TableCell className="font-medium">#{profile.best_position}</TableCell>
                  <TableCell>
                    <div className="font-medium text-blue-600">{profile.title}</div>
                    {profile.description && (
                      <div className="text-sm text-gray-600 mt-1 line-clamp-2">
                        {profile.description}
                      </div>
                    )}
                    <div className="text-xs text-gray-500 truncate max-w-md mt-1">
                      {profile.profile_url}
                    </div>
                  </TableCell>
                  <TableCell className="text-center">
                    <span className="text-sm font-medium">{profile.avg_position.toFixed(1)}</span>
                  </TableCell>
                  <TableCell className="text-center">
                    <span className="text-sm">
                      {profile.frequency}x
                    </span>
                    <div className="text-xs text-gray-500">
                      p{profile.pages_seen.join(',')}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => window.open(profile.profile_url, "_blank")}
                    >
                      <ExternalLink className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
