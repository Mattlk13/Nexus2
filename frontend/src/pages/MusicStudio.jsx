import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Music, Radio, Play } from 'lucide-react';

export default function MusicStudio() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 to-purple-50 dark:from-slate-900 dark:to-slate-800 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold flex items-center gap-3">
              <Music className="h-10 w-10 text-pink-600" />
              Music Studio
            </h1>
            <p className="text-slate-600 dark:text-slate-400 mt-2">
              AI-powered music creation and composition
            </p>
          </div>
          <Button size="lg">New Composition</Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Radio className="h-5 w-5" />
                AI Composition
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <select className="w-full p-2 border rounded">
                <option>Classical</option>
                <option>Jazz</option>
                <option>Electronic</option>
                <option>Rock</option>
              </select>
              <Button className="w-full">Generate Music</Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Play className="h-5 w-5" />
                Recent Tracks
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-600">No tracks yet. Create your first composition!</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
